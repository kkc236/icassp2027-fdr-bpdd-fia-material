Title: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging for Lightweight Object Detection in Aerial Imagery

URL Source: http://xplorestaging.ieee.org/ielx8/6287639/11323511/11611188.pdf?arnumber=11611188

Published Time: Thu, 13 Aug 2026 19:04:24 GMT

Number of Pages: 16

Markdown Content:
> Received 3 June 2026, accepted 11 July 2026, date of publication 15 July 2026, date of current version 12 August 2026.
> Digital Object Identifier 10.1109/ACCESS.2026.3713646

# SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging for Lightweight Object Detection in Aerial Imagery 

SHUHANG TANG  1 AND ZHUO ZENG  2

> 1China Mobile IoT Company Ltd., Chongqing 401120, China
> 2College of Artificial Intelligence and Big Data, Chongqing Polytechnic University of Electronic Technology, Chongqing 401331, China

Corresponding author: Zhuo Zeng (zengzhuo@cqcet.edu.cn) This work was supported by the Science and Technology Research Program of Chongqing Municipal Education Commission under Grant KJQN202403121. 

ABSTRACT Lightweight object detection in aerial imagery is important for resource-constrained unmanned aerial vehicles (UAVs) and edge platforms used in traffic monitoring, aerial inspection, and surveillance. Under tight computational budgets below 15 giga floating-point operations (GFLOPs), aggressive simplification of the backbone–neck pipeline often weakens contextual modeling and cross-scale interaction, which is particularly detrimental in aerial scenes dominated by small and crowded objects. We present SC-D-FINE, a lightweight D-FINE-based Detection Transformer (DETR)-style detector for aerial imagery. The design centers on an SGMA–CaMPB encoder for early multi-scale enhancement, with a re-parameterizable DRC tail providing low-cost high-level context. In the encoder, SGMA injects adjacent-scale cues, whereas CaMPB performs compact feature alignment and bidirectional context fusion to reduce scale-induced noise. On VisDrone2019, SC-D-FINE-N reaches 25.7% Average Precision (AP) and 43.0% AP 50 (AP at an Intersection over Union threshold of 0.50), compared with 20.8% AP and 36.8% AP 50 for D-FINE-N. In the 14-GFLOPs regime, it remains 1.8 AP above the wider D-FINE-N-14G variant while using 30.1% fewer parameters. On UAVVaste and Vehicle Detection in Aerial Imagery (VEDAI), the same design yields AP gains of 6.4 and 8.4 points over D-FINE-N. Overall, these results suggest that the gains, driven mainly by the encoder changes and supported by the lightweight DRC tail, are not confined to VisDrone2019. 

INDEX TERMS DETR, edge deployment, lightweight object detector, multi-scale feature fusion, object detection, UAV imagery. 

I. INTRODUCTION 

The demand for real-time object detection in aerial imagery is increasing in edge and unmanned aerial vehicle (UAV) applications, including traffic monitoring, aerial inspection, and security surveillance. The You Only Look Once (YOLO) family remains widely adopted because of its mature ecosystem and favorable efficiency–accuracy balance [1]. In parallel, Transformer-based end-to-end detection has emerged as a competitive alternative [2]. Detection Trans-former (DETR) demonstrated that global context modeling and set prediction can eliminate hand-crafted components 

The associate editor coordinating the review of this manuscript and approving it for publication was Li Zhang  .

such as non-maximum suppression (NMS) and anchor boxes [3]. Real-Time Detection Transformer (RT-DETR) replaced the vanilla Transformer encoder with a more efficient hybrid encoder, making real-time DETR practi-cal [4]. RT-DETRv2 further refines deformable attention by allocating different numbers of sampling points to differ-ent feature scales for selective multi-scale extraction [5]. D-FINE improves bounding-box regression and introduces effective self-distillation to ease the optimization of fixed-coordinate regression and localization uncertainty [6]. DETR with Improved Matching (DEIM) further accelerates DETR convergence via dense one-to-one matching [7]. UAV and optical remote-sensing detection studies have repeatedly pointed to the same practical difficulties: small  

> VOLUME 14, 2026
> 2026 The Authors. This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/ 120435 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging

target size, dense layouts, viewpoint changes, and limited onboard computation [8], [9], [10], [11]. Recent UAV-oriented DETR/DEIM and RT-DETR variants likewise suggest that end-to-end detectors for aerial imagery often need UAV-specific changes around matching, decoder opti-mization, feature refinement, or multi-scale fusion [12], [13], [14], [15], [16]. These observations motivate the present focus on retaining early cross-scale interaction and feature alignment inside a compact DETR-style detector, rather than increasing the backbone or decoder depth. Despite this progress, many accuracy gains still depend on relaxed computation and memory budgets, which limits deployment on resource-constrained devices. Edge platforms often require models with only a few million parameters and computational costs well below tens of giga floating-point operations (GFLOPs). Under such limits, lightweight detectors for aerial imagery struggle in scenes dominated by small and medium objects, large scale variation, occlusion, and background clutter. Starting from D-FINE-N [6] and focusing on VisDrone2019 [17], two issues are especially apparent. First, early multi-scale interaction is often removed or simplified to save computation. Fusion is delayed to the neck or the detection head, leaving high-resolution early features largely isolated. Because small and dense objects are mainly encoded in shallow layers, the lack of early cross-scale guidance weakens feature selectivity and recall. Second, lightweight fusion is commonly implemented with simple top–down or bottom–up aggregation and little explicit channel alignment. Large gaps in spatial resolution and semantics then carry noise across scales, which hurts high Intersection over Union (IoU) localization and increases false positives. Heavier attention or extra Transformer layers could mitigate part of this problem, but they are difficult to justify under strict edge budgets (e.g., < 15 GFLOPs). At the other extreme, ultra-light alignment based only on 1 × 1 convolutions or residual links often lacks the context needed to separate small objects from clutter. To address these issues, we build SC-D-FINE on top of D-FINE. The central change is a SimFusion-guided Multi-Cue Adapter (SGMA)–Context-aware Multi-scale Progres-sive Channel Attention (PCA) Bridge (CaMPB) encoder that provides early cross-scale guidance and compact feature alignment. SGMA resamples adjacent pyramid features and feeds the resulting cues back to the fine-resolution stream, while CaMPB aligns cross-scale features before fusion and uses bidirectional context interaction to suppress responses caused by scale mismatch. In addition, a lightweight re-parameterizable Dilated Residual Context (DRC) stage is attached to the deepest HGNetv2 block to supplement high-level context at little deployment cost. Fig. 1 summarizes the AP–FPS trade-off on Vis-Drone2019. The SC-D-FINE variants remain near the upper-right region of the plot. In the 14-GFLOPs regime, the widened D-FINE-N-14G point moves upward relative to D-FINE-N, but SC-D-FINE-N still remains higher. SC-D-FINE-N also matches RT-DETRv4-S [18] in AP at much lower computation, while SC-D-FINE-S and SC-D-FINE-24G remain above representative YOLO and D-FINE baselines in similar compute ranges.  

