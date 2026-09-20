"""Shape-based, fail-closed arithmetic accounting for executed inference ATen ops.

MAC=2; elementary transcendental=1 equivalent op. Comparisons, indexing,
integer arithmetic and memory movement are explicitly outside floating FLOPs.
This is dense algorithmic work, not hardware instructions or boundary sparsity.
"""
from __future__ import annotations
from collections import defaultdict
import json
import math
from pathlib import Path
import sys

CONVENTION='dense_scalar_arithmetic_v1_mac2_transcendental1'


def tensor(x):
    return isinstance(x,dict) and 'shape' in x and 'dtype' in x


def floating(x):
    return tensor(x) and x['dtype'] in ('torch.float16','torch.bfloat16','torch.float32','torch.float64')


def numel(x):
    if not tensor(x): raise ValueError('expected tensor metadata')
    return math.prod(x['shape'])


def first_tensor(x):
    if tensor(x):return x
    if isinstance(x,(list,tuple)):
        for value in x:
            found=first_tensor(value)
            if found is not None:return found
    if isinstance(x,dict):
        for value in x.values():
            found=first_tensor(value)
            if found is not None:return found
    return None


MEMORY={
 'alias','detach','detach_','view','_unsafe_view','_reshape_alias','reshape','as_strided',
 't','transpose','permute','slice','select','unsqueeze','squeeze','expand','expand_as',
 'split','split_with_sizes','unbind','cat','stack','clone','contiguous','copy_',
 '_to_copy','to','empty','empty_like','empty_strided','new_empty','new_empty_strided',
 'zeros','zeros_like','ones','ones_like','full','full_like','fill_','zero_',
 'lift_fresh','lift_fresh_copy','scalar_tensor','gather','index','index_put_',
 '_index_put_impl_','index_select','masked_fill','masked_fill_','where','constant_pad_nd',
 'repeat','unfold','set_','resize_','_local_scalar_dense','record_stream','is_pinned',
 'pad','meshgrid','flatten','unflatten','chunk','promote_types','result_type','is_nonzero','item',
 '_pin_memory','_has_same_storage_numel','_assert_async',
}
COMPARISON={
 'eq','ne','lt','le','gt','ge','isfinite','isinf','isnan','all','any','bitwise_and',
 'bitwise_not','bitwise_or','__and__','__or__','logical_and','logical_not','logical_or',
 'nonzero','topk','sort','max','min','amax','amin','maximum','minimum','clamp','clamp_',
 'clamp_min','clamp_min_','clamp_max','clamp_max_','relu','relu_',
 'max_pool2d_with_indices','max_pool2d','nan_to_num','nan_to_num_',
}


def softmax_flops(elements,rows):
    # subtract max, exp, row sum, divide; max comparisons excluded.
    return 4*elements-rows


