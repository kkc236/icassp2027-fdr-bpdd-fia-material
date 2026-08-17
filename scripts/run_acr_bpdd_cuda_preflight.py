"""Run and freeze the mandatory RTX4090 ACR-BPDD Formal100 preflight."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

import torch
from torch import Tensor


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.train_rtdetr_fdr import current_source_identity  # noqa: E402
from src.acr_bpdd_protocol import (  # noqa: E402
    ACR_BPDD_PROTOCOL,
    ACR_BPDD_PROTOCOL_SHA256,
    build_run_identity,
    canonical_json_bytes,
    public_state_sha256,
    validate_manifest,
)
from src.fdr_protocol import load_fdr_initial_state, validate_fdr_initial_state  # noqa: E402
from src.lpr_protocol import dataset_signature  # noqa: E402
from src.rtdetr_fdr_acr_bpdd import (  # noqa: E402
    ACR_BPDD_MODEL_CFG,
    FDRACRBPDDDetectionModel,
    FDRACRBPDDTrainer,
)


REQUIRED_CHECKS = (
    "real_visdrone_batch8",
    "loss_bpdd_positive",
    "active_edge_ratio_positive",
    "reliability_mass_positive",
    "common_bpdd_grads_none",
    "bbox_bpdd_grad_nonzero",
    "bbox_bpdd_grads_finite",
    "total_grads_finite",
    "replay_within_dtype_tolerance",
    "normal_queries_300",
    "dn_nonempty",
    "forward",
    "backward",
    "musgd_step",
    "checkpoint_saved",
    "strict_state_reload",
    "eval_output_exact",
    "optimizer_scaler_reload",
    "resume_step",
)

BPDD_LIVENESS_MAX_STEPS = 16


@dataclass(frozen=True)
class PreflightContext:
    protocol_manifest: Path
    initial_state: Path
    dataset_root: Path
    output: Path
    repository_root: Path = ROOT


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _read_manifest(path: Path) -> dict[str, Any]:
    unresolved = Path(path)
    if unresolved.is_symlink():
        raise FileNotFoundError(f"unsafe or missing ACR-BPDD manifest: {unresolved}")
    path = unresolved.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"unsafe or missing ACR-BPDD manifest: {path}")
    payload = json.loads(path.read_text("utf-8"))
    validate_manifest(payload)
    return payload


def _dataset_authority(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"VisDrone dataset root not found: {root}")
    signature = dataset_signature(root)
    train = tuple((root / "images" / "train").glob("*.jpg"))
    val = tuple((root / "images" / "val").glob("*.jpg"))
    expected = ACR_BPDD_PROTOCOL["dataset"]
    if str(signature.get("sha256", "")).upper() != str(expected["sha256"]).upper():
        raise RuntimeError(
            "VisDrone SHA256 mismatch: "
            f"expected={expected['sha256']}, actual={signature.get('sha256')}"
        )
    if len(train) != int(expected["train_images"]) or len(val) != int(
        expected["val_images"]
    ):
        raise RuntimeError(
            f"VisDrone count mismatch: train={len(train)}, val={len(val)}"
        )
    return dict(expected)


def summarize_gradients(
    gradients: Sequence[Tensor | None],
) -> dict[str, int | bool]:
    present = [gradient for gradient in gradients if gradient is not None]
    finite = all(bool(torch.isfinite(gradient).all().item()) for gradient in present)
    nonzero = sum(bool(torch.count_nonzero(gradient).item()) for gradient in present)
    return {
        "gradient_tensors": len(present),
        "none_tensors": len(gradients) - len(present),
        "finite": finite,
        "nonzero_tensors": nonzero,
    }


def _bpdd_step_is_live(
    step: Mapping[str, Any], statistics: Mapping[str, Tensor]
) -> bool:
    """Require an actual finite BPDD update path, not only non-zero metadata."""

    bpdd = step.get("bpdd")
    private = step.get("private", {})
    common = step.get("common", {})
    active = statistics.get("active_edge_ratio")
    mass = statistics.get("reliability_mass")
    if not all(isinstance(value, Tensor) for value in (bpdd, active, mass)):
        return False
    return bool(
        torch.isfinite(bpdd).all().item()
        and float(bpdd.detach().float().cpu()) > 0
        and torch.isfinite(active).all().item()
        and float(active.detach().float().cpu()) > 0
        and torch.isfinite(mass).all().item()
        and float(mass.detach().float().cpu()) > 0
        and bool(private.get("finite", False))
        and int(private.get("nonzero_tensors", 0)) > 0
        and int(common.get("gradient_tensors", -1)) == 0
    )


def _move_batch(batch: Mapping[str, Any], device: torch.device) -> dict[str, Any]:
    moved = {
        name: value.to(device, non_blocking=True) if isinstance(value, Tensor) else value
        for name, value in batch.items()
    }
    moved["img"] = moved["img"].float().div_(255)
    return moved


def _loader(context: PreflightContext):
    from src.fdr_runtime_preflight import _build_loader

    proxy = type(
        "Context",
        (),
        {
            "dataset_root": Path(context.dataset_root).resolve(),
            "report_root": Path(context.output).resolve().parent,
        },
    )()
    loader, _signature = _build_loader(proxy, augment=True)
    return loader


def _formal_musgd(model: torch.nn.Module) -> torch.optim.Optimizer:
    """Build MuSGD through the exact Formal100 trainer method."""

    trainer = object.__new__(FDRACRBPDDTrainer)
    return FDRACRBPDDTrainer.build_optimizer(
        trainer,
        model,
        name="MuSGD",
        lr=0.01,
        momentum=0.937,
        decay=0.0005,
        iterations=100 * 809,
    )


def _torch_state_sha256(value: Any) -> str:
    buffer = io.BytesIO()
    torch.save(value, buffer)
    return hashlib.sha256(buffer.getvalue()).hexdigest().upper()


def _load_model(context: PreflightContext, device: torch.device):
    artifact = torch.load(
        Path(context.initial_state).resolve(), map_location="cpu", weights_only=False
    )
    validate_fdr_initial_state(artifact)
    model = FDRACRBPDDDetectionModel(
        ACR_BPDD_MODEL_CFG,
        ch=3,
        nc=10,
        verbose=False,
        private_seed=10_000,
    ).to(device)
    load_fdr_initial_state(model, artifact, variant="fdr")
    return model


def _nested_max_abs(left: Any, right: Any) -> float:
    if isinstance(left, Tensor) and isinstance(right, Tensor):
        if left.shape != right.shape:
            return math.inf
        return float((left.detach().float() - right.detach().float()).abs().max().cpu())
    if isinstance(left, (tuple, list)) and isinstance(right, type(left)):
        if len(left) != len(right):
            return math.inf
        return max((_nested_max_abs(a, b) for a, b in zip(left, right)), default=0.0)
    if left is None and right is None:
        return 0.0
    return math.inf


def _runtime_environment() -> dict[str, str]:
    import torchvision
    import ultralytics

    driver = subprocess.run(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip().splitlines()[0]
    return {
        "model": "Ultralytics RT-DETR-L",
        "ultralytics": ultralytics.__version__,
        "gpu": torch.cuda.get_device_name(0),
        "driver": driver,
        "python": platform.python_version(),
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "cuda": str(torch.version.cuda),
    }


def validate_launch_environment(
    report: Mapping[str, Any],
    *,
    environment_loader: Callable[[], dict[str, str]] = _runtime_environment,
) -> dict[str, str]:
    """Recheck the environment of the process that will launch Formal100."""

    actual = environment_loader()
    expected = dict(ACR_BPDD_PROTOCOL["environment"])
    if actual != expected or report.get("environment") != expected:
        raise ValueError(
            f"current launch environment differs from authority: expected={expected}, actual={actual}"
        )
    if actual.get("gpu") != "NVIDIA GeForce RTX 4090":
        raise ValueError("current launch environment requires RTX 4090")
    return actual


def _preflight_checkpoint_path(context: PreflightContext) -> Path:
    return Path(context.output).resolve().with_suffix(".pt")


def _optimizer_evidence_path(context: PreflightContext) -> Path:
    return Path(context.output).resolve().with_suffix(".optimizer-evidence.jsonl")


def _validate_artifact_paths(context: PreflightContext) -> Path:
    output = Path(context.output).resolve()
    checkpoint = _preflight_checkpoint_path(context)
    optimizer_evidence = _optimizer_evidence_path(context)
    protected = {
        Path(context.initial_state).resolve(): "initial-state",
        Path(context.protocol_manifest).resolve(): "protocol manifest",
        output: "preflight report",
    }
    if checkpoint in protected:
        raise ValueError(
            f"preflight checkpoint path collides with {protected[checkpoint]}: {checkpoint}"
        )
    if checkpoint.exists() or checkpoint.is_symlink():
        raise FileExistsError(f"ACR-BPDD preflight checkpoint already exists: {checkpoint}")
    if optimizer_evidence in protected:
        raise ValueError(
            "preflight optimizer-evidence path collides with "
            f"{protected[optimizer_evidence]}: {optimizer_evidence}"
        )
    if optimizer_evidence.exists() or optimizer_evidence.is_symlink():
        raise FileExistsError(
            f"ACR-BPDD optimizer evidence already exists: {optimizer_evidence}"
        )
    return checkpoint


def _save_checkpoint_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            torch.save(dict(payload), stream)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _one_step(
    model: FDRACRBPDDDetectionModel,
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler,
    batch: dict[str, Any],
    *,
    optimizer_evidence_path: Path,
    optimizer_attempt: int,
) -> tuple[Tensor, dict[str, Any]]:
    optimizer.zero_grad(set_to_none=True)
    with torch.autocast("cuda", dtype=torch.float16, enabled=True):
        total, _displayed = model.loss(batch)
    bpdd = model.last_fdr_losses["loss_bpdd"]
    common: list[torch.nn.Parameter] = []
    private: list[torch.nn.Parameter] = []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        (private if ".dec_bbox_head." in name else common).append(parameter)
    before = float(scaler.get_scale())
    bpdd_gradients = torch.autograd.grad(
        scaler.scale(bpdd),
        (*common, *private),
        retain_graph=True,
        allow_unused=True,
    )
    common_grads = bpdd_gradients[: len(common)]
    private_grads = bpdd_gradients[len(common) :]
    common_summary = summarize_gradients(common_grads)
    private_summary = summarize_gradients(private_grads)

    scaler.scale(total).backward()
    total_gradients = [
        parameter.grad for parameter in model.parameters() if parameter.requires_grad
    ]
    total_summary = summarize_gradients(total_gradients)
    changed_parameter: torch.nn.Parameter | None = None
    before_update: Tensor | None = None
    for parameter in model.parameters():
        gradient = parameter.grad
        if gradient is not None and bool(torch.count_nonzero(gradient).item()):
            changed_parameter = parameter
            before_update = parameter.detach().clone()
            break
    step_trainer = object.__new__(FDRACRBPDDTrainer)
    step_trainer.model = model
    step_trainer.optimizer = optimizer
    step_trainer.scaler = scaler
    step_trainer.ema = None
    step_trainer.optimizer_evidence_path = Path(optimizer_evidence_path)
    step_trainer.optimizer_attempt = int(optimizer_attempt)
    FDRACRBPDDTrainer.optimizer_step(step_trainer)
    after = float(scaler.get_scale())
    parameter_update = (
        float((changed_parameter.detach() - before_update).abs().max().float().cpu())
        if changed_parameter is not None and before_update is not None
        else 0.0
    )
    optimizer.zero_grad(set_to_none=True)
    return total, {
        "bpdd": bpdd.detach(),
        "common": common_summary,
        "private": private_summary,
        "total": total_summary,
        "amp_before": before,
        "amp_after": after,
        "parameter_update_max_abs": parameter_update,
        "common_parameter_tensors": len(common),
        "private_parameter_tensors": len(private),
        "optimizer_evidence_attempt": int(step_trainer.optimizer_attempt),
        "gradient_norms": dict(step_trainer.last_gradient_norms),
        "bpdd_gradient_scale": before,
    }


def run_cuda_gate(context: PreflightContext) -> dict[str, Any]:
    if not torch.cuda.is_available() or torch.cuda.get_device_name(0) != "NVIDIA GeForce RTX 4090":
        raise RuntimeError("ACR-BPDD preflight requires cuda:0 NVIDIA GeForce RTX 4090")
    device = torch.device("cuda:0")
    environment = _runtime_environment()
    if environment != ACR_BPDD_PROTOCOL["environment"]:
        raise RuntimeError(f"ACR-BPDD environment drift: {environment}")

    loader = _loader(context)
    iterator = iter(loader)
    model = _load_model(context, device).train()
    optimizer = _formal_musgd(model)
    scaler = torch.amp.GradScaler(
        "cuda", enabled=True, init_scale=128.0, growth_interval=2**31 - 1
    )
    optimizer_evidence_path = _optimizer_evidence_path(context)
    first: dict[str, Any] | None = None
    total: Tensor | None = None
    batch: dict[str, Any] | None = None
    stats: Mapping[str, Tensor] | None = None
    evidence = None
    liveness_step = 0
    for attempt in range(1, BPDD_LIVENESS_MAX_STEPS + 1):
        raw = next(iterator)
        if int(raw["img"].shape[0]) != 8:
            raise RuntimeError("ACR-BPDD preflight requires a real batch8")
        candidate_batch = _move_batch(raw, device)
        candidate_total, candidate = _one_step(
            model,
            optimizer,
            scaler,
            candidate_batch,
            optimizer_evidence_path=optimizer_evidence_path,
            optimizer_attempt=attempt - 1,
        )
        candidate_stats = dict(model.last_bpdd_statistics)
        if _bpdd_step_is_live(candidate, candidate_stats):
            first = candidate
            total = candidate_total
            batch = candidate_batch
            stats = candidate_stats
            evidence = model.last_fdr_evidence
            liveness_step = attempt
            break
    if first is None or total is None or batch is None or stats is None:
        raise RuntimeError(
            "ACR-BPDD did not produce a live private-head BPDD gradient within "
            f"{BPDD_LIVENESS_MAX_STEPS} real batches"
        )
    if evidence is None:
        raise RuntimeError("ACR-BPDD preflight lost FDR evidence")

    checkpoint = _preflight_checkpoint_path(context)
    optimizer_state_sha256 = _torch_state_sha256(optimizer.state_dict())
    scaler_state_sha256 = _torch_state_sha256(scaler.state_dict())
    payload = {
        "model": {name: value.detach().cpu() for name, value in model.state_dict().items()},
        "optimizer": optimizer.state_dict(),
        "scaler": scaler.state_dict(),
    }
    _save_checkpoint_create_only(checkpoint, payload)

    model.eval()
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
        before_reload = model.predict(batch["img"])
    restored = _load_model(context, device)
    artifact = torch.load(checkpoint, map_location=device, weights_only=False)
    restored.load_state_dict(artifact["model"], strict=True)
    state_reload_exact = all(
        torch.equal(value, restored.state_dict()[name])
        for name, value in artifact["model"].items()
    )
    restored.eval()
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
        after_reload = restored.predict(batch["img"])
    eval_error = _nested_max_abs(before_reload, after_reload)

    restored.train()
    resumed_optimizer = _formal_musgd(restored)
    resumed_optimizer.load_state_dict(artifact["optimizer"])
    resumed_scaler = torch.amp.GradScaler(
        "cuda", enabled=True, init_scale=128.0, growth_interval=2**31 - 1
    )
    resumed_scaler.load_state_dict(artifact["scaler"])
    optimizer_reload_exact = _torch_state_sha256(
        resumed_optimizer.state_dict()
    ) == optimizer_state_sha256
    scaler_reload_exact = _torch_state_sha256(
        resumed_scaler.state_dict()
    ) == scaler_state_sha256
    _resume_total, second = _one_step(
        restored,
        resumed_optimizer,
        resumed_scaler,
        batch,
        optimizer_evidence_path=optimizer_evidence_path,
        optimizer_attempt=first["optimizer_evidence_attempt"],
    )

    active = float(stats["active_edge_ratio"].detach().float().cpu())
    mass = float(stats["reliability_mass"].detach().float().cpu())
    bpdd_value = float(first["bpdd"].float().cpu())
    stored_replay_error = model.last_acr_replay_max_abs_diff
    replay_error = (
        float(stored_replay_error.detach().float().cpu())
        if isinstance(stored_replay_error, Tensor)
        else float(stored_replay_error or 0.0)
    )
    stored_replay_tolerance = model.last_acr_replay_tolerance
    replay_tolerance = float(stored_replay_tolerance or 0.0)
    dn_queries = int(evidence.dn_corner_logits.shape[2]) if evidence.dn_corner_logits is not None else 0
    checks = {
        "real_visdrone_batch8": int(batch["img"].shape[0]) == 8,
        "loss_bpdd_positive": bpdd_value > 0,
        "active_edge_ratio_positive": active > 0,
        "reliability_mass_positive": mass > 0,
        "common_bpdd_grads_none": first["common"]["gradient_tensors"] == 0,
        "bbox_bpdd_grad_nonzero": first["private"]["nonzero_tensors"] > 0,
        "bbox_bpdd_grads_finite": bool(first["private"]["finite"]),
        "total_grads_finite": bool(first["total"]["finite"]),
        "replay_within_dtype_tolerance": replay_tolerance > 0
        and replay_error <= replay_tolerance,
        "normal_queries_300": int(evidence.corner_logits.shape[2]) == 300,
        "dn_nonempty": dn_queries > 0,
        "forward": bool(torch.isfinite(total.detach()).item()),
        "backward": bool(first["total"]["gradient_tensors"] > 0),
        "musgd_step": math.isfinite(first["parameter_update_max_abs"])
        and first["parameter_update_max_abs"] > 0
        and first["amp_before"] == first["amp_after"] == 128.0,
        "checkpoint_saved": checkpoint.is_file(),
        "strict_state_reload": state_reload_exact,
        "eval_output_exact": eval_error == 0.0,
        "optimizer_scaler_reload": optimizer_reload_exact
        and scaler_reload_exact
        and float(resumed_scaler.get_scale()) == 128.0,
        "resume_step": math.isfinite(second["parameter_update_max_abs"])
        and second["parameter_update_max_abs"] > 0
        and second["amp_before"] == second["amp_after"] == 128.0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"ACR-BPDD CUDA preflight checks failed: {failed}")
    return {
        "source": current_source_identity(Path(context.repository_root).resolve()),
        "protocol_sha256": ACR_BPDD_PROTOCOL_SHA256,
        "initial_state": {
            "path": str(Path(context.initial_state).resolve()),
            "sha256": file_sha256(Path(context.initial_state).resolve()),
        },
        "dataset": {
            **ACR_BPDD_PROTOCOL["dataset"],
            "root": str(Path(context.dataset_root).resolve()),
        },
        "environment": environment,
        "runtime": {
            "device": "cuda:0",
            "gpu_name": torch.cuda.get_device_name(0),
            "batch": 8,
            "imgsz": 640,
            "amp": True,
            "amp_scale": 128.0,
            "optimizer": "MuSGD",
            "optimizer_groups": len(optimizer.param_groups),
            "queries": 300,
        },
        "checks": checks,
        "measurements": {
            "loss_total": float(total.detach().float().cpu()),
            "loss_bpdd": bpdd_value,
            "active_edge_ratio": active,
            "reliability_mass": mass,
            "replay_max_abs_diff": replay_error,
            "replay_tolerance": replay_tolerance,
            "liveness_step": liveness_step,
            "liveness_max_steps": BPDD_LIVENESS_MAX_STEPS,
            "bpdd_gradient_scale": first["bpdd_gradient_scale"],
            "normal_queries": int(evidence.corner_logits.shape[2]),
            "dn_queries": dn_queries,
            "common_parameter_tensors": int(first["common_parameter_tensors"]),
            "common_bpdd_gradient_tensors": int(first["common"]["gradient_tensors"]),
            "bbox_parameter_tensors": int(first["private_parameter_tensors"]),
            "bbox_bpdd_nonzero_gradient_tensors": int(first["private"]["nonzero_tensors"]),
            "amp_scale_before": first["amp_before"],
            "amp_scale_after_first_step": first["amp_after"],
            "amp_scale_after_resume_step": second["amp_after"],
            "first_parameter_update_max_abs": first["parameter_update_max_abs"],
            "resume_parameter_update_max_abs": second["parameter_update_max_abs"],
            "optimizer_state_reload_exact": optimizer_reload_exact,
            "scaler_state_reload_exact": scaler_reload_exact,
            "state_reload_exact": state_reload_exact,
            "eval_output_max_abs_diff": eval_error,
            "cuda_peak_mib": round(torch.cuda.max_memory_allocated() / 1024**2, 2),
        },
        "artifacts": {
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": file_sha256(checkpoint),
            "optimizer_evidence": str(optimizer_evidence_path),
            "optimizer_evidence_sha256": file_sha256(optimizer_evidence_path),
        },
    }


def build_passed_report(
    evidence: Mapping[str, Any], *, manifest: Mapping[str, Any]
) -> dict[str, Any]:
    report = {
        "format_version": 1,
        "status": "passed",
        "manifest_sha256": manifest.get("manifest_sha256"),
        **dict(evidence),
    }
    report["report_sha256"] = public_state_sha256(report)
    return report


def write_create_only_report(path: Path, report: Mapping[str, Any]) -> None:
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical_json_bytes(report) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def validate_preflight_report(
    path: Path,
    *,
    manifest: Mapping[str, Any],
    source: Mapping[str, Any],
    initial_state: Path,
    dataset_root: Path,
    file_hasher: Callable[[Path], str] = file_sha256,
) -> dict[str, Any]:
    unresolved = Path(path)
    if unresolved.is_symlink():
        raise ValueError("ACR-BPDD preflight report must not be a symlink")
    path = unresolved.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"ACR-BPDD preflight report is missing: {path}")
    report = json.loads(path.read_text("utf-8"))
    return _validate_report_payload(
        report,
        manifest=manifest,
        source=source,
        initial_state=initial_state,
        dataset_root=dataset_root,
        file_hasher=file_hasher,
    )


def _validate_report_payload(
    report: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    source: Mapping[str, Any],
    initial_state: Path,
    dataset_root: Path,
    file_hasher: Callable[[Path], str] = file_sha256,
) -> dict[str, Any]:
    report = dict(report)
    digest = report.get("report_sha256")
    unhashed = dict(report)
    unhashed.pop("report_sha256", None)
    if digest != public_state_sha256(unhashed):
        raise ValueError("ACR-BPDD preflight self-hash mismatch")
    if report.get("status") != "passed":
        raise ValueError("ACR-BPDD preflight status must be passed")
    if report.get("source") != dict(source):
        raise ValueError("ACR-BPDD preflight source authority mismatch")
    if report.get("protocol_sha256") != ACR_BPDD_PROTOCOL_SHA256:
        raise ValueError("ACR-BPDD preflight protocol authority mismatch")
    initial = report.get("initial_state", {})
    expected_initial_sha = str(manifest.get("initial_state", {}).get("sha256", "")).upper()
    actual_initial_sha = file_hasher(Path(initial_state).resolve())
    if (
        Path(str(initial.get("path", ""))).resolve() != Path(initial_state).resolve()
        or str(initial.get("sha256", "")).upper() != expected_initial_sha
        or actual_initial_sha != expected_initial_sha
    ):
        raise ValueError("ACR-BPDD preflight initial-state authority mismatch")
    dataset = report.get("dataset", {})
    if dataset.get("sha256") != ACR_BPDD_PROTOCOL["dataset"]["sha256"] or Path(
        str(dataset.get("root", ""))
    ).resolve() != Path(dataset_root).resolve():
        raise ValueError("ACR-BPDD preflight dataset authority mismatch")
    if report.get("environment") != ACR_BPDD_PROTOCOL["environment"]:
        raise ValueError("ACR-BPDD preflight environment authority mismatch")
    runtime = report.get("runtime", {})
    if runtime.get("gpu_name") != "NVIDIA GeForce RTX 4090":
        raise ValueError("ACR-BPDD preflight requires RTX 4090")
    if runtime.get("device") != "cuda:0":
        raise ValueError("ACR-BPDD preflight requires cuda:0")
    if runtime.get("batch") != 8:
        raise ValueError("ACR-BPDD preflight requires batch8")
    if runtime.get("imgsz") != 640:
        raise ValueError("ACR-BPDD preflight requires imgsz640")
    if runtime.get("amp") is not True or runtime.get("amp_scale") != 128.0:
        raise ValueError("ACR-BPDD preflight requires AMP128")
    if runtime.get("optimizer") != "MuSGD":
        raise ValueError("ACR-BPDD preflight requires MuSGD")
    if int(runtime.get("optimizer_groups", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight optimizer groups are empty")
    if runtime.get("queries") != 300:
        raise ValueError("ACR-BPDD preflight requires 300 Queries")
    checks = report.get("checks")
    if not isinstance(checks, Mapping) or any(checks.get(name) is not True for name in REQUIRED_CHECKS):
        raise ValueError("ACR-BPDD preflight required check is false or missing")
    measurements = report.get("measurements", {})
    replay_tolerance = float(measurements.get("replay_tolerance", 0.0))
    replay_error = float(measurements.get("replay_max_abs_diff", math.inf))
    if (
        not math.isfinite(replay_tolerance)
        or replay_tolerance <= 0
        or not math.isfinite(replay_error)
        or replay_error > replay_tolerance
    ):
        raise ValueError("ACR-BPDD preflight replay tolerance failed")
    liveness_step = int(measurements.get("liveness_step", 0))
    if (
        int(measurements.get("liveness_max_steps", 0)) != BPDD_LIVENESS_MAX_STEPS
        or not 1 <= liveness_step <= BPDD_LIVENESS_MAX_STEPS
    ):
        raise ValueError("ACR-BPDD preflight liveness window is invalid")
    if float(measurements.get("bpdd_gradient_scale", 0.0)) != 128.0:
        raise ValueError("ACR-BPDD preflight BPDD gradient scale differs from 128")
    if float(measurements.get("loss_bpdd", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight loss_bpdd is not positive")
    if float(measurements.get("active_edge_ratio", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight active-edge ratio is not positive")
    if float(measurements.get("reliability_mass", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight reliability mass is not positive")
    if int(measurements.get("common_bpdd_gradient_tensors", -1)) != 0:
        raise ValueError("ACR-BPDD preflight detected a shared gradient")
    if int(measurements.get("common_parameter_tensors", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight common parameter set is empty")
    if int(measurements.get("bbox_parameter_tensors", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight box-head parameter set is empty")
    if int(measurements.get("bbox_bpdd_nonzero_gradient_tensors", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight has no box-head gradient")
    if int(measurements.get("normal_queries", -1)) != 300:
        raise ValueError("ACR-BPDD preflight normal Query count mismatch")
    if int(measurements.get("dn_queries", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight DN Query evidence is empty")
    amp_values = (
        measurements.get("amp_scale_before"),
        measurements.get("amp_scale_after_first_step"),
        measurements.get("amp_scale_after_resume_step"),
    )
    if amp_values != (128.0, 128.0, 128.0):
        raise ValueError("ACR-BPDD preflight AMP measurements differ from 128")
    if float(measurements.get("first_parameter_update_max_abs", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight MuSGD did not update a parameter")
    if float(measurements.get("resume_parameter_update_max_abs", 0)) <= 0:
        raise ValueError("ACR-BPDD preflight resumed MuSGD did not update a parameter")
    if measurements.get("optimizer_state_reload_exact") is not True:
        raise ValueError("ACR-BPDD preflight optimizer state reload is not exact")
    if measurements.get("scaler_state_reload_exact") is not True:
        raise ValueError("ACR-BPDD preflight scaler state reload is not exact")
    if measurements.get("state_reload_exact") is not True:
        raise ValueError("ACR-BPDD preflight model state reload is not exact")
    if float(measurements.get("eval_output_max_abs_diff", math.inf)) != 0.0:
        raise ValueError("ACR-BPDD preflight eval output reload is not exact")
    artifacts = report.get("artifacts", {})
    checkpoint_unresolved = Path(str(artifacts.get("checkpoint", "")))
    if checkpoint_unresolved.is_symlink():
        raise ValueError("ACR-BPDD preflight checkpoint must not be a symlink")
    checkpoint = checkpoint_unresolved.resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(f"ACR-BPDD preflight checkpoint is missing: {checkpoint}")
    if str(artifacts.get("checkpoint_sha256", "")).upper() != file_sha256(checkpoint):
        raise ValueError("ACR-BPDD preflight checkpoint SHA256 mismatch")
    try:
        checkpoint_payload = torch.load(
            checkpoint, map_location="cpu", weights_only=False
        )
    except Exception as error:
        raise ValueError("ACR-BPDD preflight checkpoint is unreadable") from error
    if not isinstance(checkpoint_payload, Mapping) or set(checkpoint_payload) != {
        "model",
        "optimizer",
        "scaler",
    }:
        raise ValueError("ACR-BPDD preflight checkpoint structure is invalid")
    if not isinstance(checkpoint_payload["model"], Mapping) or not checkpoint_payload["model"]:
        raise ValueError("ACR-BPDD preflight checkpoint model state is empty")
    optimizer_state = checkpoint_payload["optimizer"]
    if not isinstance(optimizer_state, Mapping) or not optimizer_state.get("param_groups"):
        raise ValueError("ACR-BPDD preflight checkpoint optimizer state is empty")
    if not isinstance(checkpoint_payload["scaler"], Mapping):
        raise ValueError("ACR-BPDD preflight checkpoint scaler state is invalid")

    optimizer_evidence_unresolved = Path(str(artifacts.get("optimizer_evidence", "")))
    if optimizer_evidence_unresolved.is_symlink():
        raise ValueError("ACR-BPDD optimizer evidence must not be a symlink")
    optimizer_evidence = optimizer_evidence_unresolved.resolve()
    if not optimizer_evidence.is_file():
        raise FileNotFoundError(
            f"ACR-BPDD optimizer evidence is missing: {optimizer_evidence}"
        )
    if str(artifacts.get("optimizer_evidence_sha256", "")).upper() != file_sha256(
        optimizer_evidence
    ):
        raise ValueError("ACR-BPDD optimizer evidence SHA256 mismatch")
    try:
        optimizer_rows = [
            json.loads(line)
            for line in optimizer_evidence.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("ACR-BPDD optimizer evidence is unreadable") from error
    expected_attempts = list(range(1, liveness_step + 2))
    if [row.get("optimizer_attempt") for row in optimizer_rows] != expected_attempts:
        raise ValueError(
            "ACR-BPDD optimizer evidence attempts do not match the liveness window"
        )
    if report.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("ACR-BPDD preflight manifest authority mismatch")
    return report


def execute_preflight(
    context: PreflightContext,
    *,
    cuda_runner: Callable[[PreflightContext], dict[str, Any]] = run_cuda_gate,
    manifest_loader: Callable[[Path], dict[str, Any]] = _read_manifest,
    source_loader: Callable[[Path], dict[str, Any]] = current_source_identity,
    state_hasher: Callable[[Path], str] = file_sha256,
    dataset_loader: Callable[[Path], dict[str, Any]] = _dataset_authority,
) -> dict[str, Any]:
    output = Path(context.output)
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"ACR-BPDD preflight report already exists: {output}")
    if Path(context.repository_root).resolve() != ROOT.resolve():
        raise ValueError(
            "ACR-BPDD preflight repository root must equal the running script root"
        )
    _validate_artifact_paths(context)
    manifest = manifest_loader(Path(context.protocol_manifest).resolve())
    source = source_loader(Path(context.repository_root).resolve())
    if manifest.get("source") != source:
        raise ValueError("ACR-BPDD preflight source differs from manifest")
    state = Path(context.initial_state).resolve()
    if state_hasher(state) != manifest.get("initial_state", {}).get("sha256"):
        raise ValueError("ACR-BPDD preflight initial-state differs from manifest")
    if dataset_loader(Path(context.dataset_root).resolve()) != ACR_BPDD_PROTOCOL["dataset"]:
        raise ValueError("ACR-BPDD preflight dataset differs from protocol")
    evidence = cuda_runner(context)
    if state_hasher(state) != str(manifest.get("initial_state", {}).get("sha256", "")).upper():
        raise ValueError("ACR-BPDD initial-state changed during preflight")
    report = build_passed_report(evidence, manifest=manifest)
    _validate_report_payload(
        report,
        manifest=manifest,
        source=source,
        initial_state=state,
        dataset_root=Path(context.dataset_root).resolve(),
        file_hasher=state_hasher,
    )
    write_create_only_report(context.output, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol-manifest", type=Path, required=True)
    parser.add_argument("--initial-state", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    execute_preflight(
        PreflightContext(
            protocol_manifest=args.protocol_manifest,
            initial_state=args.initial_state,
            dataset_root=args.dataset_root,
            output=args.output,
            repository_root=args.repository_root,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "ACR_BPDD_PROTOCOL",
    "ACR_BPDD_PROTOCOL_SHA256",
    "PreflightContext",
    "build_passed_report",
    "build_run_identity",
    "canonical_json_bytes",
    "execute_preflight",
    "file_sha256",
    "public_state_sha256",
    "summarize_gradients",
    "validate_launch_environment",
    "validate_preflight_report",
    "write_create_only_report",
]