> FIGURE 1. Average Precision (AP)–frames-per-second (FPS) trade-off on VisDrone2019. Bubble size denotes GFLOPs.

Fig. 2 contrasts D-FINE and SC-D-FINE on typical UAV scenes. In the baseline, early features receive limited cross-scale guidance and little explicit channel alignment. As a result, intermediate representations contain blurrier textures and less stable boundaries, which is particularly unfavorable for small objects. SC-D-FINE addresses these issues mainly through the SGMA–CaMPB encoder, while a lightweight DRC tail is added at the deepest backbone stage as a supporting context module. Relative to D-FINE, the resulting feature maps retain clearer local detail and more coherent textures. The dotted regions in Fig. 2 show the corresponding effect in the final detections, especially for small objects in crowded and partially occluded areas. The main contributions are as follows :

1) Early cross-scale cue injection through SGMA , which reuses adjacent pyramid features to strengthen the fine-resolution encoder stream. 2) A compact CaMPB bridge for feature alignment before fusion, reducing unstable responses introduced by large scale gaps. 3) A lightweight DRC tail added to the deepest HGNetv2 stage to provide a small context supplement at little deployment cost, complementing the encoder-side design. 

> II. METHOD
> A. OVERVIEW

This section describes SC-D-FINE and the components added to D-FINE. We first summarize the baseline pipeline and then describe the SGMA–CaMPB encoder together with the lightweight DRC tail attached to the deepest backbone stage.   

> 120436 VOLUME 14, 2026 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging
> FIGURE 2. D-FINE and SC-D-FINE on representative UAV scenes. Dotted boxes mark local differences.
> B. OVERALL ARCHITECTURE

We adopt D-FINE [6] as the baseline detector. D-FINE improves DETR localization and optimization through Fine-grained Distribution Refinement (FDR) and Global Optimal Localization Self-Distillation (GO-LSD). Its architecture combines an HGNetv2 backbone, a hybrid encoder with Transformer blocks and path aggregation feature pyramid network (PAFPN)-style fusion, and a decoder-based predic-tion head. Instead of regressing box coordinates directly, D-FINE refines per-edge probability distributions across decoder layers. This formulation eases optimization and improves localization, with little effect on inference cost. GO-LSD transfers localization cues from the last decoder layer to earlier ones during training. SC-D-FINE keeps this DETR-style pipeline. As shown in Fig. 3, the backbone follows the staged HGNetv2 design (Stem and Stages 1–4) and extracts compact multi-level features. A lightweight DRC block is attached to the deepest stage, where it serves as a low-overhead context supplement and can be re-parameterized into a single large-kernel operator at deployment. The hybrid encoder is then extended with SGMA and CaMPB. SGMA brings early cross-scale cues through its focus block and lightweight SimFusion, whereas CaMPB performs compact alignment and context-guided denoising before features are passed to the decoder. The decoder remains unchanged from D-FINE and iteratively predicts classes and boxes; GO-LSD is used during training only and does not alter inference. 

> C. A LIGHTWEIGHT DRC TAIL FOR HGNetv2

Although HGNetv2 offers a good efficiency–accuracy trade-off [6], its deepest feature can lose contextual range when the network is compressed aggressively. In crowded aerial scenes, this mainly weakens the coarse semantic anchor that is later passed to the encoder. Heavier attention blocks or extra Transformer layers could address part of this problem, but their cost is difficult to justify under the target budget (e.g., < 15 GFLOPs). We address this limitation by appending a Dilated Residual Context (DRC) stage to the HGNetv2 tail (Fig. 4). The backbone keeps the original stem and early stages unchanged and modifies only the final stage. This choice is made at the coarsest-resolution level ( P5), where a broader receptive field is relatively inexpensive and where a modest semantic improvement can still benefit the later encoder. A DRC block begins with a depthwise large-kernel convolution to keep the computational cost low [19]. Parallel dilated depthwise branches are then added to expand the effective receptive field [20]. Given an input feature x, the training-time output is 

y = BN 0(DWConv K (x)) +

> Nbr

∑

> i=1

BN i

(DWConv ki,ri (x)) , (1) where BN denotes batch normalization, DWConv K is a large-kernel depthwise convolution, DWConv ki,ri denotes depthwise convolutions with smaller kernels and different dilation rates, and Nbr is the number of dilated depthwise branches. The resulting branches cover several receptive-field ranges, which helps the backbone capture longer-range context without discarding the local cues needed to separate small objects from clutter. In the lightweight setting considered here, DRC is applied only at the deepest backbone stage and uses a large kernel    

> VOLUME 14, 2026 120437 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging
> FIGURE 3. Overall architecture of SC-D-FINE.
> FIGURE 4. HGNetv2 with the DRC tail.

K = 11. Following the default DilatedReparamConv configuration [21], we set Nbr = 5 with (ki, ri) ∈{(5 , 1) , (5 , 2) , (3 , 3) , (3 , 4) , (3 , 5) }. After training, DRC is re-parameterized for inference: BatchNorm parameters are folded into the convolution weights, dilated kernels are transformed into equivalent dense kernels, and all branches are merged into a single depthwise large-kernel operator. As a result, the deploy-time backbone remains close to the original HGNetv2 tail in latency and memory usage while retaining the contextual capacity learned during training [22]. 

D. SGMA–CAMPB ENCODER 

1) OVERALL STRUCTURE 

Feature pyramids and bidirectional path aggregation remain common choices for multi-scale fusion [23], [24], [25], but they are often simplified in lightweight DETR-style detectors to meet edge constraints. On UAV data, that simplification has two practical consequences. High-resolution early fea-tures receive too little semantic guidance, which weakens responses to small targets and lowers recall. In addition, plain top–down or bottom–up aggregation offers little explicit alignment, so large scale gaps introduce noisy or misplaced activations and hurt high-IoU localization. We therefore modify the hybrid encoder with two small modules. SGMA feeds cross-scale cues into the higher-resolution path early in the encoder, whereas CaMPB aligns features before fusion and suppresses misplaced responses during aggregation. The Transformer block is kept only on the deepest feature, where global context is least expensive. The detailed structures of SGMA and CaMPB are shown in Fig. 5 and Fig. 6, respectively. The encoder is organized in two steps: (i) focus →mix →

