"""Exact arithmetic formula checks and fail-closed coverage contracts; no GPU."""
import json
from pathlib import Path
import pytest
from scripts.count_inference_flops import count_signature,count_arm,softmax_flops


def T(*shape,dtype='torch.float32'):return {'shape':list(shape),'dtype':dtype}
def S(args,out,**kwargs):return {'args':args,'kwargs':kwargs,'out':out}


@pytest.mark.parametrize('groups,channels,kernel',[(1,3,3),(8,8,3),(2,8,1)])
def test_grouped_convolution_and_bias(groups,channels,kernel):
    out=T(2,8,5,5);weight=T(8,channels//groups,kernel,kernel)
    expected={'conv_mac2':2*2*8*5*5*(channels//groups)*kernel**2,'bias_and_scale':2*8*5*5}
    assert count_signature('aten.conv2d.default',S([T(2,channels,5,5),weight,T(8)],out))==expected
    args=[T(2,channels,5,5),weight,T(8),[1,1],[1,1],[1,1],False,[0,0],groups]
    assert count_signature('aten.convolution.default',S(args,out))==expected


def test_linear_equals_addmm_including_bias():
    expected={'matrix_mac2':2*6*5*4,'bias_and_scale':6*5}
    assert count_signature('aten.linear.default',S([T(2,3,4),T(5,4),T(5)],T(2,3,5)))==expected
    assert count_signature('aten.addmm.default',S([T(5),T(6,4),T(4,5)],T(6,5)))==expected


def test_matmul_broadcast_and_alpha_beta():
    assert count_signature('aten.matmul.default',S([T(2,3,4),T(4,5)],T(2,3,5)))['matrix_mac2']==240
    row=count_signature('aten.addmm.default',S([T(5),T(6,4),T(4,5)],T(6,5),alpha=2,beta=2))
    assert row['bias_and_scale']==90


def test_composite_and_fused_attention_match():
    q,k,v=T(2,4,3,8),T(2,4,5,8),T(2,4,5,6);bias=T(2,4,3,5)
    composite=count_signature('aten.scaled_dot_product_attention.default',S([q,k,v,bias],T(2,4,3,6)))
    fused=count_signature('aten._scaled_dot_product_efficient_attention.default',S([q,k,v,bias,False,0.,False],[T(2,4,3,6),T(2,4,3)]))
    assert composite==fused
    assert composite['attention_mac2']==2*(2*4*3*5)*(8+6)
    assert composite['attention_scale_softmax_mask']==120+(4*120-24)+120
    assert count_signature('aten._scaled_dot_product_efficient_attention.default',S([q,k,v,bias,False],[T(2,4,3,6)]))==composite


def test_bilinear_counts_channel_work_and_shared_coordinates_once():
    args=[T(2,8,10,10),T(2,3,4,2),0,0,False]
    expected={'bilinear_sample_mac2':8*2*8*3*4,'bilinear_coordinates_weights':20*2*3*4}
    assert count_signature('aten.grid_sampler.default',S(args,T(2,8,3,4)))==expected
    assert count_signature('aten.grid_sampler_2d.default',S(args,T(2,8,3,4)))==expected
    args[-1]=True
    assert count_signature('aten.grid_sampler.default',S(args,T(2,8,3,4)))['bilinear_coordinates_weights']==18*24


def test_layernorm_mean_sum_and_softmax():
    assert count_signature('aten.layer_norm.default',S([T(2,3,4),[4],T(4),T(4),1e-5],T(2,3,4)))['normalization_activation']==8*24+2*6
    assert count_signature('aten.mean.dim',S([T(2,3,4),[-1],False],T(2,3)))['reductions']==24
    assert count_signature('aten.sum.dim_IntList',S([T(2,3,4),[-1],False],T(2,3)))['reductions']==18
    assert count_signature('aten.softmax.int',S([T(2,3,4),-1],T(2,3,4)))['normalization_activation']==softmax_flops(24,6)


@pytest.mark.parametrize('op,factor',[('gelu',5),('silu_',5),('sigmoid',4),('log',1),('pow',1)])
def test_activation_convention(op,factor):
    cost=count_signature('aten.'+op+'.default',S([T(2,3)],T(2,3)))
    assert sum(cost.values())==6*factor


def test_data_and_integer_ops_are_explicitly_excluded():
    assert count_signature('aten.cat.default',S([[T(2),T(2)],0],T(4)))=={'excluded_memory':0}
    assert count_signature('aten.add.Tensor',S([T(2,dtype='torch.int64'),1],T(2,dtype='torch.int64')))=={'excluded_integer_arithmetic':0}
    assert count_signature('aten.topk.default',S([T(100),5],[T(5),T(5,dtype='torch.int64')]))=={'excluded_comparison_selection':0}


def test_unknown_operation_does_not_become_zero():
    with pytest.raises(ValueError,match='uncounted'):
        count_signature('aten.unknown.default',S([T(2)],T(2)))
    signature=json.dumps(S([T(2)],T(2)))
    report=count_arm({'ops':{'aten.unknown.default':{'calls':1,'signatures':{signature:1}}},'official_major_flops':0})
    assert report['status']=='incomplete' and report['total_flops'] is None


def test_unsupported_grid_or_attention_configuration_fails_closed():
    with pytest.raises(AssertionError):
        count_signature('aten.grid_sampler.default',S([T(1,2,4,4),T(1,2,2,2),2,0,False],T(1,2,2,2)))
    with pytest.raises(AssertionError):
        count_signature('aten.scaled_dot_product_attention.default',S([T(1,1,2,4)]*3+[None,.2,False],T(1,1,2,4)))


def test_real_five_arm_trace_coverage_and_independent_major_registry():
    root=Path(__file__).resolve().parents[1]
    base=root/'paper_material/evidence/audit_remediation_20260915/full_flops/v2'
    trace=json.loads((base/'inventory.json').read_text())
    totals={}
    for arm,data in trace['arms'].items():
        composite=count_arm(data)
        lowered=count_arm({'ops':data['no_grad_ops'],
            'official_major_flops':data['no_grad_official_major_flops'],
            'official_by_op':data['no_grad_official_by_op']})
        assert composite['status']==lowered['status']=='covered'
        assert composite['unsupported']==lowered['unsupported']=={}
        assert composite['official_major_match'] and lowered['official_major_match']
        assert composite['major_arithmetic_flops']==lowered['major_arithmetic_flops']
        predicate=sum(__import__('math').prod(json.loads(s)['args'][0]['shape'])*c
                      for s,c in data['ops'].get('aten.isfinite.default',{}).get('signatures',{}).items())
        assert composite['total_flops']==lowered['total_flops']-predicate
        assert max(data['inference_no_grad_output_max_abs_errors'])==0
        totals[arm]=composite['total_flops']
    assert totals['Full']-totals['G+B']==totals['G+F']-totals['G']
    assert totals['Full']==134051394487
