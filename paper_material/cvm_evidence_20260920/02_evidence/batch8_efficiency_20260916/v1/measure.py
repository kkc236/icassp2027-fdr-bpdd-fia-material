"""Inference-only batch benchmark of the five frozen VisDrone checkpoints."""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time

PRIOR = Path('/root/sj-tmp/evidence/audit-remediation-efficiency-20260915-v3')
HELPER_SHA = '57c09032533451df81cbdeaadbb528f39a605955e1166b5e41ddbfc9d0fa5420'
PRIOR_REPORT_SHA = '2fa6c070b0c69ee021962f491b86b87274476f458eb9521e12be014d7dd669ed'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def save(path, payload):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    os.replace(temporary, path)


def summarize(samples, batch_size):
    if not samples or batch_size <= 0 or not all(math.isfinite(x) and x > 0 for x in samples):
        raise ValueError('positive finite samples and batch size required')
    ordered = sorted(samples)
    position = .9 * (len(ordered) - 1)
    low, high = math.floor(position), math.ceil(position)
    median = statistics.median(samples)
    return {
        'sample_count': len(samples),
        'batch_median_ms': median,
        'batch_p90_ms': ordered[low] + (ordered[high] - ordered[low]) * (position - low),
        'amortized_ms_per_image': median / batch_size,
        'images_per_second_from_median': batch_size * 1000 / median,
        'images_per_second_from_total_measured_time': batch_size * len(samples) * 1000 / sum(samples),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    code, output = args.code_root.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'efficiency.json').exists() or (output / 'COMPLETE.json').exists():
        raise FileExistsError('use a new isolated output directory')
    rows = []
    try:
        assert sha256(PRIOR / 'measure.py') == HELPER_SHA
        assert sha256(PRIOR / 'efficiency.json') == PRIOR_REPORT_SHA
        prior = json.loads((PRIOR / 'efficiency.json').read_text())
        assert prior['status'] == 'completed' and prior['protocol']['batch'] == 1
        source_before = {relative: sha256(code / relative) for relative in prior['source_sha256']}
        assert source_before == {key: value.lower() for key, value in prior['source_sha256'].items()}
        specification = importlib.util.spec_from_file_location('frozen_batch1_helper', PRIOR / 'measure.py')
        helper = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(helper)
        sys.path.insert(0, str(code))
        import numpy as np
        import torch
        import ultralytics
        from ultralytics import RTDETR
        assert torch.cuda.is_available()
        torch.set_num_threads(8)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        for name in ('src.rtdetr_fdr', 'src.rtdetr_lrs_system', 'src.rtdetr_bpdd_capacity', 'src.rtdetr_bpdd_capacity_fia'):
            importlib.import_module(name)
        batch_size, warmup, iterations = 8, 100, 300
        images = list(np.random.default_rng(20260915).integers(0, 256, (8, 640, 640, 3), dtype=np.uint8))
        report = {
            'status': 'running', 'rows': rows,
            'protocol': {
                'imgsz': 640, 'batch': batch_size, 'dtype': 'float32', 'warmup': warmup,
                'iterations': iterations, 'conf': .001, 'max_det': 300, 'tta': False,
                'extra_nms': False, 'seed': 20260915, 'cpu_threads': 8,
                'tf32': False, 'cudnn_benchmark': False, 'fusion': 'native predictor fusion on GPU',
                'input': 'eight fixed seeded uint8 BGR random images; first equals prior batch1 input',
                'latency_scope': 'Ultralytics predict: preprocess + model + postprocess; excludes disk I/O',
                'timing': 'CUDA synchronized wall-clock per complete eight-image prediction call',
                'amortized_latency_is_not_single_request_latency': True,
                'expert_hook': 'same lightweight per-expert forward counter as prior batch1 benchmark',
            },
            'environment': {'python': platform.python_version(), 'torch': torch.__version__,
                'cuda': torch.version.cuda, 'ultralytics': ultralytics.__version__,
                'gpu': torch.cuda.get_device_name(0), 'device_total_memory_bytes': torch.cuda.get_device_properties(0).total_memory},
            'source_sha256_before': source_before, 'code_root': str(code),
            'prior_batch1_report_sha256': PRIOR_REPORT_SHA, 'helper_sha256': HELPER_SHA,
            'measurement_source_sha256': sha256(__file__),
            'input_sha256': [hashlib.sha256(image.tobytes()).hexdigest() for image in images],
            'training_started': False, 'uavdt_in_scope': False,
        }
        for key in ('python', 'torch', 'cuda', 'ultralytics', 'gpu'):
            assert report['environment'][key] == prior['environment'][key], key
        for arm, (checkpoint, expected) in helper.CHECKPOINTS.items():
            print('START', arm, flush=True)
            save(output / 'CURRENT.json', {'arm': arm, 'phase': 'loading', 'completed_arms': len(rows)})
            before = sha256(checkpoint)
            assert before == expected.lower()
            detector = RTDETR(checkpoint)
            compatibility = helper.normalize_legacy_no_expert_head(detector.model)
            assert not compatibility or arm in ('G', 'G+F')
            detector.model.to('cuda:0').float().eval()
            unfused = sum(p.numel() for p in detector.model.parameters())
            calls = [0]
            def expert_called(*unused):
                calls[0] += 1
            expert_hooks = [module.register_forward_hook(expert_called) for module in detector.model.modules()
                            if type(module).__name__ == 'LocalBoundaryExpert']
            observed_shapes = []
            def capture_input(module, inputs):
                if inputs and isinstance(inputs[0], torch.Tensor):
                    observed_shapes.append({'shape': list(inputs[0].shape), 'dtype': str(inputs[0].dtype), 'device': str(inputs[0].device)})
            shape_hook = detector.model.register_forward_pre_hook(capture_input)
            kwargs = dict(source=images, imgsz=640, batch=batch_size, device=0, conf=.001,
                          max_det=300, verbose=False, save=False, stream=False, augment=False)
            with torch.inference_mode():
                audit_results = detector.predict(**kwargs)
                shape_hook.remove()
                assert len(audit_results) == batch_size
                assert observed_shapes and observed_shapes[-1]['shape'] == [8, 3, 640, 640], observed_shapes
                assert observed_shapes[-1]['dtype'] == 'torch.float32'
                assert observed_shapes[-1]['device'] == 'cuda:0'
                assert detector.predictor.model.fp16 is False
                del audit_results
                for index in range(warmup):
                    detector.predict(**kwargs)
                    if (index + 1) % 25 == 0:
                        save(output / 'CURRENT.json', {'arm': arm, 'phase': 'warmup', 'iteration': index + 1, 'target': warmup, 'completed_arms': len(rows)})
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
                calls[0] = 0
                samples = []
                for index in range(iterations):
                    torch.cuda.synchronize()
                    start = time.perf_counter()
                    detector.predict(**kwargs)
                    torch.cuda.synchronize()
                    samples.append((time.perf_counter() - start) * 1000)
                    if (index + 1) % 25 == 0:
                        save(output / 'CURRENT.json', {'arm': arm, 'phase': 'measuring', 'iteration': index + 1, 'target': iterations, 'completed_arms': len(rows)})
                memory = torch.cuda.max_memory_allocated() / 1024 ** 2
                reserved = torch.cuda.max_memory_reserved() / 1024 ** 2
            expert_calls = calls[0]
            for hook in expert_hooks:
                hook.remove()
            assert expert_calls == (iterations if arm in ('G+B', 'Full') else 0), expert_calls
            assert sha256(checkpoint) == before
            prior_row = next(item for item in prior['rows'] if item['arm'] == arm)
            fused = sum(p.numel() for p in detector.model.parameters())
            assert (unfused, fused) == (prior_row['parameters_unfused'], prior_row['parameters_fused'])
            row = {
                'arm': arm, 'checkpoint': checkpoint, 'sha256_before': before, 'sha256_after': sha256(checkpoint),
                'parameters_unfused': unfused, 'parameters_fused': fused,
                'in_memory_legacy_compatibility': compatibility, 'observed_forward_input': observed_shapes[-1],
                'expert_forward_calls_measured': expert_calls, 'peak_allocated_mib': memory,
                'peak_reserved_mib': reserved, 'latency_samples_ms': samples, **summarize(samples, batch_size),
            }
            rows.append(row)
            save(output / (arm.replace('+', '_') + '.json'), row)
            print('FINISHED', json.dumps({key: value for key, value in row.items() if key not in ('latency_samples_ms', 'checkpoint')}), flush=True)
            del detector, expert_hooks
            gc.collect()
            torch.cuda.empty_cache()
        source_after = {relative: sha256(code / relative) for relative in source_before}
        assert source_after == source_before
        assert sha256(PRIOR / 'measure.py') == HELPER_SHA
        assert sha256(PRIOR / 'efficiency.json') == PRIOR_REPORT_SHA
        report.update(status='completed', source_sha256_after=source_after)
        save(output / 'efficiency.json', report)
        save(output / 'COMPLETE.json', {'status': 'completed', 'arms': len(rows), 'batch': 8,
            'measured_batches': len(rows) * iterations, 'measured_images': len(rows) * iterations * batch_size,
            'checkpoints_unchanged': True, 'training_sources_unchanged': True, 'training_started': False})
        save(output / 'CURRENT.json', {'phase': 'completed', 'completed_arms': len(rows)})
    except Exception as error:
        save(output / 'FAILED.json', {'status': 'failed', 'error': repr(error), 'completed_arms': len(rows)})
        raise


if __name__ == '__main__':
    main()
