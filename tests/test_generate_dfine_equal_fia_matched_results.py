from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = (
    ROOT
    / "paper_material"
    / "evidence"
    / "dfine_s_equal_fia_matched_20260823"
    / "protocol.json"
)

METRIC_NAMES = (
    "AP",
    "AP50",
    "AP75",
    "APs",
    "APm",
    "APl",
    "AR1",
    "AR10",
    "AR100",
    "ARs",
    "ARm",
    "ARl",
)


def _protocol() -> dict:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def _complete_status() -> dict:
    treatment_checkpoint = "/runs/treatment/best_stg2.pth"
    control_checkpoint = "/runs/control/best_stg2.pth"
    treatment_sha = "a" * 64
    control_sha = "b" * 64
    stats = {
        ("treatment", "val"): [0.31 + index / 100 for index in range(12)],
        ("treatment", "test"): [0.23 + index / 100 for index in range(12)],
        ("control", "val"): [0.30 + index / 100 for index in range(12)],
        ("control", "test"): [0.20 + index / 100 for index in range(12)],
    }
    checkpoints = {
        "treatment": (treatment_checkpoint, treatment_sha),
        "control": (control_checkpoint, control_sha),
    }
    evaluations = []
    for method, split in (
        ("treatment", "val"),
        ("treatment", "test"),
        ("control", "val"),
        ("control", "test"),
    ):
        checkpoint, checkpoint_sha = checkpoints[method]
        evaluations.append(
            {
                "method": method,
                "split": split,
                "checkpoint": checkpoint,
                "checkpoint_sha256": checkpoint_sha,
                "returncode": 0,
                "ema_restored": True,
                "metrics": {"coco_eval_bbox": stats[(method, split)]},
            }
        )
    return {
        "format": "dfine.post_training_evaluations",
        "version": 1,
        "status": "complete",
        "runs": {
            method: {
                "best": {
                    "checkpoint_path": checkpoint,
                    "checkpoint_sha256": checkpoint_sha,
                }
            }
            for method, (checkpoint, checkpoint_sha) in checkpoints.items()
        },
        "evaluations": evaluations,
    }


