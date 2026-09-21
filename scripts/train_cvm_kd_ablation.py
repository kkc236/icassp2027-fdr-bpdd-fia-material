"""Formal100 no-KD / edge-only / mixed-IoU ablations of the frozen Full."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402
import ultralytics  # noqa: E402
from scripts.sync_experiment_checkpoint import write_json_atomic  # noqa: E402
from scripts.train_ace_fdr import require_clean_tracked_worktree  # noqa: E402
from scripts.train_lrs_gfdr_capacity_v3_safe_fia import _sha256, build_settings  # noqa: E402
from scripts.train_rtdetr_fdr import current_source_identity, prepare_data_yaml  # noqa: E402
from scripts.train_visdrone_lrs_system import validate_initial_state_file  # noqa: E402
from src.cvm_kd_ablation import (  # noqa: E402
    BASE_COMMIT, KD_MODES, KDAblationRecorder, KDAblationTrainer, resolved_options,
)
from src.lpr_protocol import dataset_signature  # noqa: E402
from src.rtdetr_bpdd_capacity_fia import CAPACITY_BPDD_FIA_SAFE_CFG  # noqa: E402


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=KD_MODES, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--initial-state", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--name")
    parser.add_argument("--resume", type=Path, help="this arm's unstripped weights/last.pt")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def check_resume_location(checkpoint: Path, run_dir: Path) -> Path:
    checkpoint = checkpoint.resolve(strict=True)
    if checkpoint != (run_dir / "weights" / "last.pt").resolve():
        raise ValueError("resume must use this exact run's weights/last.pt")
    return checkpoint


def main(argv=None):
    args = build_parser().parse_args(argv)
    require_clean_tracked_worktree()
    output = args.output_root.resolve()
    authority_dir = output / "authority"
    name = args.name or f"formal-seed0-kd-{args.mode}"
    initial = validate_initial_state_file(args.initial_state)
    data = prepare_data_yaml(args.dataset_root.resolve(), "formal", authority_dir / "data")
    settings = build_settings(data, output, name)
    run_dir = output / settings["name"]
    environment = {
        "python": platform.python_version(), "torch": torch.__version__,
        "ultralytics": ultralytics.__version__, "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }
    record = {
        "format_version": 3, "method": "cvm-full-kd-ablation",
        "base_commit": BASE_COMMIT, "mode": args.mode,
        "source": current_source_identity(),
        "config": {"path": str(CAPACITY_BPDD_FIA_SAFE_CFG.resolve()),
                   "sha256": _sha256(CAPACITY_BPDD_FIA_SAFE_CFG)},
        "effective_capacity_options": asdict(resolved_options(args.mode)),
        "initial_state": {"path": str(initial), "sha256": _sha256(initial)},
        "dataset": dataset_signature(args.dataset_root.resolve()),
        "settings": settings, "environment": environment,
        "checkpoint_selection": "native validation AP50:95 best; also report epoch100",
    }
    authority = authority_dir / f"{settings['name']}.json"
    checkpoint = check_resume_location(args.resume, run_dir) if args.resume else None
    if checkpoint and not authority.exists():
        raise ValueError("resume requires the original run authority")
    if authority.exists():
        if json.loads(authority.read_text(encoding="utf-8")) != record:
            raise ValueError(f"authority mismatch; original is preserved: {authority}")
    else:
        write_json_atomic(authority, record)
    if not checkpoint and run_dir.exists():
        raise FileExistsError(f"run already exists; use explicit --resume: {run_dir}")
    print(json.dumps(record, indent=2, sort_keys=True))
    if args.dry_run:
        return 0
    if not torch.cuda.is_available():
        raise RuntimeError("Formal100 requires CUDA; CPU execution is limited to tests/dry-run")
    overrides = dict(settings)
    if checkpoint:
        overrides["resume"] = str(checkpoint)
        with (authority_dir / f"{settings['name']}.resumes.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"checkpoint": str(checkpoint), "sha256": _sha256(checkpoint)},
                                    sort_keys=True) + "\n")
    trainer = KDAblationTrainer(
        overrides=overrides, initial_state_path=initial, experiment_seed=0, kd_mode=args.mode,
    )
    recorder = KDAblationRecorder(args.mode)

    def save_effective(active):
        model = getattr(active.model, "module", active.model)
        payload = {
            "mode": model.kd_ablation_mode,
            "options": asdict(model.capacity_options),
            "fresh_initial_state_sha256": active.fresh_initial_state_sha256,
            "parameters": sum(p.numel() for p in model.parameters()),
        }
        destination = Path(active.save_dir) / "kd-effective.json"
        if destination.exists() and json.loads(destination.read_text()) != payload:
            raise ValueError("effective run identity changed across resume")
        write_json_atomic(destination, payload)

    def begin_epoch(active):
        # Preserve the original Safe launcher's actual epoch convention.
        active.model.set_completed_epoch(int(active.epoch) + 1)
        recorder.reset(active)

    trainer.add_callback("on_pretrain_routine_end", save_effective)
    trainer.add_callback("on_train_epoch_start", begin_epoch)
    trainer.add_callback("on_train_batch_end", recorder.capture)
    trainer.add_callback("on_train_epoch_end", recorder.write)
    trainer.train()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
