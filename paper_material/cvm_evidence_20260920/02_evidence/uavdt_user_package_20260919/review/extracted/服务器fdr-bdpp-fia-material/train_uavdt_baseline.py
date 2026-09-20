import warnings, os, sys
# os.environ["CUDA_VISIBLE_DEVICES"]="-1"    # 代表用cpu训练 不推荐！没意义！ 而且有些模块不能在cpu上跑
# os.environ["CUDA_VISIBLE_DEVICES"]="0"     # 代表用第一张卡进行训练  0：第一张卡 1：第二张卡
warnings.filterwarnings('ignore')
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# 纯 stock RT-DETR-L 对照臂（无 FDR/FIA/BPDD），不依赖 src/ 中的自定义模块，
# 超参数与 train.py 完全一致，未写出的参数由 ultralytics 默认值接管。
from ultralytics import RTDETR


if __name__ == '__main__':
    model = RTDETR('rtdetr-l.yaml')  # stock RT-DETR-L 结构，即 ultralytics 内置 rtdetr-l.yaml 的本地副本
    model.train(
        model='rtdetr-l.yaml',
        data='configs/UAVDT.yaml',
        cache=False,
        imgsz=640,
        epochs=100,
        batch=8,
        workers=4,  # Windows下出现莫名其妙卡主的情况可以尝试把workers设置为0
        # 'device': '0,1',  # 指定显卡和多卡训练参考<使用教程.md>下方常见错误和解决方案
        # 'resume': '',  # last.pt path
        patience=0,  # 设置0代表不早提供，设置30代表精度持续30epoch没有比之前最高的高就早停
        pretrained=False,  # 从头训练
        optimizer='MuSGD',
        project='runs/train',
        name='uavdt-rtdetr-baseline-exp',
    )
