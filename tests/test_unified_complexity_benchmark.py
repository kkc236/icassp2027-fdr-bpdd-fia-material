import importlib.util
import math
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmark_unified_complexity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("benchmark_unified_complexity", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_frozen_protocol_is_paper_contract():
    module = _load_module()
    assert module.BENCHMARK_PROTOCOL == {
        "imgsz": 640,
        "batch": 1,
        "half": False,
        "warmup_iterations": 100,
        "measured_iterations": 300,
        "cuda_synchronize": True,
        "latency_scope": "preprocess_inference_postprocess",
        "latency_statistic": "median_and_p90_end_to_end_ms",
        "fps_definition": "1000 / median_end_to_end_latency_ms",
        "conf": 0.001,
        "max_det": 300,
    }


def test_latency_summary_uses_median_and_linear_p90():
    module = _load_module()
    result = module.latency_summary([1.0, 2.0, 3.0, 4.0])
    assert result["sample_count"] == 4
    assert result["median_ms"] == 2.5
    assert result["p90_ms"] == pytest.approx(3.7)
    assert result["fps"] == 400.0


def test_predict_kwargs_do_not_emit_deprecated_half_warning():
    module = _load_module()
    kwargs = module.prediction_kwargs(image="fixed-image", device_index=0)
    assert kwargs["source"] == "fixed-image"
    assert "half" not in kwargs
    assert kwargs["imgsz"] == 640
    assert kwargs["batch"] == 1


@pytest.mark.parametrize("values", [[], [0.0], [-1.0], [math.inf], [math.nan]])
def test_latency_summary_rejects_invalid_samples(values):
    module = _load_module()
    with pytest.raises(ValueError):
        module.latency_summary(values)


def test_checkpoint_sha256_is_lowercase_and_exact(tmp_path):
    module = _load_module()
    checkpoint = tmp_path / "best.pt"
    checkpoint.write_bytes(b"unified-complexity\n")
    assert module.checkpoint_sha256(checkpoint) == (
        "856661edfe1651e132c0f8e3dbd659fcfe36571a35a99d99e1dfd2711931f7d6"
    )


def test_report_requires_all_five_authorities_and_preserves_four_paper_rows():
    module = _load_module()
    records = {
        name: {
            "method": name,
            "checkpoint": {"path": f"/{name}/best.pt", "sha256": name * 64},
            "parameters": 1,
            "gflops": 2.0,
            "peak_memory_mib": 3.0,
            "latency": {
                "sample_count": 300,
                "median_ms": 4.0,
                "p90_ms": 5.0,
                "fps": 250.0,
            },
        }
        for name in module.REQUIRED_AUTHORITIES
    }
    report = module.build_report(records, environment={"gpu": "RTX 4090"})
    assert report["status"] == "completed_unified_measurement"
    assert [row["authority_id"] for row in report["paper_rows"]] == list(
        module.PAPER_ROWS
    )
    assert report["strict_bpdd_pair"]["fdr_authority_id"] == "strict_pair_fdr"
    assert report["strict_bpdd_pair"]["bpdd_authority_id"] == "fdr_bpdd"

    records.pop("fdr_bpdd_fia")
    with pytest.raises(ValueError, match="missing benchmark authorities"):
        module.build_report(records, environment={"gpu": "RTX 4090"})