def test_builds_pure_matched_documents_with_exact_split_local_deltas() -> None:
    from tools.generate_dfine_equal_fia_matched_results import build_matched_results

    status = _complete_status()
    status_before = copy.deepcopy(status)
    protocol = _protocol()
    protocol_before = copy.deepcopy(protocol)

    documents = build_matched_results(status, protocol)

    assert status == status_before
    assert protocol == protocol_before
    assert set(documents) == {"pair_summary", "paper_results", "markdown"}

    pair = documents["pair_summary"]
    assert pair["protocol_id"] == protocol["protocol_id"]
    assert pair["strict_paired"] is False
    assert pair["bundle_attribution_boundary"] == protocol[
        "bundle_attribution_boundary"
    ]
    assert pair["source_ids"] == {
        "treatment": "dfine_s_equal_fia_24c9cb1_seed0_formal132_best_val_test",
        "control": "dfine_s_official7fe2_seed0_formal132_best_val_test",
        "pair": "dfine_s_equal_fia_vs_official7fe2_matched_pair",
    }
    assert pair["source_id"] == "dfine_s_equal_fia_vs_official7fe2_matched_pair"
    assert pair["metric_availability"] == {
        "precision": {
            "value": None,
            "status": "not_reported_by_coco_evaluator",
        },
        "recall": {
            "value": None,
            "status": "not_reported_by_coco_evaluator",
        },
        "f1": {
            "value": None,
            "status": "not_reported_by_coco_evaluator",
        },
    }
    assert pair["arms"]["treatment"]["checkpoint"] == {
        "path": "/runs/treatment/best_stg2.pth",
        "sha256": "a" * 64,
    }
    assert pair["arms"]["control"]["checkpoint"] == {
        "path": "/runs/control/best_stg2.pth",
        "sha256": "b" * 64,
    }

    for split in ("val", "test"):
        comparison = pair["comparisons"][split]
        treatment = status["evaluations"][0 if split == "val" else 1]["metrics"][
            "coco_eval_bbox"
        ]
        control = status["evaluations"][2 if split == "val" else 3]["metrics"][
            "coco_eval_bbox"
        ]
        assert comparison["treatment_metrics"] == dict(zip(METRIC_NAMES, treatment))
        assert comparison["control_metrics"] == dict(zip(METRIC_NAMES, control))
        assert comparison["delta_pp"] == {
            name: (treatment[index] - control[index]) * 100
            for index, name in enumerate(METRIC_NAMES)
        }
    assert pair["comparisons"]["val"]["treatment_metrics"]["AP"] == 0.31
    assert pair["comparisons"]["test"]["treatment_metrics"]["AP"] == 0.23
    assert pair["comparisons"]["val"]["delta_pp"]["AP"] == (
        0.31 - 0.30
    ) * 100
    assert pair["comparisons"]["test"]["delta_pp"]["AP"] == (
        0.23 - 0.20
    ) * 100

    paper = documents["paper_results"]
    assert [(row["split"], row["id"]) for row in paper["rows"]] == [
        ("val", "DF-0"),
        ("val", "DF-1"),
        ("test", "DF-0"),
        ("test", "DF-1"),
    ]
    assert all(row["precision"] is None for row in paper["rows"])
    assert all(row["recall"] is None for row in paper["rows"])
    assert all(row["f1"] is None for row in paper["rows"])
    assert all(
        row["precision_recall_f1_status"] == "not_reported_by_coco_evaluator"
        for row in paper["rows"]
    )
    assert paper["metric_availability"] == pair["metric_availability"]
    assert "## VisDrone val" in documents["markdown"]
    assert "## VisDrone test" in documents["markdown"]
    assert documents["markdown"].count("| DF-0 |") == 2
    assert documents["markdown"].count("| DF-1 |") == 2


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda status: status.update(format="different.format"),
            "postrun format",
        ),
        (lambda status: status.update(version=2), "postrun version"),
        (lambda status: status.update(status="running"), "status=complete"),
        (
            lambda status: status["evaluations"].reverse(),
            "fixed evaluation order",
        ),
        (
            lambda status: status["evaluations"][0].update(returncode=1),
            "returncode=0",
        ),
        (
            lambda status: status["evaluations"][0].update(ema_restored=False),
            "ema_restored=true",
        ),
        (
            lambda status: status["evaluations"][1].update(
                checkpoint="/runs/treatment/other.pth"
            ),
            "same checkpoint",
        ),
        (
            lambda status: status["evaluations"][0].update(
                checkpoint_sha256="c" * 64
            ),
            "checkpoint SHA-256",
        ),
        (
            lambda status: status["evaluations"][0]["metrics"][
                "coco_eval_bbox"
            ].__setitem__(0, math.nan),
            "finite numeric",
        ),
        (
            lambda status: status["evaluations"][0]["metrics"][
                "coco_eval_bbox"
            ].pop(),
            "exactly 12",
        ),
    ],
)
def test_rejects_incomplete_or_inconsistent_postrun_status(
    mutate, message: str
) -> None:
    from tools.generate_dfine_equal_fia_matched_results import MatchedResultError
    from tools.generate_dfine_equal_fia_matched_results import build_matched_results

    status = _complete_status()
    mutate(status)

    with pytest.raises(MatchedResultError, match=message):
        build_matched_results(status, _protocol())


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda protocol: protocol["arms"]["control"].update(
                source_commit="0" * 40
            ),
            "control source commit",
        ),
        (
            lambda protocol: protocol["arms"]["treatment"].update(
                source_commit="0" * 40
            ),
            "treatment source commit",
        ),
        (
            lambda protocol: protocol["bundle_attribution_boundary"].update(
                isolated_fia_gain_claim_allowed=True
            ),
            "bundle attribution boundary",
        ),
    ],
)
def test_rejects_protocols_that_do_not_bind_the_fixed_sources_or_boundary(
    mutate, message: str
) -> None:
    from tools.generate_dfine_equal_fia_matched_results import MatchedResultError
    from tools.generate_dfine_equal_fia_matched_results import build_matched_results

    protocol = _protocol()
    mutate(protocol)

    with pytest.raises(MatchedResultError, match=message):
        build_matched_results(_complete_status(), protocol)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_atomic_writer_uses_only_the_new_result_bundle_paths(tmp_path: Path) -> None:
    from tools.generate_dfine_equal_fia_matched_results import build_matched_results
    from tools.generate_dfine_equal_fia_matched_results import write_matched_results

    protected = [
        ROOT / "paper_material" / "results" / "MAIN_TABLE_ZH.md",
        ROOT / "paper_material" / "results" / "main_results.json",
        ROOT / "paper_material" / "results" / "RESULTS_ZH.md",
        ROOT / "README.md",
    ]
    hashes_before = {path: _sha256(path) for path in protected if path.is_file()}
    documents = build_matched_results(_complete_status(), _protocol())
    output_root = tmp_path / "new-bundle"

    written = write_matched_results(documents, output_root)

    expected = {
        "pair_summary": output_root / "pair_summary.json",
        "paper_results": (
            output_root
            / "paper_material"
            / "results"
            / "dfine_equal_fia_matched_results.json"
        ),
        "markdown": (
            output_root
            / "paper_material"
            / "results"
            / "DFINE_EQUAL_FIA_MATCHED_RESULTS_ZH.md"
        ),
    }
    assert written == {key: str(path.resolve()) for key, path in expected.items()}
    assert json.loads(expected["pair_summary"].read_text("utf-8")) == documents[
        "pair_summary"
    ]
    assert json.loads(expected["paper_results"].read_text("utf-8")) == documents[
        "paper_results"
    ]
    assert expected["markdown"].read_text("utf-8") == documents["markdown"]
    assert all(path.read_bytes().endswith(b"\n") for path in expected.values())
    assert not list(output_root.rglob("*.tmp"))
    assert {path: _sha256(path) for path in hashes_before} == hashes_before