denoise, which injects early cross-scale guidance into the fine-resolution stream; and (ii) align →refocus →fuse, which corrects scale mismatch and produces the representations sent to the decoder. 

2) FEATURE DIFFUSION AND CONNECTION STRATEGY 

Let the backbone multi-scale features be ( P2, P3, P4, Pdrc 5 ). Features {P3, P4, Pdrc 5 } are first projected to a shared hidden width, while lightweight 1 × 1 projections inside the fusion modules handle any additional channel alignment. The coarsest feature is then enhanced by a Transformer to obtain a semantic anchor :

P5 = T

(

Pdrc 5

)

. (2)  

> 120438 VOLUME 14, 2026 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging

In Stage I (focus →mix →denoise), SGMA-Focus, imple-mented as multi-cue focusing (MCF), is applied around the mid-level P4 to concentrate multi-cue information, SGMA-Fusion (SimFusion) mixes information toward the P3 stream, and CaMPB-Fuse, implemented as context-guided fusion (CGF), stabilizes the output :

F(1) 4 = MCF( P5, P4, P3), (3) 

Fsf 3 = SimFusion( P2, P3, F(1) 4 ), (4) 

E3 = CGF( Fsf 3 , P3). (5) In Stage II (align →refocus →fuse), CaMPB-Align, imple-mented by a Multi-scale Progressive Channel Attention block (MultiScalePCA, denoted as MSPCA), aligns the Transformer-enhanced P5 with the P4-side representation, after which cues are refocused at P4 and the high-level output is consolidated :

A5 = MSPCA( P5, F(1) 4 ), (6) 

E4 = MCF( A5, F(1) 4 , E3), (7) 

E5 = CGF( A5, Down 3×3,s=2(E4)) . (8) The encoder outputs ( E3, E4, E5) are then aggregated and forwarded to the decoder. 

3) SGMA: SimFusion-GUIDED MULTI-CUE ADAPTER 

SGMA consists of two submodules: SGMA-Focus (MCF) and SGMA-Fusion (SimFusion). MCF first gathers cues from adjacent scales and produces a refined mid-level representation. SimFusion then transfers this information to the target pyramid level by resampling and 1 × 1 mixing. Fig. 5 shows the two SGMA components used for cue aggregation and scale transfer. 

a: SGMA-FOCUS (MCF) 

MCF (Fig. 5a) receives three adjacent-scale features and outputs a focused representation at the reference scale (P4). In the two-stage encoder, MCF is instantiated twice: (Xc, Xr , Xf ) = (P5, P4, P3) in Stage-I and ( Xc, Xr , Xf ) =

(A5, F(1) 4 , E3) in Stage-II. Let the reference input be Xr ∈

RB×C×H ×W ; then the coarse and fine inputs have spatial sizes ( H /2, W /2) and (2 H , 2W ), respectively. The coarse feature is first upsampled to the reference resolution, the fine feature is downsampled by a lightweight operator, and all branches are projected to a reduced channel width ( C′ = eC ). Following common multi-kernel context designs in remote-sensing and UAV detection, we fix e = 0.5 and use the odd-kernel set K = { 3, 5, 7, 9} in all experiments. These four kernels span several neighborhood sizes, from local detail to broader context :

Fc = Conv 1×1(↑ Xc), (9) 

Fr = Conv 1×1(Xr ), (10) 

Ff = ADown( Xf ), (11) where ( Xc, Xr , Xf ) denote the coarse/reference/fine inputs, ↑

denotes upsampling, and ADown is an efficient downsampler  

> FIGURE 5. Structure of SGMA.

that reduces aliasing while retaining local structures. The aligned cues are concatenated as 

X = Concat( Fc, Fr , Ff ), (12) and then aggregated with multi-kernel depthwise context :

O = X + ∑

> k∈K

DWConv k×k (X ), (13) followed by pointwise mixing :

H = PWConv( O),

FMCF = Conv 1×1(X + H ). (14) Here, PWConv denotes pointwise convolution.  

> VOLUME 14, 2026 120439 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging
> b: SGMA-FUSION (SimFusion)

After SGMA-Focus, SGMA-Fusion (Fig. 5b) transfers the focused feature to the target scale. It follows a simple align-then-fuse strategy: given three adjacent-scale features and a chosen reference resolution, SimFusion downsamples higher-resolution inputs by adaptive average pooling (AAP) and upsamples lower-resolution inputs by interpolation, followed by compact 1 ×1 convolutional mixing and optional Efficient Multi-Scale Attention (EMA). Let the reference input be 

Fm ∈ RB×C×H ×W ; then Fh and Fl denote the adjacent higher-and lower-resolution inputs, respectively. One representative instantiation used in our SimFusion block is 

Zh = Conv 1×1(AAP( Fh)) , (15) 

Zm = Conv 1×1(Fm), (16) 

Zl = Conv 1×1(Up( Fl )) , (17) 

Fsf = EMA (Conv 1×1

(Concat( Zh, Zm, Zl ))) , (18) where AAP is adaptive average pooling, Up is bilinear interpolation, and EMA denotes the Efficient Multi-Scale Attention module [26] (group factor g = 8). Here, EMA refers to the attention module rather than the exponential moving average of model weights used during training. To keep the encoder lightweight, we disable EMA in the default setting (i.e., EMA( ·) = Identity( ·)). 

> 4) CaMPB: CONTEXT-AWARE MULTI-SCALE PROGRESSIVE CHANNEL ATTENTION (PCA) BRIDGE

CaMPB is used to handle scale mismatch and semantic inconsistency before fusion. It has two parts. CaMPB-Align performs scale-aware alignment in a compact latent form, and CaMPB-Fuse applies bidirectional context-guided fusion to suppress noise and correct misplaced responses. Fig. 6 shows the MultiScalePCA-based down-alignment and the following fusion block. 

> a: CaMPB-ALIGN (MultiScalePCA)

CaMPB-Align (Fig. 6a) is adapted from the Multi-scale Progressive Channel Attention (MPCA) mechanism [27]. Here it serves as a compact cross-scale alignment bridge inside the encoder. Unlike the original MPCA, which upsamples deeper features to higher resolution, we use a down-alignment variant to keep the computation low and to better match the coarse-to-fine interaction pattern of the present lightweight DETR-style pipeline. Given two inputs 

X1 ∈ RB×C1×H ×W (coarse) and X2 ∈ RB×C2×2H ×2W (fine), MSPCA first computes channel descriptors with global average pooling (GAP) and efficient 1D convolutions. The 1D kernel size is set adaptively as 

k(C) = odd 

(⌊∣ ∣∣∣

log 2(C) + b

γ

∣∣∣∣⌋) 

