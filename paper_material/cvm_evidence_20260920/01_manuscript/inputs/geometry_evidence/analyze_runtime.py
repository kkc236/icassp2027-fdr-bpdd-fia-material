"""Aggregate existing epoch geometry logs; performs no model execution.

Usage: python analyze_runtime.py --manifest raw_manifest.json --output-dir analysis
The manifest is a list of run records with path, run_id, role, source_commit,
remote_run, and expected_epochs fields. Paths are relative to the manifest.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric_min(rows, key):
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    if any(not math.isfinite(v) for v in values):
        raise ValueError(f"non-finite persisted statistic: {key}")
    return min(values) if values else None


def aggregate(meta, rows, lo, hi):
    chosen = [r for r in rows if lo <= int(r['completed_epoch']) <= hi]
    if [int(r['completed_epoch']) for r in chosen] != list(range(lo, hi + 1)):
        raise ValueError(f"{meta['run_id']}: missing/duplicate/out-of-order epochs {lo}-{hi}")
    total = sum(int(r['geometry_total']) for r in chosen)
    horizontal = sum(int(r['geometry_horizontal_infeasible']) for r in chosen)
    vertical = sum(int(r['geometry_vertical_infeasible']) for r in chosen)
    if not total or not (0 <= horizontal <= total and 0 <= vertical <= total):
        raise ValueError('invalid geometry counts')
    result = {
        'run_id': meta['run_id'], 'role': meta['role'],
        'source_commit': meta['source_commit'], 'epoch_window': f'{lo}-{hi}',
        'epochs': len(chosen), 'batches': sum(int(r['batches']) for r in chosen),
        'geometry_total': total,
        'horizontal_below_relative_floor_count': horizontal,
        'vertical_below_relative_floor_count': vertical,
        'horizontal_percent': 100 * horizontal / total,
        'vertical_percent': 100 * vertical / total,
        'minimum_raw_horizontal_pair': numeric_min(chosen, 'geometry_minimum_raw_horizontal'),
        'minimum_raw_vertical_pair': numeric_min(chosen, 'geometry_minimum_raw_vertical'),
        'minimum_decoded_width': numeric_min(chosen, 'geometry_minimum_decoded_width'),
        'minimum_decoded_height': numeric_min(chosen, 'geometry_minimum_decoded_height'),
        'nonfinite_geometry_observations': sum(int(r['nonfinite_geometry_observations']) for r in chosen),
        'epochs_with_negative_horizontal_pair': sum(float(r['geometry_minimum_raw_horizontal']) < 0 for r in chosen),
        'epochs_with_negative_vertical_pair': sum(float(r['geometry_minimum_raw_vertical']) < 0 for r in chosen),
    }
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    items = json.loads(args.manifest.read_text(encoding='utf-8'))
    statistics, provenance = [], []
    for meta in items:
        path = args.manifest.parent / meta['path']
        rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        expected = int(meta.get('expected_epochs', 100))
        if len(rows) != expected or [int(r['completed_epoch']) for r in rows] != list(range(1, expected + 1)):
            raise ValueError(f"{meta['run_id']}: incomplete or duplicate epoch sequence")
        revisions = sorted(set(str(r['method_revision']) for r in rows))
        floors = sorted(set(float(r['geometry_minimum_extent']) for r in rows))
        if any(not math.isclose(x, 0.001, rel_tol=1e-6) for x in floors):
            raise ValueError(f'unexpected recorded relative floor: {floors}')
        provenance.append({**meta, 'sha256': sha256(path), 'bytes': path.stat().st_size,
                           'method_revisions': revisions, 'recorded_minimum_extents': floors})
        statistics += [aggregate(meta, rows, 1, expected), aggregate(meta, rows, expected - 9, expected)]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / 'geometry_windows.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(statistics[0]))
        writer.writeheader()
        writer.writerows(statistics)
    interpretation = {
        'scope': 'Recorded training-forward layer/query observations, including matched/unmatched and normal/DN predictions; not final detections or per-object failure rates.',
        'count_definition': 'Raw paired support sum reg_scale + d_left/top + d_right/bottom < minimum_extent (1e-3). Counts include small positive extents and are not strictly negative-extent counts.',
        'denominator': 'Sum geometry_total across every epoch in the stated window; counts pooled before computing percentages.',
        'no_union_rate': 'Horizontal and vertical counts may overlap; their sum is not a unique-box frequency.',
        'not_all_floor_activations': 'numerical_floor_edges was not saved by this recorder, so these counts do not quantify all machine-precision floor activations.',
        'no_causal_accuracy_claim': 'An observed negative raw minimum and positive decoded minimum support feasibility correction; they do not establish AP benefit or quantify causal damage.',
        'nonfinite_scope': 'Zero nonfinite_geometry_observations only characterizes the persisted decoded-minimum observations.',
        'historical_names': 'Historical F denotes the LRS-GFDR base; historical G adds legacy AC-BPDD, not the current local-expert v3 bundle.',
    }
    (args.output_dir / 'geometry_summary.json').write_text(json.dumps({'provenance': provenance, 'statistics': statistics, 'interpretation': interpretation}, indent=2), encoding='utf-8')
    lines = ['# Existing training geometry diagnostics', '', '| Run | Epochs | Observations | Horizontal count (%) | Vertical count (%) | Min raw pair H/V | Min decoded W/H |', '|---|---:|---:|---:|---:|---:|---:|']
    for s in statistics:
        lines.append(f"| {s['run_id']} | {s['epoch_window']} | {s['geometry_total']:,} | {s['horizontal_below_relative_floor_count']:,} ({s['horizontal_percent']:.6f}%) | {s['vertical_below_relative_floor_count']:,} ({s['vertical_percent']:.6f}%) | {s['minimum_raw_horizontal_pair']:.9g} / {s['minimum_raw_vertical_pair']:.9g} | {s['minimum_decoded_width']:.9g} / {s['minimum_decoded_height']:.9g} |")
    lines += ['', *('- ' + v for v in interpretation.values())]
    (args.output_dir / 'GEOMETRY_EVIDENCE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'runs': len(provenance), 'windows': len(statistics), 'output': str(args.output_dir)}))


if __name__ == '__main__':
    main()
