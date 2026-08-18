"""Local SFTP-to-GitHub relay for the frozen ACR-BPDD Formal100 run.

The paid RTX4090 server trains without waiting on GitHub's slow direct upload.
This operations-only process verifies every queue path and SHA256, downloads
the exact checkpoint over SFTP, uploads it with the canonical Release asset
name, then asks the frozen server publisher to create and verify its manifest
and append-only ledger from an immutable queue-prefix snapshot.
"""

from __future__ import annotations

import hashlib
import json
import msvcrt
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path


HOST = "36.103.236.222"
USER = "ubuntu"
KEY = Path(r"C:\Users\16946\.ssh\bpdd_36_103_177_173_ed25519")
KNOWN_HOSTS = Path(r"C:\Users\16946\.ssh\bpdd_known_hosts")
ROOT = Path(__file__).resolve().parent / "acr-bpdd-relay-07d900d3"
REMOTE_RUN = Path(
    "/data/uav/runs/acr-bpdd-formal-07d900d3/"
    "formal-seed0-fdr_acr_bpdd-v1"
)
REMOTE_QUEUE = Path(
    "/data/uav/publication/acr-bpdd-formal-07d900d3/queue.jsonl"
)
REMOTE_RELAY_QUEUE = REMOTE_QUEUE.with_name("relay-queue.jsonl")
REMOTE_STATUS = Path(
    "/data/uav/logs/acr-bpdd-formal-07d900d3/sync-status.json"
)
REMOTE_SOURCE = Path("/data/uav/source/uav-detection-baselines-07d900d3")
REMOTE_PYTHON = Path("/data/uav/venvs/iber-be-v1/bin/python")
REMOTE_TOKEN = Path("/data/uav/secrets/github_material_token")
REPO = "kkc236/icassp2027-fdr-bpdd-fia-material"
TAG = "acr-bpdd-formal-07d900d3-live"
BRANCH = "codex/acr-bpdd-formal-20260817"
PREFIX = "acr-bpdd-07d900d3"
TARGET_EPOCHS = 100
POLL_SECONDS = 20


class AuthorityViolation(ValueError):
    """Irrecoverable evidence-contract violation; retrying cannot repair it."""


def executable(name: str) -> str:
    value = shutil.which(name)
    if value is None:
        raise FileNotFoundError(f"required executable not found: {name}")
    return value


SSH = executable("ssh.exe")
SCP = executable("scp.exe")
SFTP = executable("sftp.exe")
GH = executable("gh.exe")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def run(
    command: list[str], *, timeout: int = 600, capture: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        timeout=timeout,
        creationflags=NO_WINDOW,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()[-1200:]
        raise RuntimeError(
            f"command failed ({result.returncode}): {command[0]}: {detail}"
        )
    return result


def ssh_args() -> list[str]:
    return [
        SSH,
        "-i",
        str(KEY),
        "-o",
        f"UserKnownHostsFile={KNOWN_HOSTS}",
        "-o",
        "StrictHostKeyChecking=yes",
        "-o",
        "BatchMode=yes",
        f"{USER}@{HOST}",
    ]


def scp_args() -> list[str]:
    return [
        SCP,
        "-i",
        str(KEY),
        "-o",
        f"UserKnownHostsFile={KNOWN_HOSTS}",
        "-o",
        "StrictHostKeyChecking=yes",
        "-o",
        "BatchMode=yes",
    ]


def sftp_args() -> list[str]:
    return [
        SFTP,
        "-i",
        str(KEY),
        "-o",
        f"UserKnownHostsFile={KNOWN_HOSTS}",
        "-o",
        "StrictHostKeyChecking=yes",
        "-o",
        "BatchMode=yes",
    ]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def download_checkpoint(row: dict, destination: Path) -> None:
    """Resume an interrupted checkpoint transfer and verify it before promotion."""

    temporary = destination.with_suffix(".pt.download")
    batch = destination.with_suffix(".pt.sftp-batch")
    batch.write_text(
        f'reget "{row["checkpoint"]}" "{temporary.as_posix()}"\n',
        encoding="utf-8",
    )
    atomic_status({"state": "downloading", "epoch": int(row["completed_epoch"])})
    try:
        run(
            [*sftp_args(), "-b", str(batch), f"{USER}@{HOST}"],
            timeout=300,
        )
    finally:
        batch.unlink(missing_ok=True)
    actual = sha256(temporary)
    expected = str(row["checkpoint_sha256"]).upper()
    if actual != expected:
        temporary.unlink(missing_ok=True)
        raise ValueError(
            "downloaded checkpoint SHA256 mismatch at epoch "
            f"{row['completed_epoch']}: {actual}"
        )
    os.replace(temporary, destination)


def atomic_status(payload: dict) -> None:
    destination = ROOT / "relay-status.json"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, destination)


