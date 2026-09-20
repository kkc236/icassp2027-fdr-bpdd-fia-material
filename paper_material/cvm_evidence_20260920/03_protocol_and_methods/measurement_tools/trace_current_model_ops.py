"""Inventory executed ATen operations on fixed inference checkpoints, without counting guesses."""
import collections
import gc
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

OUT=Path(sys.argv[1])
CODE=Path('/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code')
sys.path.insert(0,str(CODE))
spec=importlib.util.spec_from_file_location('prior_measure','/root/sj-tmp/evidence/audit-remediation-efficiency-20260915-v3/measure.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
import torch
from torch.utils._python_dispatch import TorchDispatchMode
from torch.utils.flop_counter import FlopCounterMode
from ultralytics import RTDETR
import src.rtdetr_fdr,src.rtdetr_lrs_system,src.rtdetr_bpdd_capacity,src.rtdetr_bpdd_capacity_fia


def metadata(x):
    if isinstance(x,torch.Tensor): return {'shape':list(x.shape),'dtype':str(x.dtype)}
    if isinstance(x,(list,tuple)): return [metadata(v) for v in x]
    if isinstance(x,dict): return {str(k):metadata(v) for k,v in x.items()}
    if isinstance(x,(int,float,str,bool)) or x is None: return x
    return str(x)


class Inventory(TorchDispatchMode):
    def __init__(self):
        super().__init__();self.ops={}
    def __torch_dispatch__(self,func,types,args=(),kwargs=None):
        kwargs=kwargs or {};out=func(*args,**kwargs);name=str(func)
        item=self.ops.setdefault(name,{'schema':str(func._schema),'calls':0,'signatures':{}})
        item['calls']+=1
        signature=json.dumps({'args':metadata(args),'kwargs':metadata(kwargs),'out':metadata(out)},sort_keys=True)
        item['signatures'][signature]=item['signatures'].get(signature,0)+1
        return out


torch.set_num_threads(8)
torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
torch.backends.cudnn.benchmark=False
generator=torch.Generator(device='cuda').manual_seed(20260915)
x=torch.rand((1,3,640,640),generator=generator,device='cuda')
result={'protocol':{'input':[1,3,640,640],'dtype':'float32','training':False,'fusion':'native model.fuse'},'arms':{}}
for arm,(checkpoint,expected) in helper.CHECKPOINTS.items():
    helper.save(OUT/'CURRENT.json',{'arm':arm,'status':'tracing'})
    assert helper.sha256(checkpoint)==expected
    detector=RTDETR(checkpoint);compat=helper.normalize_legacy_no_expert_head(detector.model)
    model=detector.model.cuda().float().eval().fuse(verbose=False)
    with torch.inference_mode():
        for _ in range(2):model(x)
        with Inventory() as inventory: reference=model(x)
        with FlopCounterMode(display=False) as official:model(x)
    with torch.no_grad():
        with Inventory() as lowered: compared=model(x)
        with FlopCounterMode(display=False) as official_lowered:model(x)
    def flat_tensors(value):
        if isinstance(value,torch.Tensor):return [value]
        if isinstance(value,(list,tuple)):return [t for v in value for t in flat_tensors(v)]
        if value is None:return []
        raise TypeError(type(value))
    reference_tensors=flat_tensors(reference);compared_tensors=flat_tensors(compared)
    assert len(reference_tensors)==len(compared_tensors)
    differences=[]
    for left,right in zip(reference_tensors,compared_tensors):
        assert left.shape==right.shape
        torch.testing.assert_close(left,right,rtol=1e-5,atol=1e-6)
        differences.append(float((left-right).abs().max()) if left.numel() else 0.)
    result['arms'][arm]={'checkpoint_sha256':expected,'ops':inventory.ops,
        'official_major_flops':official.get_total_flops(),
        'official_by_op':{str(k):v for k,v in official.get_flop_counts()['Global'].items()},
        'no_grad_ops':lowered.ops,'no_grad_official_major_flops':official_lowered.get_total_flops(),
        'no_grad_official_by_op':{str(k):v for k,v in official_lowered.get_flop_counts()['Global'].items()},
        'inference_no_grad_output_max_abs_errors':differences,
        'legacy_compatibility':compat}
    helper.save(OUT/(arm.replace('+','_')+'.json'),result['arms'][arm])
    assert helper.sha256(checkpoint)==expected
    del model,detector,inventory,official,lowered,official_lowered,reference,compared,reference_tensors,compared_tensors
    gc.collect();torch.cuda.empty_cache()
helper.save(OUT/'inventory.json',result)
helper.save(OUT/'COMPLETE.json',{'status':'inventory_complete','arms':5})
