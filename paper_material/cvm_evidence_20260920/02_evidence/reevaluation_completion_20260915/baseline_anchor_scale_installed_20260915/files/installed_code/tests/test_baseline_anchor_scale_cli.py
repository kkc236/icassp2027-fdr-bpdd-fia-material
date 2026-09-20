import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


def cli():
    assert importlib.util.find_spec('scripts.eval_baseline_anchor_scale'), 'baseline correction CLI is missing'
    from scripts import eval_baseline_anchor_scale
    return eval_baseline_anchor_scale


def arguments(extra=()):
    return cli().build_parser().parse_args([
        '--checkpoint','baseline.pt','--data-yaml','data.yaml',
        '--output-dir','result',*extra])


def test_native_by_default_and_calibration_explicit():
    assert arguments().anchor_scale_reference is None
    assert arguments(['--anchor-scale-reference','640']).anchor_scale_reference == 640
    assert arguments().imgsz == 800
    assert arguments().split == 'val'


@pytest.mark.parametrize('recorded', [None,800,[640,800]])
def test_training_size_mismatch_is_rejected(recorded):
    with pytest.raises(ValueError, match='training'):
        cli().validate_reference_size({'train_args':{'imgsz':recorded}},640)


def test_matching_training_size_and_native_do_not_fail():
    cli().validate_reference_size({'train_args':{'imgsz':640}},640)
    cli().validate_reference_size({},None)


def test_invalid_inference_size_is_rejected_before_loading_weights():
    with pytest.raises(ValueError, match='divisible'):
        cli().validate_options(arguments(['--imgsz','801']))


def test_existing_results_not_overwritten(tmp_path):
    out=tmp_path/'old'
    out.mkdir()
    sentinel=out/'summary.json'
    sentinel.write_text('original')
    args=arguments(['--output-dir',str(out)])
    with pytest.raises(FileExistsError):
        cli().run(args)
    assert sentinel.read_text() == 'original'


def test_direct_help():
    path=Path(__file__).resolve().parents[1]/'scripts/eval_baseline_anchor_scale.py'
    assert path.is_file(), 'baseline correction CLI is missing'
    result=subprocess.run([sys.executable,str(path),'--help'],capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    assert '--anchor-scale-reference' in result.stdout


def test_prepare_eval_model_uses_supported_device_api():
    import torch
    module=cli()
    assert hasattr(module,'prepare_eval_model'), 'device preparation is not covered by a runtime API check'
    model=torch.nn.Linear(2,2)
    returned=module.prepare_eval_model(model,'cpu')
    assert returned is model
    assert not model.training
    assert next(model.parameters()).device.type == 'cpu'


def test_native_fusion_happens_before_calibration_scope():
    import torch
    from ultralytics.nn.tasks import RTDETRDetectionModel
    config={'nc':10,'backbone':[[-1,1,'Conv',[32,3,1]] for _ in range(12)],
            'head':[[[11],1,'RTDETRDecoder',[10,32,4,4,4,1]]]}
    model=RTDETRDetectionModel(cfg=config,verbose=False).eval()
    assert isinstance(model.model[0].bn,torch.nn.BatchNorm2d)
    prepared=cli().prepare_eval_model(model,'cpu')
    assert not hasattr(prepared.model[0],'bn')
