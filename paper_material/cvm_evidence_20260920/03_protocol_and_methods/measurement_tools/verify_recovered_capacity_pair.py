"""Verify recovered file bytes against Git blobs and compare the FIA-off/on sources."""
import copy
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'paper_material/evidence/audit_remediation_20260915'
FULL = 'a43056af2a843ec9bae109d3420367c13f3bcef6'
OFF = '5ef57473e89e3b91aa5236a18066aed99f5afc0f'


def verified_tree(commit, listing):
    base = EVIDENCE / ('source-' + commit[:7])
    result = {}
    for line in listing.splitlines():
        metadata, relative = line.split('\t', 1)
        mode, kind, object_id = metadata.split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('unsupported source entry ' + line)
        path = (base / relative).resolve()
        path.relative_to(base.resolve())
        data = path.read_bytes()
        computed = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if computed != object_id:
            raise ValueError('recovered Git blob mismatch: ' + relative)
        result[relative] = {'git_blob': object_id, 'sha256': hashlib.sha256(data).hexdigest()}
    return result


def compare():
    recovery = json.loads((EVIDENCE / 'source-recovery.json').read_text())
    full = verified_tree(FULL, recovery['commits'][FULL]['scoped_tree_listing'])
    off = verified_tree(OFF, recovery['commits'][OFF]['scoped_tree_listing'])
    shared = sorted(full.keys() & off.keys())
    changed = [p for p in shared if full[p] != off[p]]
    added = sorted(off.keys() - full.keys())
    expected_added = sorted(['configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd.yaml',
                             'scripts/queue_v3_safe_bpdd_after_joint.sh',
                             'scripts/train_lrs_gfdr_capacity_v3_safe_bpdd.py'])
    assert not changed and added == expected_added and not (full.keys() - off.keys())
    on_path = EVIDENCE / 'source-a43056a/configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml'
    off_path = EVIDENCE / 'source-5ef5747/configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd.yaml'
    on_cfg = yaml.safe_load(on_path.read_text())
    off_cfg = yaml.safe_load(off_path.read_text())
    normalized = copy.deepcopy(on_cfg)
    graph = normalized['backbone'] + normalized['head']
    assert graph[22] == [21, 1, 'FIA', [256]] and graph[23][0] == 21
    def resolve_relative(value, index):
        if isinstance(value, list):
            return [resolve_relative(v, index) for v in value]
        return index + value if value < 0 else value
    for index, layer in enumerate(graph):
        layer[0] = resolve_relative(layer[0], index)
    graph.pop(22)
    def bypass(value):
        if isinstance(value, list):
            return [bypass(v) for v in value]
        return 21 if value == 22 else value - 1 if value > 22 else value
    for layer in graph:
        layer[0] = bypass(layer[0])
    normalized['backbone'], normalized['head'] = graph[:10], graph[10:]
    off_normalized = copy.deepcopy(off_cfg)
    off_graph = off_normalized['backbone'] + off_normalized['head']
    for index, layer in enumerate(off_graph):
        layer[0] = resolve_relative(layer[0], index)
    off_normalized['backbone'], off_normalized['head'] = off_graph[:10], off_graph[10:]
    assert normalized == off_normalized, 'configuration difference exceeds FIA insertion/index remap'
    ep = ROOT / 'paper_material/evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913'
    off_auth = json.loads((ep / 'bpdd-authority.json').read_text())
    on_auth = json.loads((ep / 'joint-authority.json').read_text())
    assert off_auth['initial_state']['sha256'] == on_auth['initial_state']['sha256']
    assert off_auth['dataset']['sha256'] == on_auth['dataset']['sha256']
    excluded = {'data', 'model', 'name', 'project'}
    settings = lambda a: {k:v for k,v in a['settings'].items() if k not in excluded}
    assert settings(off_auth) == settings(on_auth)
    for cfg, authority in ((on_path, on_auth), (off_path, off_auth)):
        # Windows-hosted deployment authorities used CRLF. Test LF and CRLF
        # explicitly and record which bytes match; do not erase that distinction.
        raw = cfg.read_bytes()
        variants = {'git_bytes':raw, 'crlf':raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')}
        assert any(hashlib.sha256(v).hexdigest().upper() == authority['config']['sha256'] for v in variants.values())
    return {'status':'source_and_config_verified', 'full_commit':FULL, 'off_commit':OFF,
            'verified_shared_file_count':len(shared), 'shared_changed_files':changed,
            'off_added_files':added, 'all_shared_src_bytes_equal':True,
            'normalized_config_fia_only':True, 'recorded_settings_equal':True,
            'dataset_sha256':on_auth['dataset']['sha256'],
            'initial_state_sha256':on_auth['initial_state']['sha256'],
            'files':{'full':full, 'off':off},
            'scope':'V12/V13 only; does not certify Base/G/G+F or all historical variants',
            'runtime_initialization_check':'separate measurement; not inferred from source equality',
            'old_authorities_modified':False}


if __name__ == '__main__':
    report = compare()
    output = EVIDENCE / 'source_pair_comparison.json'
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'files'}, indent=2))
