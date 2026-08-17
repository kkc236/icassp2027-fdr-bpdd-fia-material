from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path):
    path = ROOT / relative_path
    assert path.is_file(), f"missing FIA ablation artifact: {relative_path}"
    return path.read_text(encoding="utf-8")


def test_fia_ablation_configs_isolate_stock_and_fdr_decoders():
    fia = _read("configs/rtdetr-l-fia.yaml")
    fdr_fia = _read("configs/rtdetr-l-fdr-fia.yaml")
    fia_head = yaml.safe_load(fia)["head"]
    fdr_fia_head = yaml.safe_load(fdr_fia)["head"]

    assert "[-1, 1, FIA, [256]]" in fia
    assert "[[22, 25, 28], 1, RTDETRDecoder, [nc]]" in fia
    assert "FDRRTDETRDecoder" not in fia

    assert "[-1, 1, FIA, [256]]" in fdr_fia
    assert "FDRRTDETRDecoder" in fdr_fia
    assert "fdr_loss:" in fdr_fia

    # Keep the exact P3-only topology already validated by the three-module
    # config: decoder P3 sees FIA, while rebuilt P4/P5 use the original P3.
    for head in (fia_head, fdr_fia_head):
        assert head[12] == [-1, 1, "FIA", [256]]
        assert head[13][0] == 21
        assert head[14][0] == [23, 17]
        assert head[16][0] == 25
        assert head[17][0] == [26, 12]
        assert head[19][0] == [22, 25, 28]


def test_fia_ablation_trainers_are_bound_to_their_configs():
    fia = _read("train_fia.py")
    fdr_fia = _read("train_fdr_fia.py")

    compile(fia, "train_fia.py", "exec")
    compile(fdr_fia, "train_fdr_fia.py", "exec")
    assert "FDRControlTrainer" in fia
    assert '"model": "configs/rtdetr-l-fia.yaml"' in fia
    assert "FDRTrainer" in fdr_fia
    assert '"model": "configs/rtdetr-l-fdr-fia.yaml"' in fdr_fia


def test_fia_ablation_validators_accept_weights_and_use_test_split():
    for relative_path in ("val_fia.py", "val_fdr_fia.py"):
        source = _read(relative_path)
        compile(source, relative_path, "exec")
        assert '"--weights"' in source
        assert "required=True" in source
        assert "20260815" not in source
        assert 'split="test"' in source


def test_visdrone_config_uses_repository_relative_dataset_root():
    data = _read("configs/VisDrone.yaml")
    assert data.splitlines()[0] == "path: VisDrone"
