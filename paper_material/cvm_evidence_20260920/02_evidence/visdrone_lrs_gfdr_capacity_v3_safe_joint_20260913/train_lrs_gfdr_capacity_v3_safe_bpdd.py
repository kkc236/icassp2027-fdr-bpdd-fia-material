"""Launch the standalone BPDD arm extracted from the v3-safe joint candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.sync_experiment_checkpoint import write_json_atomic  # noqa: E402
from scripts.train_ace_fdr import require_clean_tracked_worktree  # noqa: E402
from scripts.train_rtdetr_fdr import (  # noqa: E402
    FORMAL_EPOCHS, FROZEN_SETTINGS, current_source_identity, prepare_data_yaml,
)
from scripts.train_visdrone_lrs_system import (  # noqa: E402
    validate_initial_state_file, validate_run_name,
)
from src.lpr_protocol import dataset_signature  # noqa: E402
from src.lrs_runtime_evidence import RuntimeEvidenceRecorder  # noqa: E402
from src.rtdetr_bpdd_capacity import CapacityBPDDTrainer  # noqa: E402


CONFIG = ROOT / "configs" / "rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd.yaml"
METHOD = "lrs_gfdr_capacity_v3_safe_bpdd"
METHOD_REVISION = "v3-safe-loc-kd-decay80-100-no-cls-kd-bpdd-only"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train the v3-safe BPDD-only Formal100 arm")
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--initial-state", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--name", default="formal-seed0-lrs_gfdr_capacity_v3_safe_bpdd")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require_clean_tracked_worktree()
    dataset_root = args.dataset_root.resolve()
    output_root = args.output_root.resolve()
    authority_root = output_root / "authority"
    data_yaml = prepare_data_yaml(dataset_root, "formal", authority_root / "data")
    initial_state = validate_initial_state_file(args.initial_state)
    settings: dict[str, Any] = {
        **FROZEN_SETTINGS,
        "model": str(CONFIG.resolve()),
        "data": str(data_yaml.resolve()),
        "epochs": FORMAL_EPOCHS,
        "seed": 0,
        "project": str(output_root.resolve()),
        "name": validate_run_name(args.name),
        "exist_ok": False,
        "save_period": -1,
    }
    record = {
        "format_version": 2,
        "method_revision": METHOD_REVISION,
        "method": METHOD,
        "source": current_source_identity(),
        "config": {"path": str(CONFIG.resolve()), "sha256": _sha256(CONFIG)},
        "initial_state": {"path": str(initial_state.resolve()), "sha256": _sha256(initial_state)},
        "dataset": dataset_signature(dataset_root),
        "settings": settings,
    }
    authority_path = authority_root / f"{settings['name']}.json"
    if authority_path.exists():
        if json.loads(authority_path.read_text(encoding="utf-8")) != record:
            raise ValueError(f"launch authority conflict: {authority_path}")
    else:
        write_json_atomic(authority_path, record)
    print(json.dumps(record, indent=2, sort_keys=True))
    if args.dry_run:
        return 0

    trainer = CapacityBPDDTrainer(
        overrides=settings, initial_state_path=initial_state, experiment_seed=0,
    )
    recorder = RuntimeEvidenceRecorder()

    def begin_epoch(active_trainer) -> None:
        active_trainer.model.set_completed_epoch(int(active_trainer.epoch) + 1)
        recorder.reset(active_trainer)

    trainer.add_callback("on_train_epoch_start", begin_epoch)
    trainer.add_callback("on_train_batch_end", recorder.capture)
    trainer.add_callback("on_train_epoch_end", recorder.write)
    trainer.train()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
