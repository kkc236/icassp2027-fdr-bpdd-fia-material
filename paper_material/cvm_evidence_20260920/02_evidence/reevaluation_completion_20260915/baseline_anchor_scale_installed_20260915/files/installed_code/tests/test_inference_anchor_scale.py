"""Real stock decoder contracts for the opt-in, reversible anchor correction."""
import importlib.util

import pytest
import torch
from torch import nn
from ultralytics.nn.modules.head import RTDETRDecoder


def correction():
    assert importlib.util.find_spec('src.inference_anchor_scale'), 'anchor correction has not been implemented'
    from src.inference_anchor_scale import calibrated_rtdetr_anchors
    return calibrated_rtdetr_anchors


class DecoderContainer(nn.Module):
    def __init__(self):
        super().__init__()
        self.head = RTDETRDecoder(nc=3, ch=(32,32,32), hd=32, nq=4, nh=4, ndl=2, d_ffn=64, nd=0)

    def forward(self, image):
        return image


@pytest.fixture
def model():
    return DecoderContainer().eval()


@pytest.mark.parametrize('dtype', [torch.float32, torch.float64])
def test_exact_anchor_formula_preserves_centers_and_validity(model, dtype):
    shapes = [[100,100],[50,50],[25,25]]
    original = model.head._generate_anchors
    native, native_mask = original(shapes, dtype=dtype)
    expected, mask = original(shapes, grid_size=.05*.8, dtype=dtype)
    with correction()(model, reference_imgsz=640, inference_imgsz=800) as info:
        actual, actual_mask = model.head._generate_anchors(shapes, dtype=dtype)
        torch.testing.assert_close(actual, expected, rtol=0, atol=0)
        assert torch.equal(mask, actual_mask) and torch.equal(mask, native_mask)
        valid = mask.squeeze(-1)
        assert torch.equal(actual[valid][:,:2], native[valid][:,:2])
        assert actual.dtype == dtype and actual.device.type == 'cpu'
        assert info['scale'] == .8 and info['applied']


@pytest.mark.parametrize('size,enabled', [(640,True), (800,False)])
def test_noop_preserves_exact_cached_anchor_objects(model, size, enabled):
    head = model.head
    head.shapes = [[80,80],[40,40],[20,20]]
    head.anchors, head.valid_mask = head._generate_anchors(head.shapes, dtype=torch.float16)
    before = {key:getattr(head,key) for key in ['anchors','valid_mask','shapes','dynamic']}
    original = head._generate_anchors
    with correction()(model, reference_imgsz=640, inference_imgsz=size, enabled=enabled) as info:
        assert not info['applied']
        assert head._generate_anchors is original
        assert all(getattr(head,k) is v for k,v in before.items())
    assert all(getattr(head,k) is v for k,v in before.items())


def test_restores_generator_cache_and_parameters_after_exception(model):
    head = model.head
    head.shapes = [[80,80],[40,40],[20,20]]
    head.anchors, head.valid_mask = head._generate_anchors(head.shapes)
    before = {key:getattr(head,key) for key in ['anchors','valid_mask','shapes','dynamic']}
    weights = {key:value.clone() for key,value in model.state_dict().items()}
    original = head._generate_anchors
    with pytest.raises(RuntimeError, match='deliberate'):
        with correction()(model, reference_imgsz=640, inference_imgsz=800):
            head.shapes = [[100,100],[50,50],[25,25]]
            head.anchors, head.valid_mask = head._generate_anchors(head.shapes)
            raise RuntimeError('deliberate')
    assert head._generate_anchors is original
    assert all(getattr(head,k) is v for k,v in before.items())
    assert not model._forward_pre_hooks
    assert '_generate_anchors' not in head.__dict__
    assert all(torch.equal(v, model.state_dict()[k]) for k,v in weights.items())


def test_encoder_queries_and_classification_unchanged(model):
    torch.manual_seed(42)
    head = model.head
    shapes = [[20,20],[10,10],[5,5]]
    features = torch.randn(1,525,32)
    with torch.inference_mode():
        native = head._get_decoder_input(features, shapes)
        with correction()(model, reference_imgsz=640, inference_imgsz=800):
            calibrated = head._get_decoder_input(features, shapes)
    assert torch.equal(native[0], calibrated[0])
    assert torch.equal(native[3], calibrated[3])
    assert torch.equal(native[2][...,:2], calibrated[2][...,:2])
    assert not torch.equal(native[2][...,2:], calibrated[2][...,2:])


@pytest.mark.parametrize('reference,size', [(0,800),(640,0),(True,800),(640,801),(640,800.0)])
def test_invalid_sizes_rejected(model, reference, size):
    with pytest.raises(ValueError):
        with correction()(model, reference_imgsz=reference, inference_imgsz=size):
            pass


def test_training_rejected_before_and_during_correction(model):
    model.train()
    with pytest.raises(RuntimeError, match='inference'):
        with correction()(model, reference_imgsz=640, inference_imgsz=800):
            pass
    model.eval()
    with correction()(model, reference_imgsz=640, inference_imgsz=800):
        model.train()
        with pytest.raises(RuntimeError, match='inference'):
            model(torch.zeros(1,3,800,800))


def test_wrong_actual_input_size_rejected(model):
    with correction()(model, reference_imgsz=640, inference_imgsz=800):
        with pytest.raises(ValueError, match='800'):
            model(torch.zeros(1,3,640,640))
        with pytest.raises(ValueError, match='800'):
            model(torch.zeros(1,3,800,640))


def test_nested_calibration_rejected_without_damaging_outer_context(model):
    with correction()(model, reference_imgsz=640, inference_imgsz=800):
        wrapped = model.head._generate_anchors
        with pytest.raises(RuntimeError, match='already'):
            with correction()(model, reference_imgsz=640, inference_imgsz=800):
                pass
        assert model.head._generate_anchors is wrapped


def test_unvalidated_custom_decoder_not_silently_modified():
    class CustomDecoder(RTDETRDecoder):
        pass
    model = nn.Sequential(CustomDecoder(nc=3,ch=(32,32,32),hd=32,nq=4,nh=4,ndl=1,d_ffn=64,nd=0)).eval()
    with pytest.raises(TypeError, match='stock'):
        with correction()(model, reference_imgsz=640, inference_imgsz=800):
            pass
