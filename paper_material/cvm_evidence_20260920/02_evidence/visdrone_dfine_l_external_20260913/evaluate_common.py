"""Common prediction validation and optional COCOeval reporting."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from prediction_contract import validate_row


def _coco_image_id(value: str) -> int | str:
    return int(value) if value.isdecimal() else value


def validate_image_coverage(rows: Iterable[Mapping[str, Any]], expected_ids: Iterable[str]) -> list[dict[str, Any]]:
    normalized = [validate_row(row) for row in rows]
    ids = [row["image_id"] for row in normalized]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate prediction image_id")
    expected = {str(value) for value in expected_ids}
    actual = set(ids)
    missing, extra = sorted(expected - actual), sorted(actual - expected)
    if missing or extra:
        raise ValueError(f"missing or extra prediction images: missing={missing[:5]}, extra={extra[:5]}")
    return normalized


def predictions_to_coco(rows: Iterable[Mapping[str, Any]], annotations=None) -> list[dict[str, Any]]:
    """Convert contract rows to COCO detection JSON without clipping coordinates."""

    output: list[dict[str, Any]] = []
    image_map = None
    if annotations is not None:
        image_map = {Path(im['file_name']).stem: im for im in annotations['images']}
        if len(image_map) != len(annotations['images']):
            raise ValueError('duplicate annotation filename stem')
        rows = validate_image_coverage(rows, image_map)
    for row in rows:
        normalized = validate_row(row)
        if image_map is not None:
            im = image_map[normalized['image_id']]
            if (normalized['width'], normalized['height']) != (im['width'], im['height']):
                raise ValueError('prediction image dimensions disagree with annotations')
            image_id = im['id']
        else:
            image_id = _coco_image_id(normalized['image_id'])
        for detection in normalized["detections"]:
            x1, y1, x2, y2 = detection["bbox_xyxy"]
            output.append({
                "image_id": image_id,
                "category_id": int(detection["category_id"]),
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "score": float(detection["score"]),
            })
    return output


def evaluate_coco(prediction_file: Path, annotation_file: Path, *, max_det: int = 300) -> dict[str, Any]:
    """Run standard COCOeval and return raw stats plus explicit maxDet."""

    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    prediction_payload = json.loads(prediction_file.read_text(encoding="utf-8"))
    if not isinstance(prediction_payload, list):
        raise ValueError("COCO prediction file must contain a list")
    ground_truth = COCO(str(annotation_file))
    if prediction_payload:
        detections = ground_truth.loadRes(prediction_payload)
    else:
        detections = COCO()
        detections.dataset = {'images': ground_truth.dataset['images'],
                              'categories': ground_truth.dataset['categories'], 'annotations': []}
        detections.createIndex()
    evaluator = COCOeval(ground_truth, detections, "bbox")
    evaluator.params.imgIds = sorted(ground_truth.getImgIds())
    evaluator.params.maxDets = [1, 10, int(max_det)]
    evaluator.evaluate()
    evaluator.accumulate()
    # COCOeval.summarize hardcodes maxDets=100 for stats[0]. Read the actual
    # precision/recall tensors at the requested cap instead (also valid at 300).
    import numpy as np
    from importlib.metadata import version
    precision, recall = evaluator.eval['precision'], evaluator.eval['recall']
    def mean_valid(v):
        valid = v[v > -1]
        return float(valid.mean()) if valid.size else -1.0
    m = evaluator.params.maxDets.index(int(max_det))
    stats = [mean_valid(precision[:,:,:,0,m]),
             mean_valid(precision[np.isclose(evaluator.params.iouThrs, .5),:,:,0,m]),
             mean_valid(precision[np.isclose(evaluator.params.iouThrs, .75),:,:,0,m]),
             *[mean_valid(precision[:,:,:,area,m]) for area in (1,2,3)],
             *[mean_valid(recall[:,:,0,k]) for k in range(3)],
             *[mean_valid(recall[:,:,area,m]) for area in (1,2,3)]]
    per_class = {str(cat): mean_valid(precision[:,:,i,0,m])
                 for i,cat in enumerate(evaluator.params.catIds)}
    return {
        "evaluator": "pycocotools.COCOeval",
        "evaluator_version": version('pycocotools'),
        "max_det": int(max_det),
        "image_count": len(evaluator.params.imgIds),
        "stats": stats,
        "mAP50_95": stats[0],
        "AP50": stats[1],
        "AP75": stats[2],
        "AP_small": stats[3],
        "AP_medium": stats[4],
        "AP_large": stats[5],
        "AR": stats[8],
        "per_class_AP": per_class,
        "metric_definition": f'COCO IoU .50:.95, maxDets={max_det}; YOLO-derived project annotations',
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True, help="contract JSONL")
    parser.add_argument("--annotations", type=Path, required=True, help="COCO annotations")
    parser.add_argument("--coco-output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--max-det", type=int, default=300)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows = []
    for line in args.predictions.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    annotations = json.loads(args.annotations.read_text(encoding='utf-8'))
    coco_predictions = predictions_to_coco(rows, annotations)
    args.coco_output.parent.mkdir(parents=True, exist_ok=True)
    args.coco_output.write_text(json.dumps(coco_predictions, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    report = evaluate_coco(args.coco_output, args.annotations, max_det=args.max_det)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
