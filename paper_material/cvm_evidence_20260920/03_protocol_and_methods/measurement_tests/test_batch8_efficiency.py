"""Checks for batch accounting and frozen prior benchmark dependencies."""
from pathlib import Path
import hashlib
import json
import pytest
from scripts.measure_batch8_efficiency import HELPER_SHA, PRIOR_REPORT_SHA, sha256, summarize

ROOT = Path(__file__).resolve().parents[1]


def test_accounting_distinguishes_batch_latency_from_amortization():
    summary = summarize([80., 100., 120.], 8)
    assert summary['batch_median_ms'] == 100.
    assert summary['amortized_ms_per_image'] == 12.5
    assert summary['images_per_second_from_median'] == 80.
    assert summary['images_per_second_from_total_measured_time'] == 80.
    assert summary['batch_p90_ms'] == 116.


def test_single_sample():
    summary = summarize([80.], 8)
    assert summary['batch_p90_ms'] == 80.
    assert summary['images_per_second_from_median'] == 100.


@pytest.mark.parametrize('samples,batch', [([], 8), ([0.], 8), ([-1.], 8), ([float('nan')], 8), ([float('inf')], 8), ([10.], 0)])
def test_reject_invalid_measurements(samples, batch):
    with pytest.raises(ValueError):
        summarize(samples, batch)


def test_frozen_helper_hash_matches():
    assert sha256(ROOT / 'paper_material/evidence/audit_remediation_20260915/efficiency/v3/measure.py') == HELPER_SHA


def test_frozen_prior_report_hash_matches():
    assert sha256(ROOT / 'paper_material/evidence/audit_remediation_20260915/efficiency/v3/efficiency.json') == PRIOR_REPORT_SHA


def test_completed_real_batch8_sample_accounting():
    report = json.loads((ROOT / 'paper_material/evidence/batch8_efficiency_20260916/v1/efficiency.json').read_text())
    assert report['status'] == 'completed'
    assert len(report['rows']) == 5
    assert report['source_sha256_before'] == report['source_sha256_after']
    for row in report['rows']:
        assert row['observed_forward_input']['shape'] == [8, 3, 640, 640]
        assert row['sample_count'] == 300
        assert row['sha256_before'] == row['sha256_after']
        summary = summarize(row['latency_samples_ms'], 8)
        for key, value in summary.items():
            assert value == row[key]


def test_fixed_batch_first_image_matches_prior_single_image_rule():
    import numpy as np
    report = json.loads((ROOT / 'paper_material/evidence/batch8_efficiency_20260916/v1/efficiency.json').read_text())
    first = np.random.default_rng(20260915).integers(0, 256, (640, 640, 3), dtype=np.uint8)
    assert hashlib.sha256(first.tobytes()).hexdigest() == report['input_sha256'][0]