def count_signature(name,signature):
    """Return a disjoint category breakdown; unrecognized operations raise."""
    op=name.split('.')[1]
    a=signature['args'];kw=signature['kwargs'];out=signature['out']
    output=first_tensor(out)
    n=numel(output) if output is not None else 0
    if op in MEMORY:return {'excluded_memory':0}
    if op in COMPARISON:return {'excluded_comparison_selection':0}
    if op in ('upsample_nearest2d','upsample_nearest1d','upsample_nearest3d'):
        return {'excluded_nearest_copy':0}
    if op in ('dropout','dropout_','native_dropout'):
        assert (len(a)>2 and a[2] is False) or (len(a)>1 and a[1]==0), 'training dropout unsupported'
        return {'excluded_eval_identity':0}
    if op in ('convolution','_convolution'):
        assert not a[6], 'transposed convolution not in current inference graph'
        w=a[1]['shape']
        result={'conv_mac2':n*math.prod(w[1:])*2}
        if a[2] is not None: result['bias_and_scale']=n
        return result
    if op=='conv2d':
        w=a[1]['shape'];result={'conv_mac2':2*n*math.prod(w[1:])}
        if len(a)>2 and a[2] is not None:result['bias_and_scale']=n
        return result
    if op in ('linear','matmul'):
        left,right=a[:2]
        k=left['shape'][-1]
        assert k==right['shape'][-1 if op=='linear' else -2 if len(right['shape'])>1 else 0]
        result={'matrix_mac2':2*n*k}
        if op=='linear' and len(a)>2 and a[2] is not None:result['bias_and_scale']=n
        return result
    if op in ('mm','bmm','addmm','baddbmm','mv','addmv','addmv_','dot'):
        fused=op in ('addmm','baddbmm','addmv','addmv_')
        left,right=(a[1],a[2]) if fused else (a[0],a[1])
        k=left['shape'][-1]
        result={'matrix_mac2':2*n*k}
        if fused:
            alpha=kw.get('alpha',1);beta=kw.get('beta',1)
            extra=n*(int(alpha!=1)+int(beta!=0)+int(beta not in (0,1)))
            if extra:result['bias_and_scale']=extra
        return result
    if op in ('scaled_dot_product_attention','_scaled_dot_product_efficient_attention','_scaled_dot_product_flash_attention',
              '_scaled_dot_product_flash_attention_for_cpu','_scaled_dot_product_cudnn_attention'):
        q,k,v=[x['shape'] for x in a[:3]]
        assert len(q)==len(k)==len(v)==4
        batch,heads,qlen,dim=q
        assert k[:2]==v[:2]==q[:2] and k[-1]==dim and k[-2]==v[-2]
        klen=k[-2];vdim=v[-1];scores=batch*heads*qlen*klen;rows=batch*heads*qlen
        efficient=op=='_scaled_dot_product_efficient_attention'
        cudnn=op=='_scaled_dot_product_cudnn_attention'
        composite=op=='scaled_dot_product_attention'
        dropout_index=5 if efficient or cudnn else 4 if composite else 3
        causal_index=6 if efficient or cudnn else 5 if composite else 4
        dropout=a[dropout_index] if len(a)>dropout_index else kw.get('dropout_p',0)
        causal=a[causal_index] if len(a)>causal_index else kw.get('is_causal',False)
        assert dropout==0 and not causal, 'only non-causal eval attention is covered'
        bias=a[3] if (efficient or cudnn or composite) and len(a)>3 else None
        return {'attention_mac2':2*scores*(dim+vdim),
                'attention_scale_softmax_mask':scores+softmax_flops(scores,rows)+(scores if tensor(bias) else 0)}
    if op in ('grid_sampler_2d','grid_sampler'):
        assert a[2]==0 and a[3]==0,'only bilinear zero-padding is covered'
        b,c,_,_=a[0]['shape'];grid=a[1]['shape']
        assert len(grid)==4 and grid[0]==b and grid[-1]==2
        points=b*grid[1]*grid[2]
        # 4 dense contributions per output, MAC=2. Shared per-grid-point:
        # unnormalize x/y (3 each if aligned, 4 each otherwise), 8 weight
        # subtractions +4 weight multiplies. Floors/indices excluded.
        return {'bilinear_sample_mac2':8*n,'bilinear_coordinates_weights':points*(12+(6 if a[4] else 8))}
    if op in ('_softmax','softmax','_log_softmax','log_softmax'):
        size=a[0]['shape'][a[1]];rows=numel(a[0])//size
        return {'normalization_activation':softmax_flops(n,rows)+(n if 'log' in op else 0)}
    if op in ('native_layer_norm','layer_norm'):
        count=numel(a[0]);width=math.prod(a[1]);rows=count//width
        # mean: width ops; centered variance: width subtract+square plus
        # width ops mean. eps+rsqrt:2/row; normalize:2/element.
        # affine multiply/add each if present. Dense two-pass convention.
        affine=int(a[2] is not None)+int(a[3] is not None)
        return {'normalization_activation':(6+affine)*count+2*rows}
    if op in ('batch_norm','native_batch_norm','_native_batch_norm_legit','_native_batch_norm_legit_no_training','cudnn_batch_norm'):
        # All current graphs are eval. Count normalized affine expression;
        # not a claim about kernel precomputation or hardware instruction count.
        if op=='_native_batch_norm_legit_no_training':training=False
        elif op=='cudnn_batch_norm':training=a[5]
        else:training=a[5]
        assert training is False
        channels=a[0]['shape'][1];count=numel(a[0])
        affine=int(a[1] is not None)+int(a[2] is not None)
        return {'normalization_activation':(2+affine)*count+2*channels}
    if op in ('add','add_','sub','sub_','rsub','mul','mul_','div','div_','true_divide',
              'pow','neg','neg_','abs','abs_','reciprocal','sqrt','rsqrt','exp','log','sin','cos','tanh','erf'):
        if not floating(output):return {'excluded_integer_arithmetic':0}
        factor=1
        if op in ('add','add_','sub','sub_','rsub') and kw.get('alpha',a[2] if len(a)>2 else 1)!=1:factor+=1
        if op=='div' and kw.get('rounding_mode') is not None:raise ValueError('rounded floating division not covered')
        return {'elementwise_arithmetic':factor*n}
    if op in ('sigmoid','sigmoid_','silu','silu_','gelu'):
        factor={'sigmoid':4,'sigmoid_':4,'silu':5,'silu_':5,'gelu':5}[op]
        if op=='gelu':assert kw.get('approximate','none')=='none'
        return {'normalization_activation':factor*n}
    if op in ('sum','mean'):
        if not floating(output):return {'excluded_integer_arithmetic':0}
        return {'reductions':max(0,numel(a[0])-n)+(n if op=='mean' else 0)}
    if op=='cumsum':
        if not floating(output):return {'excluded_integer_arithmetic':0}
        rows=n//a[0]['shape'][a[1]]
        return {'reductions':n-rows}
    if op in ('arange','linspace'):
        if not floating(output):return {'excluded_integer_arithmetic':0}
        # Dense coordinate construction: start + index*step; linspace
        # step includes one subtraction and one division, once per call.
        return {'coordinate_construction':2*n+(2 if op=='linspace' and n>1 else 0)}
    if op in ('adaptive_avg_pool2d','_adaptive_avg_pool2d'):
        inp=a[0]['shape'];target=output['shape'];h,w=inp[-2:];oh,ow=target[-2:]
        work=0
        for iy in range(oh):
            kh=math.ceil((iy+1)*h/oh)-math.floor(iy*h/oh)
            for ix in range(ow):
                kwidth=math.ceil((ix+1)*w/ow)-math.floor(ix*w/ow)
                work+=kh*kwidth # (k-1) adds + one divide
        return {'reductions':math.prod(inp[:-2])*work}
    raise ValueError('uncounted operator: '+name)


