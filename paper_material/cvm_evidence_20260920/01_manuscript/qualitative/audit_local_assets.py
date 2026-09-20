"""Read-only dataset audit; writes only the qualitative handoff artifacts."""
import gzip
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = ROOT / 'tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913'
REPORTS = EVIDENCE / 'common_evaluation_20260915'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    gt = HERE / 'gt_reconstructed/instances_val.json'
    expected = json.loads((REPORTS / 'dataset-preflight.json').read_text())['val']
    data = json.loads(gt.read_text())
    assert sha(gt) == expected['sha256']
    assert len(data['images']) == expected['images'] == 548
    assert len(data['annotations']) == expected['annotations'] == 38759
    compressed = gt.with_suffix('.json.gz')
    compressed.write_bytes(gzip.compress(gt.read_bytes(), mtime=0))
    assert hashlib.sha256(gzip.decompress(compressed.read_bytes())).hexdigest() == expected['sha256']
    rows = []
    for im in data['images']:
        p = ROOT / 'datasets/VisDrone/images/val' / im['file_name']
        original = ROOT / 'datasets/VisDrone/VisDrone2019-DET-val/images' / im['file_name']
        h = sha(p)
        assert h == sha(original), im['file_name']
        rows.append({'file_name': im['file_name'], 'width': im['width'], 'height': im['height'], 'sha256': h})
    (HERE / 'image_manifest.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    reports = {name: json.loads((REPORTS / f'{name}.report.json').read_text()) for name in ('dfine_final_val', 'joint_final_val')}
    manifest = {
        'status': 'prepared; actual final-val prediction JSONLs not present locally at audit time; no qualitative example selected or rendered',
        'raw_remote_directory': '/root/sj-tmp/eval/visdrone_dfine_bs4_results_20260914/',
        'required_raw_files': {
            'dfine_final_val.jsonl': '9f2892072bfc5b60991f8d0543664ffca177e492a3c01304a4ee5de3a8dbf51c',
            'joint_final_val.jsonl': 'd946fc4fff304873707ea558f9b702644873f1a7c7b00496fb9512ca74783d72'},
        'gt': {'path': str(gt.relative_to(ROOT)), 'sha256': sha(gt), 'compressed_path': str(compressed.relative_to(ROOT)),
               'compressed_sha256': sha(compressed), 'images': len(rows), 'annotations': len(data['annotations']),
               'source': str((REPORTS / 'dataset-preflight.json').relative_to(ROOT)),
               'converter': str((EVIDENCE / 'convert_visdrone_yolo_to_coco.py').relative_to(ROOT)),
               'converter_sha256': sha(EVIDENCE / 'convert_visdrone_yolo_to_coco.py'),
               'process': 'existing archived converter over existing local val images/YOLO labels, then LF normalization; exact equality with recorded server GT SHA256'},
        'images': {'path': 'datasets/VisDrone/images/val', 'count': len(rows), 'byte_equal_to_official_extracted_originals': len(rows), 'manifest': 'image_manifest.json'},
        'prediction_contract': 'one row per image filename stem; original width/height; detections bbox_xyxy in original pixels, category_id 0..9, score 0..1',
        'categories': data['categories'],
        'recorded_final_reports': reports,
        'scope': 'val only; no training, inference, weight load, network, or internal component test access in artifact preparation',
        'script_validation': 'Python compilation and CLI help passed; ranking/rendering require real hashed raw predictions and have not run on them'
    }
    (HERE / 'asset_manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    output = HERE / 'qualitative_handoff_small.zip'
    included = ['prepare_qualitative.py', 'audit_local_assets.py', 'README_ZH.md', 'asset_manifest.json', 'image_manifest.json', 'gt_reconstructed/instances_val.json.gz']
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name in included:
            z.write(HERE / name, name)
    print(json.dumps({'exact_gt_sha256': sha(gt), 'original_images_byte_equal': len(rows), 'zip': str(output), 'zip_bytes': output.stat().st_size, 'zip_sha256': sha(output)}))

if __name__ == '__main__':
    main()