, (19) where odd( ·) enforces an odd kernel size (i.e., odd( k) = k

if k is odd and k + 1 otherwise), and we use ( γ , b) = (2 , 1) in all experiments. MSPCA then performs joint gating and down-alignment :

s1 = Conv1D k(C1)(GAP( X1)) , (20) 

s2 = Conv1D k(C2)(GAP( X2)) , (21) 

s = σ (Conv1D k(C1+C2)(Concat( s1, s2)) ) , (22) [w1, w2] = Split( s), (23) 

A = φ1×1

(

X1 ⊙ w1

+ Down 3×3,s=2(X2 ⊙ w2)

)

, (24) where φ1×1 is a convolution–BN–activation projection. 

> b: CaMPB-FUSE (CONTEXT-GUIDED FUSION)

CaMPB-Fuse (Fig. 6b) serves as the Context-Guided Fusion (CGF) block. Given two spatially aligned feature maps X ∈

RB×Cx ×H ×W and Y ∈ RB×Cy×H ×W , CGF first removes channel mismatch through an adaptive 1 × 1 projection so that both share channel width C. It then builds a joint context over the two inputs through concatenation and a squeeze– excitation-style operator [28], using a standard channel bottleneck with reduction ratio r = 16 to keep the fusion block lightweight :

U = Concat( X , Y ),

˜U = U ⊙ σ (W2 δ(W1 GAP( U )) ), (25) where GAP is global average pooling, δ(·) is the rectified linear unit (ReLU), and σ (·) is Sigmoid. We split the reweighted feature ˜U into two parts :

[ ˜X , ˜Y ] = Split( ˜U ), (26) and then perform symmetric bidirectional enhancement and 1 × 1 compression :

Fout = φ1×1(Concat( X + ˜ Y , Y + ˜ X )) , (27) where φ1×1 is a convolution–BN–activation projection. 

> 5) D-FINE TRANSFORMER DECODER

We retain the D-FINE Transformer decoder [6]. It consumes 

{E3, E4, E5} and applies multi-scale deformable attention with iterative refinement [29]. The decoder outputs a fixed-size prediction set, enabling end-to-end inference without NMS [3]. During training, denoising queries are constructed by injecting label and box noise to stabilize early optimiza-tion [30]. D-FINE-style self-distillation further supervises intermediate refinement stages to improve localization stabil-ity [6]. 

> III. EXPERIMENTS AND ANALYSIS
> A. DATASETS AND EXPERIMENTAL SETUP
> 1) DATASET

VisDrone2019 is a publicly available UAV object-detection benchmark released by the AISKYEYE team at Tianjin University [17]. It contains 8,599 high-resolution aerial images covering diverse urban, suburban, and road scenes, and is split into 6,471 training images, 548 validation images,   

> 120440 VOLUME 14, 2026 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging
> FIGURE 6. Structure of CaMPB.

and 1,580 test images. The dataset defines 10 categories with 2D bounding-box annotations: pedestrian , people , bicycle ,

car , van , truck , tricycle , awning-tricycle , bus , and motorbike ,thereby enabling standardized and reproducible evaluation. SC-D-FINE is also evaluated on two public aerial datasets with markedly different annotation granularity to test whether its behavior extends beyond a single benchmark. UAVVaste [31] is a low-altitude UAV rubbish-detection dataset; in our prepared split it contains 540 training, 116 validation, and 116 test images with a single rubbish 

category. Vehicle Detection in Aerial Imagery (VEDAI) [32] is a fine-grained aerial vehicle benchmark, and we follow the standard 9-class fold-01 split at 1024-pixel resolution, containing 1,089 training and 121 evaluation images. Unless otherwise specified, VisDrone2019 remains the primary benchmark, whereas UAVVaste and VEDAI are used in Section III-B5 as additional transferability checks.  

> FIGURE 7. VisDrone2019 statistics.

2) DATASET STATISTICS 

VisDrone2019 poses several challenges for aerial object detection. Instance sizes span a wide range, from only a few pixels to several hundred pixels; the bounding-box scale distribution and per-category instance distribution are visualized in Fig. 7a and Fig. 7b. Crowded scenes and severe occlusions are common, producing adjacent boundaries and frequent overlaps that complicate localization and classifica-tion. In addition, the top-down viewpoint and varying capture angles of UAV imagery lead to marked perspective and appearance variation, yielding large intra-class differences across heights, poses, and imaging conditions. Following common practice in related work, we refer to this benchmark simply as VisDrone2019 throughout the remainder of the paper; unless otherwise specified, models are trained on the official training split and evaluated on the official validation split using Common Objects in Context (COCO)-style annotations [33]. 

3) EVALUATION METRICS 

Detection performance is reported using Average Precision (AP), AP 50 , and scale-aware AP for small, medium, and large objects (AP S , AP M , AP L ), together with Average Recall (AR). We also report FPS, parameter count (Params), and computational complexity (GFLOPs). Precision and recall, based on true positives (TP), false positives (FP), and false negatives (FN), are defined as Precision = TP TP + FP ,

Recall = TP TP + FN , (28)  

> VOLUME 14, 2026 120441 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging

where TP , FP , and FN follow the definitions above. Mean Average Precision (mAP) is the mean of AP scores computed over all categories :

mAP = 1

N

> N

∑

> n=1

AP n, (29) where N is the number of categories and AP n is the AP of class n. AP 50 denotes AP at an Intersection over Union (IoU) threshold of 0.5. AP S , AP M , and AP L represent AP for small, medium, and large objects, respectively. Average Recall (AR) is defined as the mean recall over a set of IoU thresholds :

AR = 1

K

> K

∑

> k=1

Recall k , (30) where K is the number of IoU thresholds used. 

> 4) IMPLEMENTATION DETAILS

All models are implemented in PyTorch and trained on VisDrone2019 with an input resolution of 640 × 640. All variants are optimized with AdamW [34], and the key training hyperparameters are kept consistent, as summarized in Table 1. For UAVVaste and VEDAI, the same architecture and optimization strategy are used, with only the dataset-specific class definition and evaluation split changed. Server-side runtime is measured on an RTX 3090. All models are accelerated with TensorRT using batch size 1 and 640 ×

640 inputs. A separate embedded benchmark is conducted on an NVIDIA Jetson Orin Nano (4 GB) with TensorRT 16-bit floating-point (FP16) inference. For the main D-FINE and SC-D-FINE models on VisDrone2019, we additionally execute the same training configuration three times while keeping the released seed setting at 0. The deviations reported in Tables 3 and 4 therefore describe the observed run-to-run variation of this fixed setup, rather than variation across different seeds. 

> B. RESULTS AND DISCUSSION
> 1) ABLATION STUDY

