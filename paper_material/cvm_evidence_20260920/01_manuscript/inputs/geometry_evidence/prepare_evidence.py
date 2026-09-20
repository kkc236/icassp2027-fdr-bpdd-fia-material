"""Freeze existing geometry records and parse JUnit; no inference or training."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
REPO = ROOT / 'tmp-work/lrs-system-visdrone-rebuild'
COMMIT = 'f56b210798acab96d628308a5127a2e1399d00dc'
F_COMMIT = 'c1ac0b25e534f6dc5ba85ade418046a30a51a011'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    archive = OUT / 'archived_correctness'
    archive.mkdir(exist_ok=True)
    records = []
    for name in ['red.xml', 'numerical.xml', 'regression-final.xml']:
        source = REPO / 'local-validation' / name
        target = archive / name
        shutil.copy2(source, target)
        records.append({'original_path': str(source), 'archived_path': str(target.relative_to(OUT)), 'sha256': sha(target.read_bytes())})
    source_root = OUT / 'source_f56b210'
    for name in ['src/fdr_math.py', 'src/fdr_head.py', 'src/lrs_runtime_evidence.py', 'tests/test_no_server_correctness.py', 'tests/test_fdr_feasible_geometry.py']:
        data = subprocess.check_output(['git', '-C', str(REPO), 'show', COMMIT + ':' + name])
        target = source_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        current = (REPO / name).read_bytes()
        records.append({'git_commit': COMMIT, 'git_path': name, 'archived_path': str(target.relative_to(OUT)), 'sha256': sha(data), 'current_worktree_same_after_lf_normalization': current.replace(b'\r\n', b'\n') == data.replace(b'\r\n', b'\n')})
    report_details = {}
    for name in ['red.xml', 'numerical.xml', 'regression-final.xml']:
        tree = ET.parse(archive / name).getroot()
        suites = [s.attrib for s in tree.findall('testsuite')]
        relevant = []
        for case in tree.iter('testcase'):
            case_name = case.get('name', '')
            if any(x in case_name for x in ['test_feasible_decode_retains_positive_xyxy_extent', 'test_feasible_decode_keeps_ordinary_boxes_and_preserves_asymmetric_center', 'test_decoder_geometry_survives_actual_cpu_bfloat16_autocast']):
                failure = case.find('failure')
                relevant.append({'classname': case.get('classname'), 'name': case_name, 'status': 'failure' if failure is not None else 'passed', 'failure_message': failure.get('message') if failure is not None else None, 'failure_text': failure.text if failure is not None else None})
        report_details[name] = {'suites': suites, 'relevant_cases': relevant}
    final_cases = report_details['regression-final.xml']['relevant_cases']
    nominal_positive_cases = [c for c in final_cases if c['name'].startswith('test_feasible_decode_retains_positive_xyxy_extent[') and not c['name'].startswith('test_feasible_decode_retains_positive_xyxy_extent[0.0-')]
    assert len(nominal_positive_cases) == 8 and all(c['status'] == 'passed' for c in nominal_positive_cases)
    selected = 'test_decoder_geometry_survives_actual_cpu_bfloat16_autocast'
    assert next(c for c in report_details['red.xml']['relevant_cases'] if c['name'] == selected)['status'] == 'failure'
    assert next(c for c in final_cases if c['name'] == selected)['status'] == 'passed'
    summary_source = ROOT / 'diagnostics/2026-09-09-ac-bpdd-redesign-adversarial-audit.md'
    summary_copy = archive / '2026-09-09-ac-bpdd-redesign-adversarial-audit.md'
    shutil.copy2(summary_source, summary_copy)
    records.append({'original_path': str(summary_source), 'archived_path': str(summary_copy.relative_to(OUT)), 'sha256': sha(summary_copy.read_bytes()), 'evidence_level': 'secondary-summary'})
    secondary = {
        'evidence_level': 'secondary-summary-not-recomputed-from-raw',
        'source': str(summary_copy.relative_to(OUT)),
        'original_source': str(summary_source),
        'run': '/root/sj-tmp/runs/visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2',
        'source_commit_reported': F_COMMIT,
        'historical_name': 'F', 'current_manuscript_role': 'G / LRS-GFDR localization base',
        'window': [91, 100], 'horizontal_below_relative_floor_percent': 0.004483,
        'vertical_below_relative_floor_percent': 0.005329,
        'denominator': None, 'horizontal_count': None, 'vertical_count': None,
        'full_100_epoch_nonfinite_total': None,
        'raw_logs_status': 'Not found locally; remote retrieval was blocked by a powered-off device. No raw-derived frequency verification claimed.',
        'scope': 'Pooled training-forward observations across decoder layers and all query types; not unique boxes, positive matches, or final detections. Threshold is raw_pair < 1e-3, not raw_pair < 0. Machine floor activations are not all represented.'
    }
    caveats = [
        'JUnit records are original archived local test outputs; this preparation only parses and hashes them.',
        'The red and green reports identify the same BF16 regression test; they do not archive identical initial tensors, and no paired numerical effect size is claimed.',
        'Committed source f56b210 was created after the recorded reports. Current test source matches that commit exactly, but the red report does not contain a full pre-fix source manifest.',
        'The eight nominal-positive-reference cases use literal sizes 0.1 and 1e-8 across float16, bfloat16, float32, float64. Casting 1e-8 to float16 underflows to zero; call these nominal-size cases, not eight strictly positive represented inputs.',
        'The separate literal-zero-reference cases are robustness stress tests, outside the manuscript assumption of positive reference sizes.',
        'PASS supports checked predicates only. The reports do not record exact post-fix width/height values; none are inferred.',
        'The BF16 test uses the actual six-layer decoder wrapper with mocked Integral output (-4 for each edge), identity decoder layers, and synthetic features; it is a controlled numerical test, not a full trained-network evaluation or a VisDrone failure frequency.',
        'Historical G in the September 9 audit is legacy AC-BPDD, not the current expert v3 bundle; exclude it from the main geometry evidence table.'
    ]
    manifest = {'archived_files': records, 'frozen_implementation_commit': COMMIT, 'caveats': caveats, 'new_training': False, 'new_model_inference': False}
    (OUT / 'geometry_evidence_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'correctness_test_summary.json').write_text(json.dumps(report_details, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'historical_training_secondary_summary.json').write_text(json.dumps(secondary, ensure_ascii=False, indent=2), encoding='utf-8')
    pending = [
        {'path':'raw/F_LRS_GFDR/full-runtime.jsonl','run_id':'LRS-GFDR base (historical F)','role':'current G localization base','source_commit':F_COMMIT,'remote_run':secondary['run'],'expected_epochs':100},
        {'path':'raw/G_historical_AC_BPDD/full-runtime.jsonl','run_id':'Legacy AC-BPDD (historical G)','role':'historical context only; not expert v3','source_commit':COMMIT,'remote_run':'/root/sj-tmp/runs/visdrone-v2/formal-seed0-lrs_fdr_ac_bpdd-v2','expected_epochs':100}
    ]
    (OUT / 'raw_manifest_PENDING.json').write_text(json.dumps(pending, indent=2), encoding='utf-8')
    print(json.dumps({'frozen_files':len(records),'geometry_nominal_size_cases_passed':len(nominal_positive_cases),'same_named_BF16_test_failure_then_pass':True,'raw_training_log_available':False}))


if __name__ == '__main__':
    main()