def fetch_queue() -> list[dict]:
    temporary = ROOT / "queue.snapshot.tmp"
    destination = ROOT / "queue.snapshot.jsonl"
    run(
        [
            *scp_args(),
            f"{USER}@{HOST}:{REMOTE_QUEUE.as_posix()}",
            str(temporary),
        ],
        timeout=60,
    )
    os.replace(temporary, destination)
    rows = [json.loads(line) for line in destination.read_text().splitlines() if line]
    if len(rows) > TARGET_EPOCHS:
        raise AuthorityViolation(
            f"publication queue exceeds target epochs: {len(rows)} > {TARGET_EPOCHS}"
        )
    for expected, row in enumerate(rows, 1):
        if int(row.get("completed_epoch", -1)) != expected:
            raise ValueError(f"non-contiguous queue at epoch {expected}")
        expected_path = REMOTE_RUN / "weights" / f"epoch{expected - 1}.pt"
        if Path(str(row.get("checkpoint"))) != expected_path:
            raise ValueError(f"unexpected checkpoint path at epoch {expected}")
        value = str(row.get("checkpoint_sha256", "")).upper()
        if not re.fullmatch(r"[0-9A-F]{64}", value):
            raise ValueError(f"invalid checkpoint SHA256 at epoch {expected}")
        if row.get("status") != "pending":
            raise ValueError(f"unexpected queue status at epoch {expected}")
    return rows


def ensure_release() -> None:
    """Create the relay Release, or tolerate a concurrent creator."""

    view_command = [GH, "api", f"repos/{REPO}/releases/tags/{TAG}"]
    try:
        run(view_command, timeout=60)
        return
    except RuntimeError:
        pass

    try:
        run(
            [
                GH,
                "release",
                "create",
                TAG,
                "--repo",
                REPO,
                "--title",
                TAG,
                "--notes",
                "Live ACR-BPDD checkpoint relay.",
            ],
            timeout=60,
        )
    except RuntimeError as create_error:
        # Another relay may have won the create race. Accept that only after
        # independently confirming the Release now exists.
        try:
            run(view_command, timeout=60)
        except RuntimeError:
            raise create_error


def release_assets() -> dict[str, dict]:
    ensure_release()
    result = run(
        [GH, "api", f"repos/{REPO}/releases/tags/{TAG}"],
        timeout=60,
    )
    payload = json.loads(result.stdout)
    return {str(item["name"]): dict(item) for item in payload["assets"]}


def checkpoint_asset(epoch: int) -> str:
    return f"{PREFIX}-epoch-{epoch:04d}.pt"


def checkpoint_sidecar(epoch: int) -> str:
    return f"{PREFIX}-epoch-{epoch:04d}.json"


def asset_size(asset: object) -> int:
    if isinstance(asset, dict):
        return int(asset.get("size", -1))
    return int(asset)


def asset_sha256(asset: object) -> str | None:
    if not isinstance(asset, dict):
        return None
    value = str(asset.get("digest", "")).strip()
    if value.lower().startswith("sha256:"):
        value = value.split(":", 1)[1]
    value = value.upper()
    return value if re.fullmatch(r"[0-9A-F]{64}", value) else None