We start from D-FINE-N and then add DRC, SGMA, and CaMPB step by step to isolate the role of each component and their combined effect. We report AP and AP 50 together with parameter count and GFLOPs, where AP denotes the standard COCO-style AP 50 :95 metric. 

> a: DISCUSSION

Adding DRC alone raises AP from 20.8% to 20.9% and AP 50 

from 36.8% to 37.0% with virtually unchanged complexity. The gain is modest, but the direction is positive even before the encoder is modified. Adding SGMA or CaMPB separately raises AP to 24.6% and 24.5%, respectively. The close AP 50 values of these two settings (41.4% and 41.5%) are consistent with the role of alignment in crowded UAV scenes. Using both modules together reaches 25.5% AP, and adding DRC on top provides a further 0.2-point gain, bringing the final model to 25.7% AP and 43.0% AP 50 . The same direction of change therefore appears in both the baseline and the full setting. In this design, DRC is best understood as a small context supplement rather than the main source of the gain. 

> 2) COMPARISON WITH BENCHMARK REAL-TIME DETECTORS

Table 3 reports the broader VisDrone2019 benchmark and includes representative one-stage and DETR-style baselines, covering YOLOv9/10, YOLO11/12, and YOLO26 [35], [36], [37], [38], [39], RT-DETR/RT-DETRv2/RT-DETRv4 [4], [5], [18], and D-FINE [6]. The retained YOLO baselines are arranged in release order, and RT-DETRv4-S/M denotes the HGNetv2-S/M presets. These models span 5.8 to 74.8 GFLOPs. To avoid repeating every internal scaling variant, the SC-D-FINE side lists the operating points used in the trade-off analysis, whereas the full within-family comparisons across comparable compute ranges are reported separately in Table 4. The reported FPS values follow the TensorRT setting described above, whereas the non-D-FINE baselines are listed with their single benchmark values. For the D-FINE and SC-D-FINE rows, each AP metric is followed by the corresponding standard deviation in parentheses, which indicates the observed run-to-run variation under the fixed configuration described above. 

> a: DISCUSSION

The expanded comparison makes the position of SC-D-FINE clearer across the full benchmark. In the low-compute range, SC-D-FINE-N reaches 25.7% AP and 43.0% AP 50 ,compared with 20.8% and 36.8% for D-FINE-N; this margin is much larger than the attached deviations. It is also 6.6 AP above the strongest YOLO model below 10 GFLOPs (YOLOv9n) and matches RT-DETRv4-S while using 45.2% fewer GFLOPs. In the 20–30-GFLOPs range, SC-D-FINE-S and SC-D-FINE-24G reach central AP values of 27.1% and 27.5%. Both are above the YOLO s-level baselines in Table 3. Compared with D-FINE-S, SC-D-FINE-S is best read as a compact trade-off point, while SC-D-FINE-24G gives a modest 0.7 AP gain at nearly the same cost. In the higher-capacity range, SC-D-FINE-56G reaches 29.9% AP and 49.3% AP 50 , exceeding D-FINE-M (29.3%/48.3%), RT-DETR-R18 (28.7%/48.6%), RT-DETRv2-R18 (28.9%/48.6%), and RT-DETRv4-M (28.1%/46.4%). Thus, the main evidence comes from the low-compute and matched high-compute comparisons, while smaller central-value differences are treated conservatively. Table 4 then narrows the comparison to within-family settings with comparable computation, where the effect of architecture can be separated more cleanly from plain model scaling. 

> 3) EFFICIENCY VALIDATION ACROSS MODEL SCALES

Table 4 isolates the effect of feature design from plain model scaling. SC-D-FINE is compared with D-FINE variants across three matched compute regimes.     

> 120442 VOLUME 14, 2026 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging
> TABLE 1. Training settings on VisDrone2019.
> TABLE 2. Module ablation on VisDrone2019.
> TABLE 3. Benchmark comparison on VisDrone2019.

a: DISCUSSION 

The 14-GFLOPs pair is the most direct within-family check. Scaling D-FINE-N to 14.02 GFLOPs raises it to 23.9% AP, whereas SC-D-FINE-N reaches 25.7% AP at 14.00 GFLOPs. SC-D-FINE-N also uses 4.87M rather than 6.97M parameters and runs at 178.1 instead of 172.3 FPS. The AP margin is larger than the attached deviations and remains positive at all object scales ( +1.8 AP S , +2.1 AP M , and +1.1 AP L ), suggesting that the gain does not come from width scaling alone. In the 20–25-GFLOPs range, SC-D-FINE-S gives compa-rable AP to D-FINE-S while using 32.3% fewer parameters and 18.6% fewer GFLOPs; its main advantage is on medium objects (37.1% vs. 35.7%). At nearly the same cost as D-FINE-S, SC-D-FINE-24G reaches 27.5% AP and is higher on AP 50 , AP M , and AP L , although AP S remains slightly lower. In the higher-capacity setting, SC-D-FINE-M mainly improves AP M , while SC-D-FINE-56G restores most of the large-object performance and reaches the best overall AP/AP 50 (29.9%/49.3%). Across the D-FINE-family rows, the attached deviations remain limited (0.08–0.37 AP). The larger margins at the 14-GFLOPs and 56-GFLOPs points support the main trend, whereas the smaller S/M-scale differences are interpreted as efficiency–accuracy trade-offs rather than large accuracy gaps. Fig. 8 shows the same relation in AP–GFLOPs space. Across the 14–56 GFLOPs range, the plotted SC-D-FINE operating points stay above the D-FINE references   

> VOLUME 14, 2026 120443 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging
> TABLE 4. Efficiency validation within the D-FINE family on VisDrone2019.

in comparable compute ranges. SC-D-FINE-N matches RT-DETRv4-S in AP while using 45.2% fewer GFLOPs and 52.4% fewer parameters. At the higher end, SC-D-FINE-56G reaches 29.9% AP, above RT-DETR-R18/RT-DETRv2-R18 (28.7%/28.9%) and D-FINE-M (29.3%). 

> 4) EDGE DEPLOYMENT ON JETSON ORIN NANO

Complementing the RTX 3090 benchmark, runtime is further evaluated on an NVIDIA Jetson Orin Nano (4 GB). All compared models are exported and executed with TensorRT FP16 using batch size 1 and 640 × 640 inputs. AP values are taken from the VisDrone2019 benchmark above, while FPS and latency are measured directly on the device. 

> a: DISCUSSION

