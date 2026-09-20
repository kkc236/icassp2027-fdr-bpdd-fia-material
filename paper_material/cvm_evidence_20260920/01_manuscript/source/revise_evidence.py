"""Apply this revision's editorial changes to the prior frozen manuscript."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
p = OUT / 'source/body.tex'
s = p.read_text(encoding='ascii')
def replace(old, new):
    global s
    assert old in s, old[:100]
    s = s.replace(old, new)

replace('over D-FINE-L under different training recipes.',
        'over our scratch-adapted D-FINE-L reproduction under different training recipes.')
replace('physical batch eight, nominal batch 64, and seed zero.',
        'physical batch eight, nominal batch 64, and seed zero. The trainer accumulates eight physical batches after warmup, giving approximately 64 images per optimizer update; the accumulation factor ramps during warmup.')
replace('D-FINE-L has 31.146M parameters and uses 100-epoch scratch training with AdamW at learning rate 0.00025, FP32, batch four without accumulation, multiscale augmentation from 480 to 800, and stage-best checkpoint restoration. The common evaluator controls the evaluation pipeline, while these training recipes differ.',
        "Our D-FINE-L comparison is a scratch-adapted reproduction of the official implementation, with 31.146M parameters. We make the backbone and its normalization trainable and use learning rate 0.00025 across parameter groups. Training runs for 100 epochs with AdamW, FP32, physical and effective batch four without accumulation, multiscale augmentation from 480 to 800, and stage-best checkpoint restoration at epoch 72. Thus, the common evaluator aligns prediction and scoring, while optimization, effective batch size, and augmentation differ; equal epoch counts do not imply equal optimizer-update counts or training compute.")
replace('Full reaches 24.133 AP at the final checkpoint, exceeding D-FINE-L by 1.579 points.',
        'Full reaches 24.133 AP at the final checkpoint, exceeding our D-FINE-L reproduction by 1.579 points.')
replace('over D-FINE-L by 1.579 points under their respective training recipes.',
        'over our scratch-adapted D-FINE-L reproduction by 1.579 points under their respective training recipes.')
p.write_text(s, encoding='ascii')

p = OUT / 'build.py'
s = p.read_text(encoding='ascii')
s = s.replace('External VisDrone test comparison under the common evaluator. Training recipes differ. Final is primary;',
    'External VisDrone test comparison under the common evaluator. D-FINE-L denotes our scratch-adapted reproduction; training recipes and effective batches differ (Sec.~\\ref{sec:protocol}). Final is primary;')
p.write_text(s, encoding='ascii')
print('D-FINE identity, accumulation, and comparison scope clarified.')
