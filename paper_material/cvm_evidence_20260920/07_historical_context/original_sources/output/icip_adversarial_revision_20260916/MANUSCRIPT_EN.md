# Local Visual Refinement for Distributional UAV Object Detection

## ABSTRACT

Small objects in UAV imagery are sensitive to boundary errors, making local visual evidence important for precise detection. We introduce a local visual expert that revisits predicted box neighborhoods in a distributional RT-DETR detector. Built on the boundary representation of D-FINE, the expert samples multiscale features around each box and predicts residual updates to classification and edge distributions. Its directly supervised predictions also provide localization targets for the decoder, selected through matching, boundary-support, and quality checks. A shared P3 refinement branch supplies features to both prediction paths. On converted-label VisDrone, the complete system achieves 30.109 validation AP and 23.604 test AP, improving test AP over the stock RT-DETR-L baseline by 5.861 points. A matched validation comparison shows a 0.832-point benefit from shared P3 refinement within the expert-equipped detector. Full reaches 74.129 images/s in a fixed-input FP32 benchmark at 640×640 on RTX 4090 with batch eight.

Index Terms — UAV imagery, object detection, boundary distributions, local visual refinement, localization distillation

## 1 INTRODUCTION

Accurately locating a small object requires more than identifying its presence. In UAV imagery, a displacement of only a few pixels can change a box's overlap with the target substantially. VisDrone [1] combines this sensitivity with crowded objects, occlusion, and extensive background. Spatial evidence near a predicted boundary is therefore useful for deciding how a localization hypothesis should be refined.

Existing aerial detectors introduce additional visual information at different stages. Slicing Aided Hyper Inference (SAHI) [2] detects objects in resized image patches. LASOD-YOLO [3] combines context modeling with detail-preserving feature fusion, while weather-aware drone-view detection [4] uses environmental context. These approaches motivate a complementary question: once a detector has estimated an object's location, how can it revisit that neighborhood to improve the prediction?

DETR [5] formulates detection as set prediction, and RT-DETR [6] combines efficient feature encoding with query-based decoding. D-FINE [7] extends localization with discrete edge distributions that are refined across decoder layers. An edge distribution represents candidate boundary positions; local visual features provide evidence for choosing among them. We connect these sources of information after base decoding. A visual expert samples features around the predicted box and uses them to update the edge distributions and class logits.

The refined prediction has a second role during training: it can supervise the base decoder. That role requires selection. A shared query index need not correspond to the same object at every decoder layer, and a locally refined boundary may still be worse than the student's estimate. We therefore transfer localization targets only after checking matched-object identity, distribution support, edge quality, and the geometry of the proposed edge combination. Ground-truth detection losses directly train the expert; its detached distributions supervise the decoder. Shared P3 refinement supplies a common feature improvement to both paths.

Our contribution is the combination of box-conditioned visual refinement with selective distributional supervision inside a detector. We specify how the expert obtains local evidence, produces residual predictions, and returns selected localization information to the decoder. VisDrone experiments evaluate the complete system against the stock RT-DETR-L reference, examine component choices on validation data, and measure the computational cost. A matched expert-equipped comparison provides the most direct evidence for the shared P3 design.

## 2 RELATED WORK

**Visual context for aerial detection.** SAHI [2] increases the relative size of small objects through image slicing; LASOD-YOLO [3] and weather-aware detection [4] introduce feature and environmental context. RemDet [8] revisits feature and downsampling design, while NRQO [9] addresses feature-fusion noise and query quality. Our refinement operates on local samples from the existing feature pyramid after the base decoder has predicted boxes.

**Localization refinement and distillation.** BorderDet [10] uses border features for localization, and Cascade-DETR [11] restricts decoder attention using previous box predictions. We build on this broader use of object-local evidence, with an additional expert that predicts residual edge distributions and supplies localization targets. D-FINE [7] provides the adopted distribution representation; localization distillation [12] transfers distributional knowledge. DETRDistill [13] explicitly addresses teacher–student prediction correspondence through Hungarian matching. Here, supervision is selected among same-query predictions that share a matched object, then filtered by edge and decoded-box quality. SO-DETR [14] and Dome-DETR [15] further motivate feature and query adaptation for small or tiny objects. Our focus is the connection between local visual refinement and selective supervision within one detector.


## 3 METHOD

### 3.1 Distributional detection backbone

We build on Ultralytics RT-DETR-L with six decoder layers and 300 ordinary queries. For a query, layer l predicts a residual in four edge-distribution logits, with 33 bins per edge. Following D-FINE [7], the logits accumulate across layers and the distribution expectation gives a continuous edge distance:

$$ z_l=\sum_{t=0}^{l}\Delta z_t,\quad p_{l,k}=\operatorname{softmax}(z_l)_k,\quad d_l=\sum_{k=0}^{32}p_{l,k}W_k. \tag{1} $$

The fixed support uses reg_max=32, reg_scale=4, and up=0.5. Let a be the positive fifteenth root of 3; the entries are [−4, 1−a¹⁵, …, 1−a, 0, a−1, …, a¹⁵−1, 4]. We use the incoming reference boxes rather than additional preliminary-box predictions and disable distribution feedback. The base detector uses P3, P4, and P5; P2 is used only by the local expert. Figure 1 shows the prediction and supervision paths.

![Figure 1](figures/architecture.png)

Figure 1. Local visual refinement and supervision. The base decoder receives enhanced P3, P4, and P5. P2, enhanced P3, and P4 supply the expert. P4 construction bypasses P3 refinement. Solid arrows denote prediction; dashed arrows denote training. The expert produces the inference output and also supplies detached localization targets.

### 3.2 Box conditioned local visual expert

The expert revisits the final base box instead of introducing another image-level detection pass. Let its decoded center and size be ĉᵢ and v̂ᵢ. We define T={−0.5,−0.25,0,0.25,0.5}. For each radius r∈{0.4,0.6}, the normalized offsets are (−r,t), (r,t), (t,−r), and (t,r), for t∈T. The union of these two 20-point patterns and one center point gives 41 samples. Figure 2 shows the normalized pattern; the image coordinates are

$$ s_{i,k}=\operatorname{sg}(\hat c_i)+\omega_k\odot\operatorname{sg}(\hat v_i),\qquad \omega_k\in\Omega. \tag{2} $$

![Figure 2](figures/sampling.png)

Figure 2. Normalized sampling pattern around a predicted box. Two 20-point patterns at r=0.4 and r=0.6, together with one center point, yield 41 samples at each of three feature scales.

Here sg stops gradients through the sampling coordinates. Bilinear sampling on P2, enhanced P3, and P4 gives 123 local tokens per query. Invalid coordinates are masked. Each scale is projected to 256 channels and receives a position embedding derived from the sample coordinates and scale index.

The query is augmented with eight detached distribution statistics: the mean and entropy of each edge. The mean is computed in normalized, equally spaced bin-index coordinates and serves only as an input descriptor; geometric distances still use the nonuniform support in (1). The augmented query interacts with the local tokens through two attention blocks, each with eight heads and a feed-forward width of 1024. One query token is retained in the attention input even when every local sample is invalid.

Two zero-initialized output heads predict residuals for the class logits and the 132 boundary logits. Adding these residuals to the final base predictions initially preserves their outputs. The same geometric decoder converts the refined distributions to boxes. During training, expert predictions reuse the final base layer's query-to-ground-truth assignment and receive classification, L1, generalized-IoU, and fine-grained localization (FGL) losses. Ground-truth losses directly optimize the expert, whose detached distributions provide localization targets for the base decoder.

### 3.3 Selective localization supervision

Additional local features do not make every expert prediction a suitable target. We first retain only student–teacher pairs sharing the same image, query, and matched ground-truth object. This check is applied to all six base layers, including the last. For each eligible edge, the untruncated target distance must lie within the representable support [W₀,W₃₂].

Let ℓˢ and ℓᵀ be the student and expert edge losses obtained by interpolating the ground-truth distance between its two neighboring bins. With margin m=0.02 and scale τ=0.10, we compute a detached edge weight:

$$ a_e=\max(\operatorname{sg}(\ell^S_e-\ell^T_e)-m,0),\qquad r_e=\mathbf1_{\mathrm{support}}\frac{a_e}{a_e+\tau}. \tag{3} $$

A second check tests the joint geometry of the candidate edges. We form an effective teacher by replacing only edges with positive rₑ and retaining the other student edges. These mixed distributions are decoded with the same geometry function. A query contributes to localization distillation only if the mixed box has strictly higher IoU with the matched target than the student box. Thus, the IoU test evaluates the actual combination of edges proposed for transfer.

Let wₗᵢₑ be the surviving weight, Aₗ the positive-weight edges in layer l, and Λ the layers with nonempty Aₗ. The loss averages over active edges and then active layers:

$$ L_{\mathrm{KD}}=\frac1{|\Lambda|}\sum_{l\in\Lambda}\frac1{|A_l|}\sum_{(i,e)\in A_l}w_{l,i,e}\,D_{\mathrm{KL}}\!\left(p^T_{i,e}\Vert p^S_{l,i,e}\right). \tag{4} $$

An empty active set gives zero loss. The normalization uses the number of active edges, not the sum of their weights. The teacher distributions and all selection calculations are detached; gradients flow through the student distributions.

We apply localization distillation with weight 0.15 and no classification distillation. For completed epoch e, η(e) is zero through epoch 10, rises linearly to one at epoch 20, remains one through epoch 80, and decreases linearly to zero at epoch 100. With the base detection loss L_det, additional base FGL loss L_FGL, and directly supervised expert loss L_expert, the objective is

$$ L=L_{\mathrm{det}}+L_{\mathrm{FGL}}+L_{\mathrm{expert}}+0.15\eta(e)L_{\mathrm{KD}}. \tag{5} $$

The expert's own single-layer FGL has weight 0.15 and remains active throughout training. At inference, matching and distillation are absent, while local sampling and the expert heads remain active.

### 3.4 Shared features and supporting localization rules

We refine P3 with two local residual blocks followed by channel and spatial gates. Each block uses pointwise projections, GELU, and a depthwise 3×3 convolution; the channel gate uses pooled features and the spatial gate uses a 7×7 convolution of channel-mean and channel-maximum maps. Writing the resulting transform as R, the shared feature is

$$ \widetilde P_3=P_3+\gamma\bigl(R(P_3)-P_3\bigr),\qquad \gamma_{\mathrm{init}}=0. \tag{6} $$

Both the decoder and expert read this output. The downsampling branch that constructs P4 reads the original P3, so the refinement is confined to the P3 output rather than cascaded through every pyramid stage.

For geometric validity, let the reference center and size be c and (w,h), with u=(w,h)/4. Let d⁻ and d⁺ collect the left/top and right/bottom edge distances, respectively. The decoded center is ĉ=c+(d⁺−d⁻)⊙u/2, and the raw size is v=(4+d⁻+d⁺)⊙u. We constrain the size using δ=10⁻³ and machine precision ε:

$$ f=\max\{\delta\operatorname{sg}(u),8\epsilon\max(|\operatorname{sg}(\hat{c})|,1)\},\quad \hat{v}=\operatorname{sg}(\max(v,f))+v-\operatorname{sg}(v). \tag{7} $$

The forward size is lower-bounded, while the backward path uses an identity surrogate gradient. Decoding uses at least FP32 with finite inputs and positive reference sizes. The resulting projection maintains usable positive box extents.

Base FGL uses detached matching IoU as a quality weight. For eligible matches in the same image and layer, we shrink it toward the group mean: q′ᵢ=(1−αₗ)qᵢ+αₗq̄, with αₗ=0.25(1−l/5). Eligibility requires the left interpolation-bin index of all four edges to be strictly between 0 and 31. Singleton groups and ineligible matches retain their weights. The four edge losses are summed, normalized by the layer's matched-object count, and summed across layers with weight 0.15. Standard detection, auxiliary-layer, and original RT-DETR denoising losses are retained; no additional preliminary-box or denoising-FDR supervision is used. These rules define the distributional reference variant used below.

## 4 EXPERIMENTS

### 4.1 Experimental setup

We use VisDrone with 6,471 training, 548 validation, and 1,610 test images covering ten classes. Labels were converted through YOLO format and lack the complete original ignore-region information; the results describe this converted-label protocol. AP averages IoU thresholds from 0.50 to 0.95, while AP50 and AP75 use individual thresholds [16]. Values are percentages and differences are percentage points.

RT-DETR-L and Full share a nominal recipe: scratch training for 100 epochs at 640×640, MuSGD with initial learning rate 0.01, AMP, physical batch eight, nominal batch 64, and seed zero. Baseline resumed its own run, and source revisions differ; this is a system comparison including the adopted distributional backbone. Component analysis uses native validation-selected results.

Table 1 uses validation-selected checkpoints, shared converted annotations, and native RTDETRValidator: 640×640, FP32, batch eight, confidence 0.001, max_det=300, without test-time augmentation or extra NMS. Baseline's selected epoch is also its final epoch. These evaluations were available during earlier development; test is not an untouched blind set.

External D-FINE-L comparison uses a common pipeline: PIL bilinear stretching to 640×640, RGB/255, FP32, batch one, confidence 0.001, at most 300 predictions, and no test-time augmentation or extra NMS. Original-coordinate predictions enter COCOeval 2.0.11 with maxDet=300. Native and common results are reported separately.