On Jetson Orin Nano, D-FINE-N is the fastest model in this group. Within the 14-GFLOPs regime, SC-D-FINE-N reaches 31.4 FPS with 31.9 ms latency, slightly ahead of D-FINE-N-14G (30.8 FPS, 32.5 ms), while also giving higher AP (25.7 vs. 23.9) with fewer parameters. Compared with YOLO26s, SC-D-FINE-N delivers higher AP (25.7 vs. 21.6) at lower FPS. These results indicate that SC-D-FINE-N remains suitable for the 4-GB device, with the design prefer-ence placed on accuracy rather than maximum throughput. 

> 5) CROSS-DATASET GENERALIZATION

To test whether the encoder changes are tied to Vis-Drone2019, we retrain SC-D-FINE-N and representative baselines on UAVVaste and VEDAI. UAVVaste is a single-class low-altitude rubbish-detection dataset, whereas VEDAI is a nine-class aerial vehicle benchmark. Their label spaces and scene statistics differ enough to serve as a useful secondary check. 

> a: DISCUSSION

Tables 6 and 7 report matched retraining results on the two additional datasets. SC-D-FINE-N remains clearly above D-FINE-N in both cases. On UAVVaste, the gap over D-FINE-N is 6.4 AP. SC-D-FINE-N matches RT-DETRv4-S in overall AP while using 45.2% fewer GFLOPs and 52.4% fewer parameters, and it is higher on AP 50 , AP S , and AP L .On VEDAI, SC-D-FINE-N improves over D-FINE-N by 8.4 AP and records the highest overall AP in the table. RT-DETRv4-S is slightly higher on AP S , but SC-D-FINE-N is higher on AP M and AP L with a much smaller model. Seeing the same tendency on both a single-class waste dataset and a multi-class vehicle dataset suggests that the encoder changes are not tied to one annotation setting. 

> 6) SCALE-WISE ERROR ANALYSIS

AP alone does not show where the gain comes from, so we also inspect errors by object size. Fig. 9 reports TP/FP/FN counts and precision/recall by size on VisDrone2019 for D-FINE-N and SC-D-FINE-N. SC-D-FINE-N reduces small-object false negatives from 16,006 to 13,804 and raises small-object recall from 42.5% to 50.4% while keeping precision almost unchanged (61.4% vs. 61.2%). The same tendency appears for medium objects (precision 71.1% →72.4%, recall 76.6% →79.8%) and large objects (precision 76.1% →78.7%, recall 84.2% →85.7%). In other words, the model gains recall without an obvious loss of precision across scales. 

> C. VISUALIZATION

The quantitative results are complemented by three qualita-tive views: detection outputs in difficult scenes, intermediate feature responses, and final heatmaps. The corresponding visualizations are presented in Figs. 10–14. 

> 1) DETECTION COMPARISON

Figs. 10–12 compare SC-D-FINE with the baseline on three challenging subsets of VisDrone2019: distant small objects, partial occlusion, and cluttered scenes with bright reflections. The top row in each figure shows the full image (ground truth, baseline, and SC-D-FINE, from left to right). The bottom row enlarges the regions marked by red rectangles. White dashed boxes mark the clearest local differences. 

> a: DISTANT SMALL TARGETS

Fig. 10 shows a long-distance traffic scene with numerous vehicles, pedestrians, and cyclists at very small scales. The  

> 120444 VOLUME 14, 2026

S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging 

FIGURE 8. AP–GFLOPs trade-off on VisDrone2019. 

TABLE 5. Edge inference on Jetson Orin Nano (4 GB). 

TABLE 6. Generalization results on UAVVaste. 

TABLE 7. Generalization results on VEDAI. 

baseline misses many of these distant instances, especially in the enlarged views, where several adjacent objects are fragmented or absent altogether. SC-D-FINE detects more of these targets, places boxes more tightly, and separates  

> VOLUME 14, 2026

120445 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging   

> FIGURE 9. Size-wise detection statistics on VisDrone2019.
> FIGURE 10. Qualitative comparison in a distant small-object scene.

neighboring instances more clearly in crowded regions. This observation is consistent with the quantitative improvement on small-object detection. 

b: PARTIAL OCCLUSION 

Fig. 11 focuses on heavily occluded regions. When vehicles are densely packed and partially overlap, the baseline produces more missed detections and less stable box placement, and its confidence on partially visible objects is usually lower. SC-D-FINE gives more distinct boxes that better follow the ground truth and separates neighboring vehicles more reliably. Its confidence scores are also visibly higher in several representative regions (e.g., cars at the same location rise to about 0.68, and vans in the upper-left region    

> 120446 VOLUME 14, 2026 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging
> FIGURE 11. Qualitative comparison under partial occlusion.
> FIGURE 12. Qualitative comparison in cluttered scenes with reflections.

rise from about 0.53 to about 0.82). Some overlapping boxes and occasional class confusion remain in the most crowded areas, particularly near van/car and truck/van boundaries. These cases still need better control of duplicate predictions and class ambiguity under severe occlusion. 

c: BACKGROUND CLUTTER AND REFLECTIONS 

Fig. 12 shows regions with strong reflections and heavy background clutter, such as overexposed shop fronts and specular reflections from glass or metal surfaces. In these conditions the baseline becomes less stable: boxes are sparser and less continuous, and objects near bright reflective edges are often missed. SC-D-FINE preserves more of the annotated targets in these areas and follows the annotated distribution more closely. Some redundant boxes still appear near bright highlight bands, but the overall behavior is visibly more stable. 

2) FEATURE RESPONSE COMPARISON 

The feature maps show a similar pattern. Fig. 13 compares P3 activations for three representative samples. For this feature-level comparison only, the baseline is D-FINE-N-14G: this expanded variant uses a three-scale encoder, whereas the standard D-FINE-N setting uses two encoder scales and therefore has no directly comparable P3 output. In the baseline maps (middle column), responses are more diffuse  

> VOLUME 14, 2026 120447

S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging 

FIGURE 13. P3 feature responses of D-FINE-N-14G and SC-D-FINE. 

FIGURE 14. Heatmap comparison of D-FINE-N and SC-D-FINE. 

and often spread into the background, and some objects receive only weak activation. In SC-D-FINE (right column), the P3 responses are tighter and spatially cleaner: activations follow target contours more closely and spurious background 

120448 VOLUME 14, 2026 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging 

responses are reduced. Because P3 is especially important for small and medium objects, this difference is consistent with the quantitative gains in recall and localization. 

3) HEATMAP COMPARISON 

Fig. 14 shows the final heatmap comparison. In the baseline heatmaps (middle column), activations are often scattered, some targets respond weakly, localization is coarser, and false positives appear in difficult background regions. The SC-D-FINE heatmaps (right column) are more concentrated and follow target contours more closely. Target regions receive clearer responses, predicted boxes fit the objects better, and both false positives and misses are reduced. The contrast is most visible in scenes with clutter, very small objects, and partial occlusion. 

