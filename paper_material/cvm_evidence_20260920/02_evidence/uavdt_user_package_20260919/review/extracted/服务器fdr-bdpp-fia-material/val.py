import warnings
warnings.filterwarnings('ignore')
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
from ultralytics import RTDETR
from ultralytics.utils.torch_utils import model_info

# train.py 用 src/rtdetr_fdr_bpdd_fia.py 中的 FDRBPDDFIATrainer 训练，
# 保存的 best.pt 内嵌自定义模型类 (FDRBPDDFIADetectionModel)，依赖自定义模块 (FIA / FDRRTDETRDecoder)。
# 加载权重前必须让 src 包可导入（反序列化用）并把自定义模块注册进 ultralytics（YAML 解析用）。
from src.rtdetr_fdr import register_fdr_module
from src.rtdetr_fdr_bpdd_fia import FDRBPDDFIADetectionModel  # noqa: F401

register_fdr_module()

def get_weight_size(path):
    stats = os.stat(path)
    return f'{stats.st_size / 1024 / 1024:.1f}'

if __name__ == '__main__':
    model_path = '/data/SAM/ltk/YOLO/fdr-bpdd-fia-material/runs/detect/runs/train/uavdt-fdr-bpdd-fia-exp-2/weights/best.pt' # 训练实际输出的权重路径
    model = RTDETR(model_path) # 选择训练好的权重路径
    result = model.val(data='configs/UAVDT.yaml', # 与 train.py 使用的数据集配置保持一致
                      split='val', # UAVDT.yaml 只定义了 train/val，split 可选 train、val
                      imgsz=640,
                      batch=4,
                    #   save_json=True, # if you need to cal coco metrice
                      project='runs/val',
                      name='exp',
                      )
    
    if model.task == 'detect': # 仅目标检测任务适用
        length = result.box.p.size
        model_names = list(result.names.values())
        preprocess_time_per_image = result.speed['preprocess']
        inference_time_per_image = result.speed['inference']
        postprocess_time_per_image = result.speed['postprocess']
        all_time_per_image = preprocess_time_per_image + inference_time_per_image + postprocess_time_per_image
        
        n_l, n_p, n_g, flops = model_info(model.model)
        
        print('-'*20 + '论文上的数据以以下结果为准' + '-'*20)
        print('-'*20 + '论文上的数据以以下结果为准' + '-'*20)
        print('-'*20 + '论文上的数据以以下结果为准' + '-'*20)
        print('-'*20 + '论文上的数据以以下结果为准' + '-'*20)
        print('-'*20 + '论文上的数据以以下结果为准' + '-'*20)

        header = ["Class Name", "Precision", "Recall", "F1-Score", "mAP50", "mAP75", "mAP50-95"]
        rows = [[
            model_names[idx],
            f"{result.box.p[idx]:.4f}",
            f"{result.box.r[idx]:.4f}",
            f"{result.box.f1[idx]:.4f}",
            f"{result.box.ap50[idx]:.4f}",
            f"{result.box.all_ap[idx, 5]:.4f}", # 50 55 60 65 70 75 80 85 90 95
            f"{result.box.ap[idx]:.4f}",
        ] for idx in range(length)]
        rows.append([
            "all(平均数据)",
            f"{result.results_dict['metrics/precision(B)']:.4f}",
            f"{result.results_dict['metrics/recall(B)']:.4f}",
            f"{np.mean(result.box.f1[:length]):.4f}",
            f"{result.results_dict['metrics/mAP50(B)']:.4f}",
            f"{np.mean(result.box.all_ap[:length, 5]):.4f}", # 50 55 60 65 70 75 80 85 90 95
            f"{result.results_dict['metrics/mAP50-95(B)']:.4f}",
        ])

        model_info_text = (
            f"GFLOPs: {flops:.1f}  Parameters: {n_p:,}  "
            f"前处理: {preprocess_time_per_image / 1000:.6f}s/图  "
            f"推理: {inference_time_per_image / 1000:.6f}s/图  "
            f"后处理: {postprocess_time_per_image / 1000:.6f}s/图  "
            f"FPS(全程): {1000 / all_time_per_image:.2f}  "
            f"FPS(推理): {1000 / inference_time_per_image:.2f}  "
            f"权重大小: {get_weight_size(model_path)}MB"
        )
        widths = [max(len(str(row[i])) for row in [header] + rows) for i in range(len(header))]
        model_metrice_text = '\n'.join(
            '  '.join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            for row in [header] + rows
        )
        print(model_info_text)
        print(model_metrice_text)

        with open(result.save_dir / 'paper_data.txt', 'w+', errors="ignore", encoding="utf-8") as f:
            f.write(model_info_text)
            f.write('\n')
            f.write(model_metrice_text)
        
        print('-'*20, f'结果已保存至{result.save_dir}/paper_data.txt...', '-'*20)
        print('-'*20, f'结果已保存至{result.save_dir}/paper_data.txt...', '-'*20)
        print('-'*20, f'结果已保存至{result.save_dir}/paper_data.txt...', '-'*20)
        print('-'*20, f'结果已保存至{result.save_dir}/paper_data.txt...', '-'*20)
        print('-'*20, f'结果已保存至{result.save_dir}/paper_data.txt...', '-'*20)