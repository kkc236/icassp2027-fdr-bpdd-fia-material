"""Frozen joint weights with the same PIL stretch preprocessing as D-FINE."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from prediction_contract import stretch_boxes_to_original, validate_row, write_jsonl
from export_dfine_predictions import preprocess_image, _sha256


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--code-root', type=Path, required=True)
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--model-yaml', type=Path, required=True)
    p.add_argument('--images', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--device', default='cuda:0')
    p.add_argument('--score-threshold', type=float, default=.001)
    a = p.parse_args()
    sys.path.insert(0, str(a.code_root.resolve()))
    import torch
    from PIL import Image
    from scripts.export_joint_predictions import load_joint_model
    from ultralytics.models.rtdetr.val import RTDETRValidator

    initial_sha = _sha256(a.checkpoint)
    model, metadata = load_joint_model(a.model_yaml, a.checkpoint)
    model = model.float().to(a.device).eval()
    decoder = RTDETRValidator(save_dir=a.output.parent / 'decoder',
                args={'imgsz':640, 'conf':a.score_threshold, 'max_det':300, 'single_cls':False})
    rows = []
    with torch.inference_mode():
        for path in sorted(p for p in a.images.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png'}):
            with Image.open(path) as f:
                image = f.convert('RGB')
            width, height = image.size
            tensor = preprocess_image(image).unsqueeze(0).to(a.device)
            pred = decoder.postprocess(model(tensor))[0]
            boxes = stretch_boxes_to_original(pred['bboxes'], width, height).cpu()
            scores, classes = pred['conf'].detach().cpu(), pred['cls'].detach().cpu()
            indices = scores.argsort(descending=True)[:300]
            row = {'image_id':path.stem, 'width':width, 'height':height, 'detections':[
                {'bbox_xyxy':boxes[i].tolist(), 'score':float(scores[i]), 'category_id':int(classes[i])}
                for i in indices if float(scores[i]) > a.score_threshold]}
            rows.append(validate_row(row))
    write_jsonl(a.output, rows)
    assert _sha256(a.checkpoint) == initial_sha, 'Read-only checkpoint changed'
    report = {'status':'complete','framework':'Ultralytics','checkpoint':metadata,
              'processed_images':len(rows), 'parameters':sum(v.numel() for v in model.parameters()),
              'prediction_sha256':_sha256(a.output),
              'evaluation':{'imgsz':640,'resize':'PIL bilinear stretch_xy', 'precision':'fp32',
                            'conf':a.score_threshold,'topk':300,'nms':False,'tta':False}}
    a.output.with_suffix('.report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps(report,default=str), flush=True)


if __name__ == '__main__':
    main()