IV. CONCLUSION 

SC-D-FINE extends D-FINE for lightweight object detection in aerial imagery under tight compute budgets. The design is centered on the SGMA–CaMPB encoder and uses a re-parameterizable DRC tail as a lightweight context sup-plement. On VisDrone2019, SC-D-FINE-N reaches 25.7% AP and 43.0% AP 50 , compared with 20.8% and 36.8% for D-FINE-N. In the 14-GFLOPs regime, it remains 1.8 AP above D-FINE-N-14G while using 30.1% fewer parameters. On Jetson Orin Nano (4 GB), the same model runs at 31.4 FPS with 31.9 ms latency under TensorRT FP16. Similar trends are observed for the larger variants, and retraining on UAVVaste and VEDAI leads to the same direction of change. The ablations show that most of the improvement comes from the SGMA–CaMPB encoder, while DRC provides a smaller but consistent gain at negligible extra cost. The run-to-run variation reported in the VisDrone2019 benchmark tables supports the main low-compute and 56-GFLOPs comparisons; the smaller S/M-scale differences are better interpreted as efficiency–accuracy trade-offs. The error and visual analyses support the same picture, with fewer misses on small objects and cleaner responses in cluttered or occluded scenes. The model still incurs more computation than the smallest baseline, which may matter on very constrained hardware. Severe reflections and heavy occlusion can also produce redundant detections or class ambiguity. Future work will focus on lighter fusion schemes, better control of duplicate predictions in DETR-style decoding, and broader evaluation on aerial and remote-sensing datasets. 

DATA AVAILABILITY 

The datasets used in this study are publicly available from their official project pages: VisDrone2019 at https://aiskyeye. com/iccv2019/, UAVVaste at https://uavvaste.github.io/, and VEDAI at https://downloads.greyc.fr/vedai/. The main derived data supporting the findings of this study are included in this article. The complete source code, additional implementation details, selected experimental result files, and selected trained model weights for the main SC-D-FINE variants will be made publicly available in an online repository. 

CONFLICTS OF INTEREST 

The authors declare no conflicts of interest. 

ACKNOWLEDGMENT 

Artificial intelligence (AI)-assisted tools were used only for language polishing because the authors are not native English speakers [40]; no AI tools were used for study design, data generation, data analysis, interpretation, figure generation, or scientific conclusions. 

REFERENCES 

[1] J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, ‘‘You only look once: Unified, real-time object detection,’’ in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jun. 2016, pp. 779–788. [2] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, ‘‘Attention is all you need,’’ in Proc. Adv. Neu-ral Inf. Process. Syst. , vol. 30, 2017, pp. 5998–6008. [Online]. Available: https://proceedings.neurips.cc/paper/7181-attention-is-all-you-need [3] N. Carion, F. Massa, G. Synnaeve, N. Usunier, A. Kirillov, and S. Zagoruyko, ‘‘End-to-end object detection with transformers,’’ in Proc. Eur. Conf. Comput. Vis. (ECCV) , 2020, pp. 213–229. [4] Y. Zhao, W. Lv, S. Xu, J. Wei, G. Wang, Q. Dang, Y. Liu, and J. Chen, ‘‘DETRs beat YOLOs on real-time object detection,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jun. 2024, pp. 16965–16974. [5] W. Lv, Y. Zhao, Q. Chang, K. Huang, G. Wang, and Y. Liu, ‘‘RT-DETRv2: Improved baseline with bag-of-freebies for real-time detection transformer,’’ 2024, arXiv:2407.17140 .[6] Y. Peng, H. Li, P. Wu, Y. Zhang, X. Sun, and F. Wu, ‘‘D-FINE: Redefine regression task of DETRs as fine-grained distribution refinement,’’ in 

Proc. 13th Int. Conf. Learn. Represent. , 2025. [Online]. Available: https: //openreview.net/forum?id=MFZjrTFE7h [7] S. Huang, Z. Lu, X. Cun, Y. Yu, X. Zhou, and X. Shen, ‘‘DEIM: DETR with improved matching for fast convergence,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jun. 2025, pp. 15162–15171. [8] X. Wu, W. Li, D. Hong, R. Tao, and Q. Du, ‘‘Deep learning for unmanned aerial vehicle-based object detection and tracking: A survey,’’ IEEE Geosci. Remote Sens. Mag. , vol. 10, no. 1, pp. 91–124, Mar. 2022. [9] P. Mittal, R. Singh, and A. Sharma, ‘‘Deep learning-based object detection in low-altitude UAV datasets: A survey,’’ Image Vis. Comput. , vol. 104, Dec. 2020, Art. no. 104046. [10] G. Tang, J. Ni, Y. Zhao, Y. Gu, and W. Cao, ‘‘A survey of object detection for UAVs based on deep learning,’’ Remote Sens. , vol. 16, no. 1, p. 149, Dec. 2023. [11] G. Cheng and J. Han, ‘‘A survey on object detection in optical remote sensing images,’’ ISPRS J. Photogramm. Remote Sens. , vol. 117, pp. 11–28, Jul. 2016. [12] Q. Yu, Q. Tong, L. Miao, L. Qi, and X. Liu, ‘‘An enhanced end-to-end object detector for drone aerial imagery,’’ IEEE Access , vol. 13, pp. 18798–18813, 2025. [13] H. Zhang, H. Zhang, K. Liu, Z. Gan, and G.-N. Zhu, ‘‘UAV-DETR: Effi-cient end-to-end object detection for unmanned aerial vehicle imagery,’’ in Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS) , Oct. 2025, pp. 15143–15149. [14] Y. Bai and Y. Liu, ‘‘DL-DEIM: An efficient and lightweight detection framework with enhanced feature fusion for UAV object detection,’’ Appl. Sci. , vol. 15, no. 22, p. 11966, Nov. 2025. [15] X. Chang, X. Wang, and K. Li, ‘‘Overcoming scale variations and occlusions in aerial detection: A context-aware DEIM framework,’’ 

Sensors , vol. 26, no. 1, p. 147, Dec. 2025. [16] S. Tang, L. Zhang, X. Liu, R. Lv, and R. Qin, ‘‘RFHS-RTDETR: Multi-domain collaborative network with hierarchical feature inte-gration for UAV-based object detection,’’ IEEE Access , vol. 13, pp. 121686–121703, 2025.  

> VOLUME 14, 2026 120449 S. Tang, Z. Zeng: SC-D-FINE: Early Multi-Scale Focusing and Context-Aware Bridging

