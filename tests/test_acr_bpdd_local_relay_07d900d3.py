"""Static contract tests for the isolated ACR-BPDD 07d900d3 relay."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELAY = PROJECT_ROOT / "artifacts" / "acr_bpdd_local_relay_07d900d3.py"


def relay_source() -> str:
    assert RELAY.is_file(), f"missing relay script: {RELAY}"
    return RELAY.read_text(encoding="utf-8")


def static_assignments(source: str) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            assignments[target.id] = value.value
        elif (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "Path"
            and len(value.args) == 1
        ):
            assignments[target.id] = ast.literal_eval(value.args[0])
    return assignments


def load_relay(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(shutil, "which", lambda name: name)
    spec = importlib.util.spec_from_file_location("acr_bpdd_relay_under_test", RELAY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def queue_row(epoch: int, payload: bytes) -> dict:
    return {
        "completed_epoch": epoch,
        "checkpoint": f"/remote/weights/epoch{epoch - 1}.pt",
        "checkpoint_sha256": hashlib.sha256(payload).hexdigest().upper(),
        "status": "pending",
    }


def ledger_record(row: dict, asset_name: str) -> dict:
    return {
        "completed_epoch": row["completed_epoch"],
        "verified": True,
        "checkpoint": {
            "asset_name": asset_name,
            "sha256": row["checkpoint_sha256"].lower(),
        },
    }


def sidecar_record(row: dict, asset_name: str, size: int) -> dict:
    return {
        "completed_epoch": row["completed_epoch"],
        "checkpoint": {
            "asset_name": asset_name,
            "bytes": size,
            "sha256": row["checkpoint_sha256"].lower(),
        },
    }


def test_authority_constants_are_exact_and_isolated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = relay_source()
    assignments = static_assignments(source)
    assert assignments["REMOTE_RUN"] == (
        "/data/uav/runs/acr-bpdd-formal-07d900d3/"
        "formal-seed0-fdr_acr_bpdd-v1"
    )
    assert assignments["REMOTE_QUEUE"] == (
        "/data/uav/publication/acr-bpdd-formal-07d900d3/queue.jsonl"
    )
    assert assignments["REMOTE_STATUS"] == (
        "/data/uav/logs/acr-bpdd-formal-07d900d3/sync-status.json"
    )
    assert assignments["REMOTE_SOURCE"] == (
        "/data/uav/source/uav-detection-baselines-07d900d3"
    )
    assert assignments["TAG"] == "acr-bpdd-formal-07d900d3-live"
    assert assignments["PREFIX"] == "acr-bpdd-07d900d3"
    relay = load_relay(monkeypatch)
    assert relay.ROOT == (
        PROJECT_ROOT / "artifacts" / "acr-bpdd-relay-07d900d3"
    )
    assert "70d35fa6" not in source


def test_missing_release_has_create_and_race_recheck_path() -> None:
    tree = ast.parse(relay_source())
    ensure_release = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "ensure_release"
    )
    literals = [
        node.value
        for node in ast.walk(ensure_release)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    view_runs = [
        node
        for node in ast.walk(ensure_release)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "run"
        and node.args
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "view_command"
    ]
    assert "create" in literals
    assert len(view_runs) >= 2
    assert any(isinstance(node, ast.ExceptHandler) for node in ast.walk(ensure_release))


def test_release_discovery_uses_rest_api_instead_of_graphql(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    relay = load_relay(monkeypatch)
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, '{"assets": []}', "")

    monkeypatch.setattr(relay, "run", fake_run)
    assert relay.release_assets() == {}
    assert calls
    assert all(command[:2] == [relay.GH, "api"] for command in calls)


def test_relay_does_not_read_secrets_or_manage_training() -> None:
    source = relay_source()
    assert "REMOTE_TOKEN.read_text" not in source
    assert "github_material_token).read" not in source
    for forbidden in ("pkill", "killall", "train_rtdetr_", "nvidia-smi"):
        assert forbidden not in source


def test_matching_ledger_snapshot_is_parsed_before_local_checkpoint_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"verified-checkpoint"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    local_checkpoint = tmp_path / name
    local_checkpoint.write_bytes(payload)
    record = ledger_record(row, name)

    def fake_run(command: list[str], **_kwargs):
        Path(command[-1]).write_text(json.dumps(record) + "\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(relay, "run", fake_run)
    records = relay.fetch_validated_ledger([row])
    relay.clean_local_verified([row], records)

    assert records == [record]
    assert not local_checkpoint.exists()


@pytest.mark.parametrize(
    "failure_marker",
    [
        {"verified": False},
        {"status": "failed"},
        {"state": "retrying"},
    ],
)
def test_unsuccessful_ledger_record_is_rejected_and_local_checkpoint_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_marker: dict,
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"unverified-checkpoint"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    local_checkpoint = tmp_path / name
    local_checkpoint.write_bytes(payload)
    record = ledger_record(row, name)
    record.update(failure_marker)

    with pytest.raises(ValueError, match="ledger publication is not verified"):
        relay.clean_local_verified([row], [record])

    assert local_checkpoint.read_bytes() == payload


def test_ledger_status_without_explicit_verified_true_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"status-only-is-not-authority"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    local_checkpoint = tmp_path / name
    local_checkpoint.write_bytes(payload)
    record = ledger_record(row, name)
    record.pop("verified")
    record["status"] = "verified"

    with pytest.raises(ValueError, match="ledger publication is not verified"):
        relay.clean_local_verified([row], [record])

    assert local_checkpoint.read_bytes() == payload


def test_short_verified_ledger_prefix_deletes_only_its_matching_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    rows = [queue_row(1, b"epoch-one"), queue_row(2, b"epoch-two")]
    checkpoints = []
    for row in rows:
        checkpoint = tmp_path / relay.checkpoint_asset(row["completed_epoch"])
        checkpoint.write_bytes(f"epoch-{row['completed_epoch']}".encode())
        checkpoints.append(checkpoint)

    relay.clean_local_verified(
        rows,
        [ledger_record(rows[0], relay.checkpoint_asset(1))],
    )

    assert not checkpoints[0].exists()
    assert checkpoints[1].is_file()


@pytest.mark.parametrize(
    ("corruption", "message"),
    [
        ("epoch", "ledger epoch mismatch"),
        ("asset", "ledger checkpoint asset name mismatch"),
        ("sha256", "ledger checkpoint SHA256 mismatch"),
    ],
)
def test_mismatched_ledger_record_preserves_local_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    corruption: str,
    message: str,
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"checkpoint-to-preserve"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    local_checkpoint = tmp_path / name
    local_checkpoint.write_bytes(payload)
    record = ledger_record(row, name)
    if corruption == "epoch":
        record["completed_epoch"] = 2
    elif corruption == "asset":
        record["checkpoint"]["asset_name"] = "wrong-epoch-0001.pt"
    else:
        record["checkpoint"]["sha256"] = "F" * 64

    with pytest.raises(ValueError, match=message):
        relay.clean_local_verified([row], [record])

    assert local_checkpoint.read_bytes() == payload


def test_wrong_size_existing_asset_is_downloaded_and_reuploaded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"canonical-checkpoint-content"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    sidecar_name = relay.checkpoint_sidecar(1)
    calls: list[list[str]] = []
    downloads: list[tuple[int, Path]] = []

    def fake_download(row_arg: dict, destination: Path) -> None:
        downloads.append((int(row_arg["completed_epoch"]), destination))
        destination.write_bytes(payload)

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        if command[:3] == [relay.GH, "release", "download"]:
            output = Path(command[command.index("--output") + 1])
            output.write_text(
                json.dumps(sidecar_record(row, name, len(payload))),
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(relay, "run", fake_run)
    monkeypatch.setattr(relay, "download_checkpoint", fake_download)
    monkeypatch.setattr(
        relay,
        "release_assets",
        lambda: {
            name: {
                "id": 11,
                "name": name,
                "size": len(payload),
                "digest": f"sha256:{row['checkpoint_sha256'].lower()}",
            }
        },
    )
    relay.ensure_checkpoint(
        row,
        {
            name: {"id": 11, "name": name, "size": 1},
            sidecar_name: {"id": 12, "name": sidecar_name, "size": 200},
        },
    )

    local_checkpoint = tmp_path / name
    assert local_checkpoint.read_bytes() == payload
    assert downloads == [(1, local_checkpoint)]
    deleted_names = [
        command[4]
        for command in calls
        if command[:3] == [relay.GH, "release", "delete-asset"]
    ]
    assert deleted_names == [name, sidecar_name]
    assert any(
        command[:3] == [relay.GH, "release", "upload"] and "--clobber" in command
        for command in calls
    )


def test_checkpoint_download_resumes_existing_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"complete-resumable-checkpoint"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    destination = tmp_path / name
    partial = destination.with_suffix(".pt.download")
    partial.write_bytes(payload[:9])
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        if command[0] == relay.SFTP:
            assert partial.read_bytes() == payload[:9]
            partial.write_bytes(payload)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(relay, "run", fake_run)
    relay.download_checkpoint(row, destination)

    assert destination.read_bytes() == payload
    assert any(command[0] == relay.SFTP for command in calls)


def test_matching_existing_asset_requires_size_and_sidecar_sha(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"already-published-checkpoint"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    sidecar_name = relay.checkpoint_sidecar(1)
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        if command[:3] == [relay.GH, "release", "download"]:
            output = Path(command[command.index("--output") + 1])
            pattern = command[command.index("--pattern") + 1]
            if pattern.endswith(".json"):
                output.write_text(
                    json.dumps(sidecar_record(row, name, len(payload))),
                    encoding="utf-8",
                )
            else:
                output.write_bytes(payload)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(relay, "run", fake_run)
    relay.ensure_checkpoint(
        row,
        {
            name: {"id": 21, "name": name, "size": len(payload)},
            sidecar_name: {"id": 22, "name": sidecar_name, "size": 200},
        },
    )

    assert not any(command[0] == relay.SCP for command in calls)
    assert any(
        command[:3] == [relay.GH, "release", "download"]
        and command[command.index("--pattern") + 1] == name
        for command in calls
    )
    assert not any(command[:3] == [relay.GH, "release", "upload"] for command in calls)
    assert not any(
        command[:3] == [relay.GH, "release", "delete-asset"] for command in calls
    )


def test_matching_existing_asset_uses_remote_digest_without_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"digest-verified-checkpoint"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(relay, "run", fake_run)
    relay.ensure_checkpoint(
        row,
        {
            name: {
                "id": 41,
                "name": name,
                "size": len(payload),
                "digest": f"sha256:{row['checkpoint_sha256'].lower()}",
            }
        },
    )

    assert not calls


def test_same_size_wrong_remote_digest_forces_reupload_and_digest_recheck(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"canonical-after-wrong-digest"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    calls: list[list[str]] = []
    downloads: list[tuple[int, Path]] = []

    def fake_download(row_arg: dict, destination: Path) -> None:
        downloads.append((int(row_arg["completed_epoch"]), destination))
        destination.write_bytes(payload)

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(relay, "run", fake_run)
    monkeypatch.setattr(relay, "download_checkpoint", fake_download)
    monkeypatch.setattr(
        relay,
        "release_assets",
        lambda: {
            name: {
                "id": 51,
                "name": name,
                "size": len(payload),
                "digest": f"sha256:{row['checkpoint_sha256'].lower()}",
            }
        },
    )
    relay.ensure_checkpoint(
        row,
        {
            name: {
                "id": 50,
                "name": name,
                "size": len(payload),
                "digest": "sha256:" + "F" * 64,
            }
        },
    )

    assert downloads == [(1, tmp_path / name)]
    assert any(command[:3] == [relay.GH, "release", "upload"] for command in calls)


def test_sidecar_sha_conflict_replaces_only_same_epoch_assets_and_keeps_local_pt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)
    payload = b"local-canonical-checkpoint"
    row = queue_row(1, payload)
    name = relay.checkpoint_asset(1)
    sidecar_name = relay.checkpoint_sidecar(1)
    other_name = relay.checkpoint_asset(2)
    local_checkpoint = tmp_path / name
    local_checkpoint.write_bytes(payload)
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        if command[:3] == [relay.GH, "release", "download"]:
            output = Path(command[command.index("--output") + 1])
            invalid = sidecar_record(row, name, len(payload))
            invalid["checkpoint"]["sha256"] = "F" * 64
            output.write_text(json.dumps(invalid), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(relay, "run", fake_run)
    monkeypatch.setattr(
        relay,
        "release_assets",
        lambda: {
            name: {
                "id": 31,
                "name": name,
                "size": len(payload),
                "digest": f"sha256:{row['checkpoint_sha256'].lower()}",
            }
        },
    )
    relay.ensure_checkpoint(
        row,
        {
            name: {"id": 31, "name": name, "size": len(payload)},
            sidecar_name: {"id": 32, "name": sidecar_name, "size": 200},
            other_name: {"id": 33, "name": other_name, "size": 999},
        },
    )

    deleted_names = [
        command[4]
        for command in calls
        if command[:3] == [relay.GH, "release", "delete-asset"]
    ]
    assert deleted_names == [name, sidecar_name]
    assert other_name not in deleted_names
    assert local_checkpoint.read_bytes() == payload


def test_verified_ledger_rejects_more_than_target_epochs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    relay = load_relay(monkeypatch)
    rows = []
    records = []
    for epoch in range(1, relay.TARGET_EPOCHS + 2):
        row = queue_row(epoch, f"epoch-{epoch}".encode())
        rows.append(row)
        records.append(ledger_record(row, relay.checkpoint_asset(epoch)))

    with pytest.raises(ValueError, match="exceeds target epochs"):
        relay.validated_ledger_epochs(rows, records)


def test_main_hard_fails_authority_overflow_instead_of_retrying(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relay = load_relay(monkeypatch)
    monkeypatch.setattr(relay, "ROOT", tmp_path)

    class DummyLock:
        def close(self) -> None:
            pass

    monkeypatch.setattr(relay, "acquire_lock", lambda: DummyLock())
    monkeypatch.setattr(
        relay,
        "fetch_queue",
        lambda: (_ for _ in ()).throw(
            relay.AuthorityViolation("publication queue exceeds target epochs")
        ),
    )

    with pytest.raises(relay.AuthorityViolation, match="exceeds target epochs"):
        relay.main()