def count_arm(arm):
    totals=defaultdict(int);details={};unsupported={}
    for name,op in arm['ops'].items():
        categories=defaultdict(int);errors=[]
        assert sum(op['signatures'].values())==op['calls']
        for encoded,calls in op['signatures'].items():
            try:cost=count_signature(name,json.loads(encoded))
            except (AssertionError,ValueError,IndexError,KeyError,TypeError) as error:
                errors.append({'reason':str(error),'signature':json.loads(encoded),'calls':calls});continue
            for category,count in cost.items():
                assert isinstance(count,int) and count>=0
                categories[category]+=count*calls
        if errors:unsupported[name]=errors
        details[name]={'calls':op['calls'],'categories':dict(categories),'flops':sum(categories.values())}
        for category,count in categories.items():totals[category]+=count
    major=sum(totals[k] for k in ('conv_mac2','matrix_mac2','attention_mac2'))
    official=arm['official_major_flops']
    packets=arm.get('official_by_op',{})
    registry_subset=sum(sum(value for key,value in detail['categories'].items()
                            if key in ('conv_mac2','matrix_mac2','attention_mac2'))
                        for name,detail in details.items() if '.'.join(name.split('.')[:2]) in packets)
    return {'status':'covered' if not unsupported else 'incomplete','convention':CONVENTION,
        'total_flops':sum(totals.values()) if not unsupported else None,
        'gflops':sum(totals.values())/1e9 if not unsupported else None,
        'categories':dict(totals),'ops':details,'unsupported':unsupported,
        'major_arithmetic_flops':major,'official_major_flops':official,
        'official_registry_subset_flops':registry_subset,
        'official_major_match':registry_subset==official,'operator_types':len(details),
        'operator_calls':sum(d['calls'] for d in details.values())}


def main():
    source=Path(sys.argv[1]);dest=Path(sys.argv[2])
    inventory=json.loads(source.read_text(encoding='utf-8'))
    report={'status':'pending','convention':CONVENTION,'protocol':inventory['protocol'],'arms':{}}
    for name,arm in inventory['arms'].items():
        primary=count_arm(arm)
        if 'no_grad_ops' in arm:
            lowered=count_arm({'ops':arm['no_grad_ops'],'official_major_flops':arm['no_grad_official_major_flops'],
                               'official_by_op':arm['no_grad_official_by_op']})
            primary['no_grad_crosscheck']=lowered
            primary['composite_lowered_major_match']=primary['major_arithmetic_flops']==lowered['major_arithmetic_flops']
            primary['output_max_abs_errors']=arm['inference_no_grad_output_max_abs_errors']
            primary['lowered_extra_scalar_ops']=(lowered['total_flops']-primary['total_flops']) if lowered['status']==primary['status']=='covered' else None
            # ATen decomposes isfinite into abs + comparisons under no_grad.
            # The declared predicate exclusion applies to this inner abs too.
            # Explain the exact discrepancy rather than allowing a tolerance.
            predicate_abs=sum(numel(json.loads(encoded)['args'][0])*calls for encoded,calls in
                              arm['ops'].get('aten.isfinite.default',{}).get('signatures',{}).items())
            primary['isfinite_decomposition_extra_abs_flops']=predicate_abs
            primary['composite_lowered_total_match_after_predicate_normalization']=primary['lowered_extra_scalar_ops']==predicate_abs
        report['arms'][name]=primary
    complete=all(a['status']=='covered' and a['official_major_match'] and
        a.get('composite_lowered_major_match',False) and
        a.get('composite_lowered_total_match_after_predicate_normalization',False) and
        a['no_grad_crosscheck']['status']=='covered' and a['no_grad_crosscheck']['official_major_match']
        for a in report['arms'].values())
    report['status']='complete_under_declared_convention' if complete else 'incomplete'
    dest.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({name:{'gflops':a['gflops'],'major_match':a['official_major_match'],
        'unsupported':list(a['unsupported'])} for name,a in report['arms'].items()},indent=2))
    if not complete:raise SystemExit(2)


if __name__=='__main__':main()