### 4.2 Complete system and literature comparisons

Against stock RT-DETR-L (Table 1), Full improves AP from 17.743 to 23.604, with gains of 8.987 AP50 and 5.981 AP75. Section 4.3 separately examines components on validation data.

Table 1. Complete-system VisDrone test comparison using the shared native evaluator at 640 and validation-selected checkpoints.

| Model | AP | AP50 | AP75 |
|---|---:|---:|---:|
| RT-DETR-L | 17.743 | 32.254 | 17.565 |
| Full | 23.604 | 41.241 | 23.546 |

Table 2 compares Full with D-FINE-L under common evaluation. D-FINE-L has 31.146M parameters and uses 100-epoch scratch training with AdamW (learning rate 0.00025), FP32, batch four without accumulation, 480–800 multiscale augmentation, and stage-best checkpoint restoration. These system results reflect different training recipes. Final checkpoints are primary; each model's native validation-selected best is also reported.

Table 2. External VisDrone test comparison using the common evaluator and different training recipes. Final is primary; best is native validation-selected.

| Model and checkpoint | AP | AP50 | AP75 | APs |
|---|---:|---:|---:|---:|
| D-FINE-L final | 22.554 | 38.656 | 22.720 | 13.338 |
| Full final | 24.133 | 41.885 | 24.044 | 14.575 |
| D-FINE-L best | 22.679 | 38.940 | 22.713 | 13.478 |
| Full best | 24.229 | 42.009 | 24.208 | 14.618 |

Full exceeds D-FINE-L by 1.579 AP and 1.237 APs at the final endpoint; the advantage also appears at the validation-selected endpoint under these recipes.

Table 3 adds published validation context: RemDet-L [8] has similar parameter count, while BDNet [17] reports higher AP with fewer parameters. All rows report 640 input without pretraining; training length, preprocessing, label handling, and model selection differ.

Table 3. Published VisDrone validation results and our native result. Training and evaluation recipes differ across methods.

| Method | Epochs | Params M | AP | AP50 |
|---|---:|---:|---:|---:|
| RemDet-L [8] | 300 | 35.3 | 29.3 | 47.4 |
| BDNet [17] | 300 | 2.59 | 31.2 | 50.5 |
| Full | 100 | 35.244 | 30.109 | 49.890 |

### 4.3 Validation component analysis

In Table 4, G is the distributional reference with Section 3.4's localization rules; B combines the expert, direct supervision, and selective localization distillation; F is shared P3 refinement. Full is G+B+F. B and its supervision are evaluated jointly.

Table 4. Native validation and batch-eight inference efficiency at 640×640 on RTX 4090 in FP32. Times cover the full predict call; GFLOPs are per image. Amortized time equals batch time/8 and is not single-request latency. Throughput equals 8000/batch median in milliseconds.

| Variant | Val AP | AP50 | Params M | GFLOPs | Batch ms | Amortized ms/img | Images/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 21.911 | 38.663 | 32.827 | 105.597 | 59.559 | 7.445 | 134.321 |
| G | 29.620 | 49.382 | 33.157 | 105.804 | 66.200 | 8.275 | 120.846 |
| G+F | 29.773 | 49.548 | 33.458 | 109.280 | 69.044 | 8.630 | 115.868 |
| G+B | 29.277 | 48.783 | 34.942 | 130.575 | 104.897 | 13.112 | 76.266 |
| Full | 30.109 | 49.890 | 35.244 | 134.051 | 107.920 | 13.490 | 74.129 |

Full achieves the highest validation AP, 0.489 points above G. In these configurations, adding B without shared P3 refinement does not improve validation AP: G+B is below G.

G+B and Full are the most directly matched pair: recorded training settings, shared source files, and shared initialization tensors agree, with additional state in the zero-initialized F branch. Adding F raises AP from 29.277 to 30.109 (+0.832), supporting shared P3 refinement within the expert-equipped configuration. Other historical configurations have less tightly controlled provenance.

### 4.4 Computational cost and scope

Measurements use PyTorch 2.5.1+cu121 and Ultralytics 8.4.90 on RTX 4090, eight CPU threads, with TF32 and cuDNN benchmarking disabled. Each variant uses batch eight with fixed random inputs, 100 warmup batches, and 300 CUDA-synchronized timed predict calls. Timing includes preprocessing, execution, postprocessing, and the lightweight expert-checking hook, but excludes disk I/O. We report the median batch time and its corresponding throughput. GFLOPs count two operations per multiply–accumulate for one image; parameters cover the complete unfused model.

