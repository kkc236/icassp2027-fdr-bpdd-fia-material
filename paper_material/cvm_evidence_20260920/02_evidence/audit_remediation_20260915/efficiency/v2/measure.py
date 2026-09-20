"""Measure existing VisDrone checkpoints; no training or checkpoint writes.

Run in the restored capacity runtime. Results are distinct from historical FPS.
Torch profiler FLOPs are partial operator counts, never a complete-model claim.
"""
from __future__ import annotations
import argparse
import gc
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

CHECKPOINTS = {
    'Baseline': ('/root/sj-tmp/checkpoints/fdr-formal-d97e1eb7/fdr-formal-seed0-control-d97e1eb7-epoch-0100.pt', '9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7'),
    'G': ('/root/sj-tmp/runs/visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2/weights/best.pt', 'DF76A0C8BD5B215D378ACB87EB240D7D1DFB44190167CD8C1E19F86FA18C969D'),
    'G+F': ('/root/sj-tmp/runs/visdrone-v2-lrs-gfdr-fia-20260909/formal-seed0-lrs_gfdr_fia-v1/weights/best.pt', 'C7E6E6B72A0C14A60EF27A91F70F7D80B0D9C53B6FE0021A21787546D5466D63'),
    'G+B': ('/root/sj-tmp/runs/formal-safe-capacity-bpdd-20260913-lrsv2/formal-seed0-capacity-v3-safe-bpdd/weights/best.pt', '661A27E0BE7BD7E7685E7A8AC889D558E0051306FF0BB72ACC8F154C023A377A'),
    'Full': ('/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/best.pt', '39F006DF9548B4D5DA968B9302FC14678FABAF2009802BC09A68FB23DD146BC6'),
}


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest().upper()


def save(path, payload):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    os.replace(temp,path)


