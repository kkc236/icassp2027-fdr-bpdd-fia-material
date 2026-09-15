"""Emit all predeclared comparisons; no test-based checkpoint selection."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--eval-root',type=Path,required=True)
    p.add_argument('--dfine-output',type=Path,required=True)
    a = p.parse_args()
    package = Path(__file__).resolve().parent
    rows=[]
    metrics=['mAP50_95','AP50','AP75','AP_small','AP_medium','AP_large','AR']
    for endpoint in ('final','best'):
        for split in ('val','test'):
            for cap in (100,300):
                reports={model:json.loads((a.eval_root/f'{model}_{endpoint}_{split}.cap{cap}.json').read_text()) for model in ('dfine','joint')}
                assert reports['dfine']['image_count'] == reports['joint']['image_count']
                delta={k:100*(reports['joint'][k]-reports['dfine'][k]) if min(reports['joint'][k],reports['dfine'][k])>=0 else None for k in metrics}
                rows.append({'endpoint':endpoint,'split':split,'max_det':cap,'reports':reports,'joint_minus_dfine_pp':delta})
    manifest={'format_version':2,'status':'evaluation_complete',
              'comparison_type':'cross_training_protocol_common_evaluation',
              'primary_endpoint':'final vs final; AP50:95 at maxDet=300',
              'secondary_endpoints':'frozen native best; maxDet=100; AP50/AP75/APs/AR/per-class',
              'selection_note':'Native best-selection metrics differ between frameworks. Final is the fixed epoch-100 endpoint.',
              'data_note':'Project YOLO-derived labels; ignored regions unavailable. Not official VisDrone challenge protocol. Test-set prior use is not certified.',
              'limitations':['single training seed','different physical/effective batches, optimizers, precision and augmentations','no claim of causal module gain from the external comparison'],
              'dfine_training':json.loads((a.dfine_output/'run-authority.json').read_text()),
              'joint_training':json.loads((package/'joint-authority.json').read_text()),
              'dataset':json.loads((package/'dataset-preflight.json').read_text()),
              'evaluation_source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in package.glob('*.py')},
              'comparisons':rows,
              'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in a.eval_root.iterdir() if f.is_file()}}
    (a.eval_root/'cross-protocol-manifest.json').write_text(json.dumps(manifest,indent=2,default=str)+'\n')
    lines=['# Cross-protocol common evaluation','',
           'Joint minus D-FINE deltas are percentage points. AP values below are percentages.', '',
           '| Endpoint | Split | maxDet | D-FINE AP | Joint AP | Delta pp |',
           '|---|---|---:|---:|---:|---:|']
    for r in rows:
        delta = r['joint_minus_dfine_pp']['mAP50_95']
        delta_text = 'NA' if delta is None else f'{delta:+.3f}'
        lines.append(f"| {r['endpoint']} | {r['split']} | {r['max_det']} | {100*r['reports']['dfine']['mAP50_95']:.3f} | {100*r['reports']['joint']['mAP50_95']:.3f} | {delta_text} |")
    lines += ['',manifest['data_note'], '', 'This is not a matched-training ablation or a multi-seed significance test.']
    (a.eval_root/'COMPARISON.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__=='__main__':
    main()