Full uses 35.244M parameters and 134.051 GFLOPs. At batch eight, it processes 74.129 images/s with 107.920 ms per batch, or 13.490 ms amortized per image. The amortized value measures batching efficiency, not single-request response latency. These are fixed-input throughput measurements.

Relative to G, Full adds 2.087M parameters and 28.247 GFLOPs, while batch time rises from 66.200 to 107.920 ms. B adds 24.771 GFLOPs and F adds 3.476; the expert accounts for most added computation.

Component-level conclusions are based on validation comparisons. The study uses one dataset and one seed, and evaluates the expert and its distillation jointly, without isolating each selection rule.

## 5 CONCLUSION

We presented a box-conditioned expert that uses local visual evidence to refine edge distributions and selectively supervise a UAV detector. The complete system improves over stock RT-DETR-L under the reported test protocol; matched validation evidence supports shared P3 refinement within the expert-equipped configuration. Local evidence thus informs both distributional prediction and supervision. Full processes 74.129 images/s in the fixed-input FP32 benchmark at batch eight, with expert cost the main opportunity for further efficiency improvements.

## REFERENCES

[1] P. Zhu, L. Wen, X. Bian, et al., “Vision Meets Drones: A Challenge,” arXiv:1804.07437, 2018.

[2] F. C. Akyon, S. O. Altinuc, and A. Temizel, “Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection,” in ICIP, 2022, pp. 966–970, doi: 10.1109/ICIP46576.2022.9897990.

[3] Z. Wang and J. X. Huang, “LASOD-YOLO: A Lightweight Global Context Modeling for Aerial Small-Object Detection,” in ICIP, 2026, pp. 1–6, doi: 10.1109/ICIP61757.2026.11630018.

[4] H. Kim, D. Lee, S. Park, and Y. M. Ro, “Weather-Aware Drone-View Object Detection via Environmental Context Understanding,” in ICIP, 2024, pp. 549–555, doi: 10.1109/ICIP51287.2024.10647388.

[5] N. Carion, F. Massa, G. Synnaeve, et al., “End-to-End Object Detection with Transformers,” in ECCV, 2020.

[6] Y. Zhao, W. Lv, S. Xu, et al., “DETRs Beat YOLOs on Real-time Object Detection,” in CVPR, 2024, pp. 16965–16974.

[7] Y. Peng, H. Li, P. Wu, et al., “D-FINE: Redefine Regression Task of DETRs as Fine-grained Distribution Refinement,” in ICLR, 2025.

[8] C. Li, R. Zhao, Z. Wang, et al., “RemDet: Rethinking Efficient Model Design for UAV Object Detection,” in AAAI, 2025, pp. 4643–4651, doi: 10.1609/aaai.v39i5.32490.

[9] X. Fang, J. Cai, H. Liu, et al., “Revisiting DETR for Small Object Detection via Noise-Resilient Query Optimization,” in ICME, 2025.

[10] H. Qiu, Y. Ma, Z. Li, et al., “BorderDet: Border Feature for Dense Object Detection,” in ECCV, 2020.

[11] M. Ye, L. Ke, S. Li, et al., “Cascade-DETR: Delving into High-Quality Universal Object Detection,” in ICCV, 2023, pp. 6704–6714.

[12] Z. Zheng, R. Ye, P. Wang, et al., “Localization Distillation for Dense Object Detection,” in CVPR, 2022, pp. 9407–9416.

[13] J. Chang, S. Wang, H.-M. Xu, et al., “DETRDistill: A Universal Knowledge Distillation Framework for DETR-families,” in ICCV, 2023, pp. 6898–6908.

[14] H. Zhang, H. Zhang, A. Mei, et al., “SO-DETR: Leveraging Dual-Domain Features and Knowledge Distillation for Small Object Detection,” in IJCNN, 2025, doi: 10.1109/IJCNN64981.2025.11229240.

[15] Z. Hu, P. Wu, J. Chen, et al., “Dome-DETR: DETR with Density-Oriented Feature-Query Manipulation for Efficient Tiny Object Detection,” in ACM Multimedia, 2025, doi: 10.1145/3746027.3754861.

[16] T.-Y. Lin, M. Maire, S. Belongie, et al., “Microsoft COCO: Common Objects in Context,” in ECCV, 2014.

[17] W. Guan, C. Lin, S. Huang, et al., “BDNet:Bio-Inspired Dual-Backbone Small Object Detection Network,” in CVPR, 2026.