def initial_state_probe(code, torch):
    from src.rtdetr_bpdd_capacity import CapacityBPDDDetectionModel
    from src.rtdetr_bpdd_capacity_fia import (CapacityBPDDFIASafeDetectionModel,
        load_capacity_fia_initial_state, remap_capacity_fia_shared_key)
    from src.rtdetr_fdr import _load_initial_state
    state=Path('/root/sj-tmp/protocols/lrs-v2-f56b210/initial-state-seed0.pt')
    expected='935D68428BFC5848DE51F82844658ABBC7EC8C99CBBF6BBF823166D38CB65D5B'
    assert sha256(state)==expected
    torch.manual_seed(0)
    off=CapacityBPDDDetectionModel(code/'configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd.yaml',nc=10,verbose=False,private_seed=10000)
    _load_initial_state(off,state,variant='fdr')
    on=CapacityBPDDFIASafeDetectionModel(code/'configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml',nc=10,verbose=False,private_seed=10000,fia_private_seed=20000)
    artifact=torch.load(state,map_location='cpu',weights_only=False)
    load_capacity_fia_initial_state(on,artifact)
    left,right=off.state_dict(),on.state_dict()
    mismatches=[]
    for name,value in left.items():
        key=remap_capacity_fia_shared_key(name)
        if key not in right or value.shape != right[key].shape or not torch.equal(value,right[key]):
            mismatches.append(name)
    mapped={remap_capacity_fia_shared_key(name) for name in left}
    extra=sorted(set(right)-mapped)
    extra_fia_only=all(name.startswith('model.22.') for name in extra)
    result={'status':'pass' if not mismatches and extra_fia_only else 'mismatch',
            'initial_state_sha256':expected,'compared_tensor_count':len(left),
            'mismatches':mismatches,'extra_keys_fia_only':extra_fia_only,
            'extra_tensor_count':len(extra),'fia_residual_scale':float(on.fia.residual_scale.detach().cpu()),
            'kind':'replay_of_original_initialization_not_new_training'}
    del left,right,artifact,off,on
    gc.collect()
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--code-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    code=args.code_root.resolve(); output=args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=True)
    if (output/'COMPLETE.json').exists() or (output/'efficiency.json').exists():
        raise FileExistsError('use a new output directory')
    sys.path.insert(0,str(code))
    import numpy as np
    import torch
    import ultralytics
    from ultralytics import RTDETR
    assert torch.cuda.is_available()
    torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False
    for name in ('src.rtdetr_fdr','src.rtdetr_lrs_system','src.rtdetr_bpdd_capacity','src.rtdetr_bpdd_capacity_fia'):
        importlib.import_module(name)
    src_files=['src/fdr_head.py','src/fdr_math.py','src/fdr_loss.py','src/bpdd_capacity.py',
               'src/bpdd_capacity_loss.py','src/rtdetr_bpdd_capacity.py','src/rtdetr_bpdd_capacity_fia.py','src/fia.py']
    expected_source=dict(zip(src_files,[
        'faf52c3ffa49f5a1cc94be49d773cb849817917c65debeb09f4c47d376ac23fc',
        'ac60364c008b048d3dfda619354ce3c1c0e5367b3d8a55de54c49ee43ebebb9a',
        'ac60523868ebfdeaeaf63e906095225813f6c250a833f2beb1feea84585c2ecb',
        '38df591604ac891219a66ad9e4ff48240880c9711d4b81e1672c80c8ef3b8db9',
        'dee01d47ab6bacbe120b21f7f6cd0f82d4131890caf1e2c7966bf10882e4eef2',
        'ab1693ac97b1875cbf4a8a5e608b1bba097fb50b35bfe335b40149b3bcd9fe75',
        '9e40ecf65129ab5bef05391d0415b229968b5e929b515d71c9670c94f7ad6550',
        '2686c028429ccb2260ea46c6031e1c55dc2e4d43a09d211be5ca4134585457a1']))
    for relative,expected in expected_source.items():
        assert sha256(code/relative).lower()==expected, 'runtime source mismatch: '+relative
    report={'status':'running','protocol':{'imgsz':640,'batch':1,'dtype':'float32',
        'warmup':100,'iterations':300,'conf':0.001,'max_det':300,'tta':False,'extra_nms':False,
        'input':'fixed seeded uint8 BGR 640x640 image, no file I/O',
        'seed':20260915,'cpu_threads':8,'tf32':False,'cudnn_benchmark':False,
        'latency_scope':'Ultralytics predict: preprocess + model + postprocess; excludes disk I/O',
        'fusion':'native predictor fusion on GPU','flops_scope':'partial PyTorch operator count only'},
        'environment':{'python':platform.python_version(),'torch':torch.__version__,'cuda':torch.version.cuda,
                       'ultralytics':ultralytics.__version__,'gpu':torch.cuda.get_device_name(0)},
        'code_root':str(code),'source_sha256':{p:sha256(code/p) for p in src_files},'rows':[]}
    save(output/'CURRENT.json',{'status':'initialization_probe'})
    try:
        init=initial_state_probe(code,torch)
        save(output/'initialization_probe.json',init)
        report['initialization_probe']=init
        image=np.random.default_rng(20260915).integers(0,256,(640,640,3),dtype=np.uint8)
        for label,(checkpoint,expected) in CHECKPOINTS.items():
            save(output/'CURRENT.json',{'status':'measuring','arm':label,'completed_arms':len(report['rows'])})
            before=sha256(checkpoint); assert before==expected,(label,before)
            detector=RTDETR(checkpoint)
            detector.model.to('cuda:0').float().eval()
            assert all(p.dtype==torch.float32 for p in detector.model.parameters())
            total=sum(p.numel() for p in detector.model.parameters())
            expert_params=sum(p.numel() for n,p in detector.model.named_parameters() if '.local_expert.' in n)
            expected_expert=label in ('G+B','Full')
            assert (expert_params>0)==expected_expert
            calls=[0]
            def expert_called(*unused): calls[0]+=1
            hooks=[m.register_forward_hook(expert_called) for m in detector.model.modules() if type(m).__name__=='LocalBoundaryExpert']
            kwargs=dict(source=image,imgsz=640,batch=1,device=0,conf=0.001,max_det=300,
                        verbose=False,save=False,stream=False,augment=False)
            with torch.inference_mode():
                for _ in range(100): detector.predict(**kwargs)
                assert not detector.predictor.model.fp16
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
                calls[0]=0
                samples=[]
                for _ in range(300):
                    torch.cuda.synchronize(); start=time.perf_counter()
                    detector.predict(**kwargs)
                    torch.cuda.synchronize(); samples.append((time.perf_counter()-start)*1000)
                memory=torch.cuda.max_memory_allocated()/1024**2
                expert_calls=calls[0]
                for hook in hooks: hook.remove()
                partial={}
                try:
                    from torch.profiler import profile,ProfilerActivity
                    with profile(activities=[ProfilerActivity.CPU,ProfilerActivity.CUDA],with_flops=True) as prof:
                        detector.predict(**kwargs)
                    events=prof.key_averages()
                    partial={'status':'partial_only','counted_gflops':sum(e.flops or 0 for e in events)/1e9,
                             'not_a_complete_model_gflops':True,
                             'ops_without_reported_flops':sorted({e.key for e in events if e.key.startswith('aten::') and not e.flops})}
                except Exception as error:
                    partial={'status':'unavailable','error':repr(error)}
            assert len(samples)==300 and all(math.isfinite(s) and s>0 for s in samples)
            assert expert_calls==(300 if expected_expert else 0),(label,expert_calls)
            after=sha256(checkpoint); assert before==after
            ordered=sorted(samples); pos=.9*(len(ordered)-1); low=math.floor(pos); high=math.ceil(pos)
            median=statistics.median(samples)
            row={'arm':label,'checkpoint':checkpoint,'sha256_before':before,'sha256_after':after,
                 'parameters_unfused':total,'parameters_fused':sum(p.numel() for p in detector.model.parameters()),
                 'expert_parameters_unfused':expert_params,'expert_forward_calls_measured':expert_calls,
                 'sample_count':300,'median_ms':median,'p90_ms':ordered[low]+(ordered[high]-ordered[low])*(pos-low),
                 'fps':1000/median,'peak_allocated_mib':memory,'latency_samples_ms':samples,
                 'operator_flops':partial}
            report['rows'].append(row)
            save(output/(label.replace('+','_')+'.json'),row)
            del detector
            if 'prof' in locals(): del prof
            if 'events' in locals(): del events
            gc.collect(); torch.cuda.empty_cache()
        report['status']='completed'
        save(output/'efficiency.json',report)
        save(output/'COMPLETE.json',{'status':'completed','arms':len(report['rows']),
             'initialization_probe_status':init['status'],'full_model_flops_certified':False})
        save(output/'CURRENT.json',{'status':'completed'})
    except Exception as error:
        save(output/'FAILED.json',{'status':'failed','error':repr(error),'completed_arms':len(report['rows'])})
        raise


if __name__=='__main__':
    main()