def test_writer_refuses_a_nonempty_output_root_without_touching_it(
    tmp_path: Path,
) -> None:
    from tools.generate_dfine_equal_fia_matched_results import MatchedResultError
    from tools.generate_dfine_equal_fia_matched_results import build_matched_results
    from tools.generate_dfine_equal_fia_matched_results import write_matched_results

    output_root = tmp_path / "occupied"
    output_root.mkdir()
    sentinel = output_root / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")

    with pytest.raises(MatchedResultError, match="new or empty"):
        write_matched_results(
            build_matched_results(_complete_status(), _protocol()), output_root
        )

    assert list(output_root.iterdir()) == [sentinel]
    assert sentinel.read_text("utf-8") == "keep"


def test_cli_reads_complete_status_and_writes_only_a_fresh_output_root(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "postrun_status.json"
    status_path.write_text(
        json.dumps(_complete_status(), allow_nan=False), encoding="utf-8"
    )
    output_root = tmp_path / "generated"
    script = ROOT / "tools" / "generate_dfine_equal_fia_matched_results.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--postrun-status",
            str(status_path),
            "--protocol",
            str(PROTOCOL_PATH),
            "--output-root",
            str(output_root),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "written"
    assert Path(report["files"]["pair_summary"]) == (
        output_root / "pair_summary.json"
    ).resolve()
    assert (output_root / "pair_summary.json").is_file()
    assert (
        output_root
        / "paper_material"
        / "results"
        / "dfine_equal_fia_matched_results.json"
    ).is_file()
    assert (
        output_root
        / "paper_material"
        / "results"
        / "DFINE_EQUAL_FIA_MATCHED_RESULTS_ZH.md"
    ).is_file()
