import json
import sys
from pathlib import Path

import pytest

PACKAGE = Path(__file__).parents[1] / 'paper_material/evidence/visdrone_dfine_l_external_20260913'
sys.path.insert(0, str(PACKAGE))
from evaluate_common import predictions_to_coco, evaluate_coco


def fixture_data():
    gt = {'info': {}, 'images': [{'id': 17, 'file_name':'000001_x.jpg','width':1280,'height':720}],
          'categories':[{'id':0,'name':'pedestrian'}],
          'annotations':[{'id':1,'image_id':17,'category_id':0,'bbox':[100,100,80,100],'area':8000,'iscrowd':0}]}
    rows = [{'image_id':'000001_x','width':1280,'height':720,
             'detections':[{'bbox_xyxy':[100,100,180,200],'score':0.9,'category_id':0}]}]
    return gt, rows


def test_filename_mapping_uses_annotation_id_not_numeric_stem():
    gt, rows = fixture_data()
    assert predictions_to_coco(rows, gt)[0]['image_id'] == 17


def test_missing_image_is_rejected_even_if_other_predictions_are_valid():
    gt, rows = fixture_data()
    with pytest.raises(ValueError, match='missing'):
        predictions_to_coco([], gt)


def test_wrong_image_dimensions_are_rejected():
    gt, rows = fixture_data()
    rows[0]['height'] = 1280
    with pytest.raises(ValueError, match='dimension'):
        predictions_to_coco(rows, gt)


def test_perfect_ap_at_300_is_one_not_coco_default_minus_one(tmp_path):
    gt, _ = fixture_data()
    ann = tmp_path/'gt.json'
    pred = tmp_path/'pred.json'
    ann.write_text(json.dumps(gt))
    pred.write_text(json.dumps([{'image_id':17,'category_id':0,'bbox':[100,100,80,100],'score':0.9}]))
    report = evaluate_coco(pred, ann, max_det=300)
    assert report['mAP50_95'] == pytest.approx(1.0)
    assert report['AP50'] == pytest.approx(1.0)


def test_empty_detections_have_zero_ap_not_an_exception(tmp_path):
    gt, _ = fixture_data()
    ann, pred = tmp_path/'gt.json', tmp_path/'pred.json'
    ann.write_text(json.dumps(gt))
    pred.write_text('[]')
    assert evaluate_coco(pred, ann, max_det=300)['mAP50_95'] == 0


def test_dfine_resize_does_not_add_padding_to_nonsquare_image():
    from PIL import Image
    from export_dfine_predictions import preprocess_image
    tensor = preprocess_image(Image.new('RGB', (1280,720), 'white'))
    assert tuple(tensor.shape) == (3,640,640)
    assert float(tensor.min()) == 1.0


def test_joint_boxes_scale_both_axes_independently():
    import torch
    from prediction_contract import stretch_boxes_to_original
    boxes = torch.tensor([[0.,0.,640.,640.], [160.,160.,480.,480.]])
    out = stretch_boxes_to_original(boxes, 1280, 720)
    assert out.tolist() == [[0.,0.,1280.,720.],[320.,180.,960.,540.]]
    assert boxes[0,2] == 640  # input is not modified


def test_common_evaluator_keeps_all_classes_and_records_version(tmp_path):
    gt, _ = fixture_data()
    gt['categories'].append({'id':1, 'name':'people'})
    gt['annotations'].append({'id':2,'image_id':17,'category_id':1,'bbox':[300,100,80,100],'area':8000,'iscrowd':0})
    ann, pred = tmp_path/'gt.json', tmp_path/'pred.json'
    ann.write_text(json.dumps(gt))
    pred.write_text(json.dumps([{'image_id':17,'category_id':0,'bbox':[100,100,80,100],'score':0.9}]))
    result = evaluate_coco(pred, ann, max_det=100)
    assert result['mAP50_95'] == pytest.approx(.5)
    assert result['per_class_AP']['1'] == 0
    assert result['evaluator_version']
