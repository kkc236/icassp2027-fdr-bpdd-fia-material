"""Audit/rank/render existing final-val predictions. Never imports a model.

TP means score >= .25, same class, greedy score-ordered one-to-one IoU >= .5.
This diagnostic is for selecting examples; it is not COCO AP evaluation.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXPECTED = {
    "dfine_final_val.jsonl": "9f2892072bfc5b60991f8d0543664ffca177e492a3c01304a4ee5de3a8dbf51c",
    "joint_final_val.jsonl": "d946fc4fff304873707ea558f9b702644873f1a7c7b00496fb9512ca74783d72",
    "instances_val.json": "92d2866fe6e6ff4c3101b82c01b7718eb78b3759399042c4501d893798fc8bfa",
}
CLASSES = ["pedestrian", "people", "bicycle", "car", "van", "truck", "tricycle", "awning-tricycle", "bus", "motor"]
SHORT = ["ped", "people", "bike", "car", "van", "truck", "tri", "awning-tri", "bus", "motor"]
COLORS = {"gt": "#00D59A", "tp": "#18B3EF", "fp": "#FF3F78", "fn": "#FFC24A"}
SCORE, IOU = .25, .5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_images():
    """Find an enclosing workspace; a distributed ZIP may need --images."""
    for parent in HERE.parents:
        candidate = parent / "datasets/VisDrone/images/val"
        if candidate.is_dir():
            return candidate
    return None


def load_verified(path, expected_name):
    actual = sha(path)
    if actual != EXPECTED[expected_name]:
        raise ValueError(f"SHA256 mismatch for {path}: {actual}; refuse mixed-version examples")
    return actual


def load_predictions(path, images):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        image_id = str(row["image_id"])
        if image_id in rows or image_id not in images:
            raise ValueError(f"duplicate/unknown image: {image_id}")
        im = images[image_id]
        if (row["width"], row["height"]) != (im["width"], im["height"]):
            raise ValueError(f"original-coordinate dimensions disagree: {image_id}")
        if len(row["detections"]) > 300:
            raise ValueError("prediction cap exceeds recorded 300")
        for d in row["detections"]:
            box = d["bbox_xyxy"]
            cat, score = d["category_id"], d["score"]
            if len(box) != 4 or not all(math.isfinite(x) for x in box):
                raise ValueError("invalid bbox")
            if box[2] < box[0] or box[3] < box[1]:
                raise ValueError("reversed xyxy")
            if isinstance(cat, bool) or cat != int(cat) or not 0 <= cat < 10 or not 0 <= score <= 1:
                raise ValueError("invalid class/score")
            d["category_id"] = int(cat)
        rows[image_id] = row
    if set(rows) != set(images):
        raise ValueError("prediction coverage differs from GT")
    return rows


def iou(a, b):
    inter = max(0., min(a[2], b[2]) - max(a[0], b[0])) * max(0., min(a[3], b[3]) - max(a[1], b[1]))
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union else 0.


def match(gt, detections):
    predictions = sorted((d for d in detections if d["score"] >= SCORE), key=lambda d: -d["score"])
    by_class = defaultdict(list)
    for j, g in enumerate(gt):
        by_class[g["category_id"]].append(j)
    used, matches = set(), []
    for d in predictions:
        eligible = [(iou(d["bbox_xyxy"], gt[j]["bbox_xyxy"]), j) for j in by_class[d["category_id"]] if j not in used]
        best = max(eligible, default=(0., -1))
        j = best[1] if best[0] >= IOU else None
        if j is not None:
            used.add(j)
        matches.append(j)
    return {"predictions": predictions, "matches": matches, "matched_gt": sorted(used),
            "tp": len(used), "fp": len(predictions) - len(used), "fn": len(gt) - len(used)}


def crop_for(gt, indices, width, height):
    """Fixed-size image-relative crop around densest discordant GT cluster."""
    if not indices:
        return [0, 0, width, height]
    cw, ch = min(width, max(480, round(width * .45))), min(height, max(360, round(height * .45)))
    centres = [((gt[i]["bbox_xyxy"][0] + gt[i]["bbox_xyxy"][2]) / 2,
                (gt[i]["bbox_xyxy"][1] + gt[i]["bbox_xyxy"][3]) / 2) for i in indices]
    proposals = []
    for cx, cy in centres:
        x, y = max(0, min(width - cw, round(cx - cw / 2))), max(0, min(height - ch, round(cy - ch / 2)))
        n = sum(x <= xx <= x + cw and y <= yy <= y + ch for xx, yy in centres)
        proposals.append((n, -x, -y, [x, y, x + cw, y + ch]))
    return max(proposals)[3]


def intersects(box, crop):
    return box[0] < crop[2] and box[2] > crop[0] and box[1] < crop[3] and box[3] > crop[1]


def crop_diagnostics(gt, result, crop):
    """Count visible objects using original whole-image assignments, not a crop AP."""
    visible_gt = [j for j, g in enumerate(gt) if intersects(g["bbox_xyxy"], crop)]
    visible_preds = [i for i, d in enumerate(result["predictions"]) if intersects(d["bbox_xyxy"], crop)]
    matched = set(result["matched_gt"])
    return {
        "visible_gt_indices": visible_gt,
        "visible_prediction_indices": visible_preds,
        "visible_missed_gt_indices": [j for j in visible_gt if j not in matched],
        "visible_matched_predictions": sum(result["matches"][i] is not None for i in visible_preds),
        "visible_unmatched_predictions": sum(result["matches"][i] is None for i in visible_preds),
        "matching_scope": "whole image; crop only changes the displayed region",
    }


def load_data(args):
    compressed_gt = args.gt.with_suffix(args.gt.suffix + ".gz")
    if not args.gt.exists() and compressed_gt.exists():
        payload = gzip.decompress(compressed_gt.read_bytes())
        if hashlib.sha256(payload).hexdigest() != EXPECTED["instances_val.json"]:
            raise ValueError("compressed GT SHA256 mismatch")
        args.gt.write_bytes(payload)
    hashes = {
        "gt": load_verified(args.gt, "instances_val.json"),
        "dfine": load_verified(args.raw_dir / "dfine_final_val.jsonl", "dfine_final_val.jsonl"),
        "full": load_verified(args.raw_dir / "joint_final_val.jsonl", "joint_final_val.jsonl"),
    }
    coco = json.loads(args.gt.read_text(encoding="utf-8"))
    if sorted(coco["categories"], key=lambda x: x["id"]) != [{"id": i, "name": name, "supercategory": "object"} for i, name in enumerate(CLASSES)]:
        raise ValueError("unexpected category mapping")
    images = {Path(im["file_name"]).stem: im for im in coco["images"]}
    if len(images) != len(coco["images"]):
        raise ValueError("duplicate image stems in GT")
    by_id = {im["id"]: stem for stem, im in images.items()}
    gt = defaultdict(list)
    for annotation in coco["annotations"]:
        if annotation.get("iscrowd", 0) or annotation.get("ignore", 0):
            raise ValueError("this matching diagnostic does not implement ignore/crowd; inspect protocol")
        x, y, w, h = annotation["bbox"]
        gt[by_id[annotation["image_id"]]].append({"bbox_xyxy": [x, y, x + w, y + h], "category_id": annotation["category_id"], "annotation_id": annotation["id"]})
    image_manifest = json.loads(args.image_manifest.read_text(encoding="utf-8"))
    expected_images = {item["file_name"]: item for item in image_manifest}
    if len(expected_images) != len(image_manifest) or set(expected_images) != {im["file_name"] for im in images.values()}:
        raise ValueError("image manifest coverage differs from GT")
    for stem, im in images.items():
        image_path = args.images / im["file_name"]
        if sha(image_path) != expected_images[im["file_name"]]["sha256"]:
            raise ValueError(f"local image content hash mismatch {stem}")
        with Image.open(image_path) as image:
            if image.size != (im["width"], im["height"]):
                raise ValueError(f"local image size mismatch {stem}")
    dfine = load_predictions(args.raw_dir / "dfine_final_val.jsonl", images)
    full = load_predictions(args.raw_dir / "joint_final_val.jsonl", images)
    hashes["image_manifest"] = sha(args.image_manifest)
    return images, gt, dfine, full, hashes


def rank(args, data):
    images, gt, dfine, full, hashes = data
    rows = []
    for stem, im in images.items():
        a, b = match(gt[stem], dfine[stem]["detections"]), match(gt[stem], full[stem]["detections"])
        gained = sorted(set(b["matched_gt"]) - set(a["matched_gt"]))
        lost = sorted(set(a["matched_gt"]) - set(b["matched_gt"]))
        row = {"image_id": stem, "image_path": str((args.images / im["file_name"]).resolve()), "width": im["width"], "height": im["height"],
               "gt_count": len(gt[stem]), "dfine": {k: a[k] for k in ("tp", "fp", "fn")}, "full": {k: b[k] for k in ("tp", "fp", "fn")},
               "delta_tp": b["tp"] - a["tp"], "delta_fp": b["fp"] - a["fp"],
               "full_gained_gt_indices": gained, "full_lost_gt_indices": lost,
               "suggested_improvement_crop": crop_for(gt[stem], gained, im["width"], im["height"]),
               "suggested_failure_crop": crop_for(gt[stem], lost, im["width"], im["height"])}
        rows.append(row)
    improvements = sorted((r for r in rows if r["full_gained_gt_indices"]), key=lambda r: (r["delta_tp"] - max(0, r["delta_fp"]), len(r["full_gained_gt_indices"])), reverse=True)
    failures = sorted((r for r in rows if r["full_lost_gt_indices"]), key=lambda r: (len(r["full_lost_gt_indices"]), -r["delta_tp"], r["delta_fp"]), reverse=True)
    write_json(args.output / "all_image_diagnostics.json", rows)
    write_json(args.output / "candidate_rankings.json", {"notice": "Candidate rankings only, human image inspection still required. Same fixed thresholds; not COCO AP.", "improvements": improvements[:30], "failures": failures[:30]})
    write_json(args.output / "analysis_manifest.json", {"scope": "VisDrone val; existing final checkpoints; no new inference", "score_threshold": SCORE, "iou_threshold": IOU,
        "matching": "descending score, same-class one-to-one greedy; GT from byte-identical project COCO conversion", "hashes": hashes,
        "raw_dir": str(args.raw_dir.resolve()), "gt_path": str(args.gt.resolve()), "images": str(args.images.resolve()), "image_count": len(images), "gt_count": sum(map(len, gt.values()))})
    print(json.dumps({"images": len(rows), "improvement_candidates": len(improvements), "failure_candidates": len(failures), "output": str(args.output.resolve())}))


@lru_cache(maxsize=8)
def font(size):
    for path in ("C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def render(args, data):
    images, gt, dfine, full, hashes = data
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    if not isinstance(selection.get("examples"), list) or not selection["examples"]:
        raise ValueError("selection must contain at least one manually reviewed genuine example")
    records, rendered = [], []
    for idx, chosen in enumerate(selection["examples"], 1):
        stem = chosen["image_id"]
        im = images[stem]
        crop = chosen.get("crop_xyxy", [0, 0, im["width"], im["height"]])
        if len(crop) != 4 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v != int(v) for v in crop):
            raise ValueError("crop_xyxy must contain four integer pixel coordinates")
        crop = [int(v) for v in crop]
        x0, y0, x1, y1 = crop
        if not (0 <= x0 < x1 <= im["width"] and 0 <= y0 < y1 <= im["height"]):
            raise ValueError("crop outside original image")
        image_path = args.images / im["file_name"]
        with Image.open(image_path) as source:
            original = source.convert("RGB")
        base = original.crop(crop)
        scale = min(660 / base.width, 1200 / base.height)
        w, h = max(1, round(base.width * scale)), max(1, round(base.height * scale))
        # Pillow rounds the resized dimensions; use their exact independent scales.
        sx, sy = w / base.width, h / base.height
        a, b = match(gt[stem], dfine[stem]["detections"]), match(gt[stem], full[stem]["detections"])
        canvas = Image.new("RGB", (max(3 * w + 24, 1320), h + 140), "#F5F7FB")
        draw = ImageDraw.Draw(canvas)
        draw.text((12, 10), f"{chosen.get('label', str(idx))}  |  {stem}", fill="#18202A", font=font(23))
        for col, (title, results) in enumerate((("Ground truth", None), ("D-FINE-L (final)", a), ("Full (final)", b))):
            panel = base.resize((w, h), Image.Resampling.LANCZOS)
            pd = ImageDraw.Draw(panel)
            occupied_labels = []
            def box(det, status, score=None):
                bx0, by0, bx1, by1 = det["bbox_xyxy"]
                if bx1 <= x0 or by1 <= y0 or bx0 >= x1 or by0 >= y1:
                    return
                coords = [(bx0 - x0) * sx, (by0 - y0) * sy, (bx1 - x0) * sx, (by1 - y0) * sy]
                color = COLORS[status]
                if status == "fn":
                    l, t, r, bot = coords
                    for xx in range(round(l), round(r), 12):
                        pd.line((xx, t, min(xx + 7, r), t), fill=color, width=2)
                        pd.line((xx, bot, min(xx + 7, r), bot), fill=color, width=2)
                    for yy in range(round(t), round(bot), 12):
                        pd.line((l, yy, l, min(yy + 7, bot)), fill=color, width=2)
                        pd.line((r, yy, r, min(yy + 7, bot)), fill=color, width=2)
                else:
                    # A wider unmatched outline remains visible under a coincident
                    # higher-score match drawn later; coordinates are unchanged.
                    pd.rectangle(coords, outline=color, width=4 if status == "fp" else 2)
                if chosen.get("show_labels", True):
                    label = SHORT[det["category_id"]] + (f" {score:.2f}" if score is not None else "")
                    label_bounds = pd.textbbox((0, 0), label, font=font(13))
                    label_width = label_bounds[2] - label_bounds[0]
                    tx, ty = max(0, min(coords[0], w - label_width - 2)), max(0, coords[1] - 16)
                    bounds = pd.textbbox((tx, ty), label, font=font(13))
                    for candidate_y in (ty, ty + 16, ty + 32, max(0, ty - 16)):
                        candidate = pd.textbbox((tx, candidate_y), label, font=font(13))
                        if candidate[3] <= h and not any(intersects(candidate, other) for other in occupied_labels):
                            ty, bounds = candidate_y, candidate
                            break
                    occupied_labels.append(bounds)
                    pd.rectangle(bounds, fill="#13232C")
                    pd.text((tx, ty), label, fill=color, font=font(13))
            if results is None:
                for g in gt[stem]:
                    box(g, "gt")
            else:
                # Draw low-score boxes first so duplicates cannot erase the
                # highest-confidence prediction and its score label.
                for d, j in reversed(list(zip(results["predictions"], results["matches"]))):
                    box(d, "tp" if j is not None else "fp", d["score"])
                for j, g in enumerate(gt[stem]):
                    if j not in results["matched_gt"]:
                        box(g, "fn")
            x = 6 + col * (w + 6)
            draw.text((x + 4, 43), title, fill="#18202A", font=font(21))
            canvas.paste(panel, (x, 74))
        draw.text((12, h + 84), "Score >= 0.25; same-class IoU >= 0.50. Green: GT; cyan: matched prediction; pink: unmatched; dashed amber: missed GT.", fill="#283545", font=font(17))
        draw.text((12, h + 109), "Assignments use the complete original image; cropping changes only the view. Boxes extending outside the crop are clipped.", fill="#283545", font=font(17))
        path = args.output / f"example_{idx:02d}_{stem}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path)
        rendered.append(canvas)
        records.append({**chosen, "output": str(path.resolve()), "image_sha256": sha(image_path), "crop_xyxy": crop,
                        "whole_image_dfine": {k: a[k] for k in ("tp", "fp", "fn")}, "whole_image_full": {k: b[k] for k in ("tp", "fp", "fn")},
                        "displayed_dfine": crop_diagnostics(gt[stem], a, crop), "displayed_full": crop_diagnostics(gt[stem], b, crop),
                        "output_sha256": sha(path)})
    if rendered:
        combined = Image.new("RGB", (max(p.width for p in rendered), sum(p.height for p in rendered) + 12 * (len(rendered) - 1)), "white")
        y = 0
        for panel in rendered:
            combined.paste(panel, (0, y))
            y += panel.height + 12
        combined.save(args.output / "qualitative_triptych.png")
        combined.save(args.output / "qualitative_triptych.pdf", resolution=200.)
    write_json(args.output / "render_manifest.json", {"hashes": hashes, "selection_sha256": sha(args.selection), "score": SCORE, "iou": IOU, "examples": records})
    print(json.dumps({"examples": len(records), "output": str(args.output.resolve())}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("rank", "render"))
    p.add_argument("--raw-dir", type=Path, default=HERE / "raw")
    p.add_argument("--gt", type=Path, default=HERE / "gt_reconstructed/instances_val.json")
    p.add_argument("--images", type=Path, default=default_images())
    p.add_argument("--image-manifest", type=Path, default=HERE / "image_manifest.json")
    p.add_argument("--output", type=Path, default=HERE / "analysis")
    p.add_argument("--selection", type=Path)
    args = p.parse_args()
    if args.images is None:
        p.error("could not find the original val images; specify --images with their directory")
    if args.mode == "render" and args.selection is None:
        p.error("render requires --selection with manually reviewed genuine example IDs/crops")
    data = load_data(args)
    rank(args, data) if args.mode == "rank" else render(args, data)


if __name__ == "__main__":
    main()
