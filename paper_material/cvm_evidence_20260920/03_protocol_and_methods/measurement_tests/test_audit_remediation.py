"""Evidence and measurement contracts; no training, GPU, or network calls."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'paper_material/evidence/audit_remediation_20260915'


def test_recovered_pair_checks_all_git_blobs_and_fia_only_graph():
    from scripts.verify_recovered_capacity_pair import compare
    result=compare()
    assert result['verified_shared_file_count']==239
    assert result['shared_changed_files']==[]
    assert len(result['off_added_files'])==3
    assert result['normalized_config_fia_only'] is True
    assert result['old_authorities_modified'] is False


def test_recovered_archives_match_transferred_sha256():
    for name,expected in [
        ('source-a43056af2a843ec9bae109d3420367c13f3bcef6.tar.gz','039274df02eafdd3ae5aea24c4d6cfab5f872ee590effd98bb98477d3aac1e8f'),
        ('source-5ef57473e89e3b91aa5236a18066aed99f5afc0f.tar.gz','5d22be64ec119851dce16715defe2a0abae8713ae62e1e6b5a0da436cf58d6f1')]:
        assert hashlib.sha256((EVIDENCE/name).read_bytes()).hexdigest()==expected


def make_head(options,expert=None,inputs=3):
    head=type('FDRRTDETRDecoder',(),{})()
    head.fdr_options=options
    head.decoder=SimpleNamespace(local_expert=expert)
    head.f=list(range(inputs))
    return SimpleNamespace(named_modules=lambda:[('model.28',head)])


def test_legacy_compatibility_only_adds_absent_inactive_selector():
    from scripts.measure_current_joint_efficiency import normalize_legacy_no_expert_head
    options={'feasible_geometry':True,'local_expert':False}
    report=normalize_legacy_no_expert_head(make_head(options))
    assert options=={'feasible_geometry':True,'local_expert':False,'local_expert_preserve_base':False}
    assert len(report)==1
    assert normalize_legacy_no_expert_head(make_head(options))==[]


@pytest.mark.parametrize('options,expert,inputs',[
    ({'local_expert':True},None,3),({},object(),3),({},None,4)])
def test_legacy_compatibility_rejects_possible_expert_route(options,expert,inputs):
    from scripts.measure_current_joint_efficiency import normalize_legacy_no_expert_head
    with pytest.raises(AssertionError):
        normalize_legacy_no_expert_head(make_head(options,expert,inputs))
    assert 'local_expert_preserve_base' not in options


def test_current_expert_selector_is_not_overwritten():
    from scripts.measure_current_joint_efficiency import normalize_legacy_no_expert_head
    options={'local_expert':True,'local_expert_preserve_base':True}
    assert normalize_legacy_no_expert_head(make_head(options,object(),4))==[]
    assert options['local_expert_preserve_base'] is True


def test_table_package_retains_primary_endpoint_and_negative_test_results():
    package=ROOT/'paper_material/submission_tables_20260915'
    tables={t['id']:t for t in json.loads((package/'tables.json').read_text(encoding='utf-8'))['tables']}
    assert len(tables)==11
    assert [r[0] for r in tables['T1']['rows']]==['Final']*3+['Best']*3
    assert len(tables['S6']['rows'])==4
    assert tables['S6']['rows'][-1][-1]<0
    assert abs(tables['S1']['rows'][-1][1]-0.11793293)<1e-8
    assert [r[1] for r in tables['S5']['rows']]==['800','800']
    for table in tables.values():
        assert all(len(row)==len(table['headers']) for row in table['rows'])


def test_all_table_input_hashes_are_current():
    path=ROOT/'paper_material/submission_tables_20260915/provenance.json'
    record=json.loads(path.read_text(encoding='utf-8'))
    assert record['deferred_by_user']
    for relative,digest in record['inputs'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,relative


def test_five_arm_efficiency_is_complete_and_all_checkpoints_unchanged():
    import statistics
    from scripts.measure_current_joint_efficiency import CHECKPOINTS
    base=EVIDENCE/'efficiency'
    manifest=json.loads((base/'transport_manifest.json').read_text())
    assert len(manifest['files'])==22
    for name,item in manifest['files'].items():
        data=(base/name).read_bytes()
        assert len(data)==item['size']
        assert hashlib.sha256(data).hexdigest()==item['sha256']
    report=json.loads((base/'v3/efficiency.json').read_text())
    assert report['status']=='completed'
    assert len(report['rows'])==5
    assert report['initialization_probe']['status']=='pass'
    assert report['initialization_probe']['compared_tensor_count']==994
    for row in report['rows']:
        assert row['sha256_before']==row['sha256_after']==CHECKPOINTS[row['arm']][1]
        assert len(row['latency_samples_ms'])==300
        assert row['median_ms']==statistics.median(row['latency_samples_ms'])
        assert row['expert_forward_calls_measured']==(300 if row['arm'] in ('G+B','Full') else 0)
    assert json.loads((base/'v3/COMPLETE.json').read_text())['full_model_flops_certified'] is False