[17] D. Du et al., ‘‘VisDrone-DET2019: The vision meets drone object detection in image challenge results,’’ in Proc. IEEE/CVF Int. Conf. Comput. Vis. Workshop (ICCVW) , Oct. 2019, pp. 213–226. [18] Z. Liao, Y. Zhao, X. Shan, Y. Yan, C. Liu, L. Lu, X. Ji, and J. Chen, ‘‘RT-DETRv4: Painlessly furthering real-time object detection with vision foundation models,’’ 2025, arXiv:2510.25257 .[19] A. G. Howard, M. Zhu, B. Chen, D. Kalenichenko, W. Wang, T. Weyand, M. Andreetto, and H. Adam, ‘‘MobileNets: Efficient convolutional neural networks for mobile vision applications,’’ 2017, arXiv:1704.04861 .[20] F. Yu and V. Koltun, ‘‘Multi-scale context aggregation by dilated convolutions,’’ 2015, arXiv:1511.07122 .[21] X. Ding, Y. Zhang, Y. Ge, S. Zhao, L. Song, X. Yue, and Y. Shan, ‘‘UniRepLKNet: A universal perception large-kernel ConvNet for audio, video, point cloud, time-series and image recognition,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jun. 2024, pp. 5513–5524. [22] X. Ding, X. Zhang, N. Ma, J. Han, G. Ding, and J. Sun, ‘‘RepVGG: Making VGG-style ConvNets great again,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jun. 2021, pp. 13728–13737. [23] T.-Y. Lin, P. Dollár, R. Girshick, K. He, B. Hariharan, and S. Belongie, ‘‘Feature pyramid networks for object detection,’’ in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jul. 2017, pp. 936–944. [24] S. Liu, L. Qi, H. Qin, J. Shi, and J. Jia, ‘‘Path aggregation network for instance segmentation,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. , Jun. 2018, pp. 8759–8768. [25] M. Tan, R. Pang, and Q. V. Le, ‘‘EfficientDet: Scalable and efficient object detection,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jun. 2020, pp. 10781–10790. [26] D. Ouyang, S. He, G. Zhang, M. Luo, H. Guo, J. Zhan, and Z. Huang, ‘‘Efficient multi-scale attention module with cross-spatial learning,’’ in Proc. IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP) ,Jun. 2023, pp. 1–5. [27] Z. Zhou, A. He, Y. Wu, R. Yao, X. Xie, and T. Li, ‘‘Spatial-frequency dual domain attention network for medical image segmentation,’’ in Proc. IEEE Int. Conf. Bioinf. Biomed. (BIBM) , Dec. 2024, pp. 4076–4081. [28] J. Hu, L. Shen, and G. Sun, ‘‘Squeeze-and-excitation networks,’’ in 

Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. , Jun. 2018, pp. 7132–7141. [29] X. Zhu, W. Su, L. Lu, B. Li, X. Wang, and J. Dai, ‘‘Deformable DETR: Deformable transformers for end-to-end object detection,’’ in Proc. Int. Conf. Learn. Represent. , 2021. [30] F. Li, H. Zhang, S. Liu, J. Guo, L. M. Ni, and L. Zhang, ‘‘DN-DETR: Accelerate DETR training by introducing query denoising,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR) , Jun. 2022, pp. 13609–13617. [31] M. Kraft, M. Piechocki, B. Ptak, and K. Walas, ‘‘Autonomous, onboard vision-based trash and litter detection in low altitude aerial images collected by an unmanned aerial vehicle,’’ Remote Sens. , vol. 13, no. 5, p. 965, Mar. 2021. [32] S. Razakarivony and F. Jurie, ‘‘Vehicle detection in aerial imagery : A small target detection benchmark,’’ J. Vis. Commun. Image Represent. , vol. 34, pp. 187–203, Jan. 2016. [33] T.-Y. Lin, M. Maire, S. Belongie, J. Hays, P. Perona, D. Ramanan, P. Dollár, and C. L. Zitnick, ‘‘Microsoft COCO: Common objects in context,’’ in 

Proc. Eur. Conf. Comput. Vis. (ECCV) , 2014, pp. 740–755. [34] I. Loshchilov and F. Hutter, ‘‘Decoupled weight decay regularization,’’ in 

Proc. Int. Conf. Learn. Represent. (ICLR) , 2019. [35] C.-Y. Wang, I.-H. Yeh, and H.-Y. M. Liao, ‘‘YOLOv9: Learning what you want to learn using programmable gradient information,’’ in Proc. Eur. Conf. Comput. Vis. (ECCV) , 2024, pp. 1–21. [36] A. Wang, H. Chen, L. Liu, K. Chen, Z. Lin, J. Han, and G. Ding, ‘‘YOLOv10: Real-time end-to-end object detection,’’ in Proc. Adv. Neural Inf. Process. Syst. , vol. 37, 2024, pp. 107984–108011. [Online]. Available: https://proceedings.neurips.cc/paperfiles/paper/2024/ file/c34ddd05eb089991f06f3c5dc36836e0-Paper-Conference.pdf [37] R. Khanam and M. Hussain, ‘‘YOLOv11: An overview of the key architectural enhancements,’’ 2024, arXiv:2410.17725 .[38] Y. Tian, Q. Ye, and D. Doermann, ‘‘YOLOv12: Attention-centric real-time object detectors,’’ in Proc. Adv. Neural Inf. Process. Syst. (NeurIPS) , 2025, pp. 78433–78457. [Online]. Available: https://proceedings.neurips.cc/paperfiles/paper/2025/file/ 7103444259031cc58051f8c9a4868533-Paper-Conference.pdf [39] R. Sapkota, R. Harsha Cheppally, A. Sharda, and M. Karkee, ‘‘YOLO26: Key architectural enhancements and performance benchmarking for real-time object detection,’’ 2025, arXiv:2509.25164 .[40] OpenAI. (2026). ChatGPT: General FAQ . Accessed: Jun. 3, 2026. [Online]. Available: https://help.openai.com/en/articles/ 6783457-chatgpt-general-faq 

SHUHANG TANG received the B.S. degree in computer science and technology and the M.S. degree in computer applied technology from Northwestern Polytechnical University, Xi’an, China, in 2013 and 2016, respectively. He is currently a Senior Engineer with China Mobile IoT Company Ltd., Chongqing, China. His current research interests include computer vision, soft-ware architecture, and system optimization. 

ZHUO ZENG received the Ph.D. degree in computer science and technology from Chongqing University, Chongqing, China, in 2023. He is currently a Lecturer with the College of Artificial Intelligence and Big Data, Chongqing Polytechnic University of Electronic Technology, Chongqing. His current research interests include graph neural networks, artificial intelligence, and spatiotempo-ral data processing.