def fetch_checkpoint_sidecar(epoch: int, assets: dict[str, object]) -> dict | None:
    name = checkpoint_sidecar(epoch)
    if name not in assets:
        return None
    temporary = ROOT / f".{name}.download"
    temporary.unlink(missing_ok=True)
    try:
        run(
            [
                GH,
                "release",
                "download",
                TAG,
                "--repo",
                REPO,
                "--pattern",
                name,
                "--output",
                str(temporary),
            ],
            timeout=60,
        )
        try:
            payload = json.loads(temporary.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return payload if isinstance(payload, dict) else None
    finally:
        temporary.unlink(missing_ok=True)


def downloaded_release_asset_sha256(name: str) -> str:
    if not re.fullmatch(rf"{re.escape(PREFIX)}-epoch-\d{{4}}\.pt", name):
        raise ValueError(f"refusing to download unexpected Release asset: {name}")
    temporary = ROOT / f".{name}.verify"
    temporary.unlink(missing_ok=True)
    try:
        run(
            [
                GH,
                "release",
                "download",
                TAG,
                "--repo",
                REPO,
                "--pattern",
                name,
                "--output",
                str(temporary),
            ],
            timeout=600,
        )
        return sha256(temporary)
    finally:
        temporary.unlink(missing_ok=True)


def existing_checkpoint_verified(row: dict, assets: dict[str, object]) -> bool:
    epoch = int(row["completed_epoch"])
    name = checkpoint_asset(epoch)
    asset = assets.get(name)
    if asset is None:
        return False
    expected_sha = str(row["checkpoint_sha256"]).upper()
    remote_sha = asset_sha256(asset)
    if remote_sha is not None:
        return asset_size(asset) > 0 and remote_sha == expected_sha
    manifest = fetch_checkpoint_sidecar(epoch, assets)
    if manifest is None:
        return False
    checkpoint = manifest.get("checkpoint")
    if not isinstance(checkpoint, dict):
        return False
    try:
        manifest_epoch = int(manifest.get("completed_epoch", -1))
        manifest_size = int(checkpoint.get("bytes", -1))
    except (TypeError, ValueError):
        return False
    sidecar_matches = (
        manifest_epoch == epoch
        and checkpoint.get("asset_name") == name
        and str(checkpoint.get("sha256", "")).upper()
        == expected_sha
        and manifest_size > 0
        and asset_size(asset) == manifest_size
    )
    if not sidecar_matches:
        return False
    return downloaded_release_asset_sha256(name) == expected_sha


def delete_release_asset(name: str) -> None:
    if not re.fullmatch(rf"{re.escape(PREFIX)}-epoch-\d{{4}}\.(?:pt|json)", name):
        raise ValueError(f"refusing to delete unexpected Release asset: {name}")
    run(
        [GH, "release", "delete-asset", TAG, name, "--repo", REPO, "--yes"],
        timeout=60,
    )


def ensure_checkpoint(row: dict, assets: dict[str, object]) -> None:
    epoch = int(row["completed_epoch"])
    name = checkpoint_asset(epoch)
    sidecar_name = checkpoint_sidecar(epoch)
    if existing_checkpoint_verified(row, assets):
        return
    destination = ROOT / name
    expected_sha = str(row["checkpoint_sha256"]).upper()
    if not destination.is_file() or sha256(destination) != expected_sha:
        download_checkpoint(row, destination)
    for stale_name in (name, sidecar_name):
        if stale_name in assets:
            delete_release_asset(stale_name)
    atomic_status({"state": "uploading", "epoch": epoch})
    run(
        [
            GH,
            "release",
            "upload",
            TAG,
            str(destination),
            "--repo",
            REPO,
            "--clobber",
        ],
        timeout=600,
    )
    refreshed = release_assets()
    uploaded = refreshed.get(name)
    if uploaded is None or asset_size(uploaded) != destination.stat().st_size:
        raise RuntimeError(f"GitHub checkpoint size mismatch at epoch {epoch}")
    if asset_sha256(uploaded) != expected_sha:
        if downloaded_release_asset_sha256(name) != expected_sha:
            raise RuntimeError(f"GitHub checkpoint SHA256 mismatch at epoch {epoch}")


def validated_ledger_epochs(rows: list[dict], records: list[dict]) -> set[int]:
    if len(rows) > TARGET_EPOCHS or len(records) > TARGET_EPOCHS:
        raise AuthorityViolation(
            "publication evidence exceeds target epochs: "
            f"queue={len(rows)}, ledger={len(records)}, target={TARGET_EPOCHS}"
        )
    if len(records) > len(rows):
        raise ValueError(
            f"remote ledger has {len(records)} records, expected {len(rows)}"
        )

    verified_epochs: set[int] = set()
    for expected_epoch, (row, record) in enumerate(zip(rows, records), 1):
        if int(row.get("completed_epoch", -1)) != expected_epoch:
            raise ValueError(f"queue epoch mismatch at epoch {expected_epoch}")
        if int(record.get("completed_epoch", -1)) != expected_epoch:
            raise ValueError(f"ledger epoch mismatch at epoch {expected_epoch}")

        if record.get("verified") is not True:
            raise ValueError(
                f"ledger publication is not verified at epoch {expected_epoch}"
            )
        success_values = {
            "complete",
            "completed",
            "ok",
            "published",
            "success",
            "succeeded",
            "verified",
        }
        for key in ("status", "state"):
            if key in record and str(record[key]).strip().lower() not in success_values:
                raise ValueError(
                    f"ledger publication is not verified at epoch {expected_epoch}"
                )

        checkpoint = record.get("checkpoint")
        if not isinstance(checkpoint, dict):
            raise ValueError(
                f"ledger checkpoint metadata missing at epoch {expected_epoch}"
            )
        expected_name = checkpoint_asset(expected_epoch)
        if checkpoint.get("asset_name") != expected_name:
            raise ValueError(
                f"ledger checkpoint asset name mismatch at epoch {expected_epoch}"
            )
        ledger_sha = str(checkpoint.get("sha256", "")).upper()
        queue_sha = str(row.get("checkpoint_sha256", "")).upper()
        if ledger_sha != queue_sha:
            raise ValueError(
                f"ledger checkpoint SHA256 mismatch at epoch {expected_epoch}"
            )
        verified_epochs.add(expected_epoch)
    return verified_epochs


def fetch_validated_ledger(rows: list[dict]) -> list[dict]:
    temporary = ROOT / "publication-ledger.snapshot.tmp"
    destination = ROOT / "publication-ledger.snapshot.jsonl"
    temporary.unlink(missing_ok=True)
    run(
        [
            *scp_args(),
            f"{USER}@{HOST}:{(REMOTE_RUN / 'publication-ledger.jsonl').as_posix()}",
            str(temporary),
        ],
        timeout=60,
    )
    os.replace(temporary, destination)
    records = [
        json.loads(line)
        for line in destination.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    validated_ledger_epochs(rows, records)
    return records


def publish_queue_prefix(rows: list[dict]) -> list[dict]:
    snapshot = ROOT / "queue.snapshot.jsonl"
    run(
        [
            *scp_args(),
            str(snapshot),
            f"{USER}@{HOST}:{REMOTE_RELAY_QUEUE.as_posix()}",
        ],
        timeout=60,
    )
    script = REMOTE_SOURCE / "scripts" / "sync_bpdd_publication_queue.py"
    parts = [
        REMOTE_PYTHON.as_posix(),
        script.as_posix(),
        "--queue",
        REMOTE_RELAY_QUEUE.as_posix(),
        "--token-file",
        REMOTE_TOKEN.as_posix(),
        "--repo",
        REPO,
        "--tag",
        TAG,
        "--branch",
        BRANCH,
        "--asset-prefix",
        PREFIX,
        "--run-dir",
        REMOTE_RUN.as_posix(),
        "--interval",
        "60",
        "--local-retain",
        "3",
        "--once",
        "--status-file",
        REMOTE_STATUS.as_posix(),
    ]
    command = "cd " + shlex.quote(REMOTE_SOURCE.as_posix()) + " && " + " ".join(
        shlex.quote(part) for part in parts
    )
    run([*ssh_args(), command], timeout=300)
    return fetch_validated_ledger(rows)


def clean_local_verified(rows: list[dict], records: list[dict]) -> None:
    verified_epochs = validated_ledger_epochs(rows, records)
    root = ROOT.resolve()
    for path in ROOT.glob(f"{PREFIX}-epoch-*.pt"):
        match = re.fullmatch(rf"{re.escape(PREFIX)}-epoch-(\d{{4}})\.pt", path.name)
        if not match or int(match.group(1)) not in verified_epochs:
            continue
        if path.resolve().parent != root:
            raise RuntimeError("refusing to remove checkpoint outside relay root")
        path.unlink()


def acquire_lock():
    lock = (ROOT / "relay.lock").open("a+b")
    if lock.tell() == 0:
        lock.write(b"0")
        lock.flush()
    lock.seek(0)
    try:
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError as error:
        raise RuntimeError("another relay process is already running") from error
    return lock


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    lock = acquire_lock()
    (ROOT / "relay.pid").write_text(str(os.getpid()) + "\n")
    while True:
        try:
            rows = fetch_queue()
            assets = release_assets()
            for row in rows:
                ensure_checkpoint(row, assets)
                assets = release_assets()
            ledger = publish_queue_prefix(rows) if rows else []
            clean_local_verified(rows, ledger)
            atomic_status(
                {
                    "state": "verified",
                    "queued_epochs": len(rows),
                    "ledger_records": len(ledger),
                }
            )
            if len(rows) == TARGET_EPOCHS and len(ledger) == TARGET_EPOCHS:
                return
        except AuthorityViolation as error:
            atomic_status(
                {"state": "failed", "error": f"{type(error).__name__}: {error}"}
            )
            raise
        except Exception as error:
            atomic_status({"state": "retrying", "error": f"{type(error).__name__}: {error}"})
            print(f"relay retrying: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
        time.sleep(POLL_SECONDS)
    lock.close()


if __name__ == "__main__":
    main()
