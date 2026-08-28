# VisDrone Weight Asset Delivery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `subagent-driven-development` (recommended) or `executing-plans` to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the real VisDrone initial-state checkpoint as a verified public
GitHub Release asset and make the experiment handoff download, verify, and
classify it correctly on any server.

**Architecture:** Discover the exact file from the active run authority, verify
both raw bytes and canonical FDR tensor fingerprints, then upload a hash-bound
asset to one immutable GitHub Release. The Markdown handoff becomes the human
and executable manifest; tests prevent missing URLs, false historical identity,
and bypassing the four-arm fallback.

**Tech Stack:** PowerShell, OpenSSH/SCP, GitHub CLI, Bash, Python 3.10, PyTorch,
pytest, GitHub Releases.

---

## File Map

- Modify `tests/test_lrs_fdr_material.py`: enforce the published asset contract.
- Modify `paper_material/experiments/VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md`:
  add the verified asset table, download/check commands, comparison class, and
  hard fallback.
- Create `paper_material/experiments/VISDRONE_WEIGHT_ASSETS.sha256`: release
  checksum manifest copied into the repository after the asset is known.
- External artifact: GitHub Release `visdrone-lrs-system-assets-v1`.

### Task 1: Add a failing material contract test

**Files:**

- Modify: `tests/test_lrs_fdr_material.py`

- [ ] **Step 1: Add the weight-delivery contract test**

Append this test, reusing the file's existing `MATERIAL` constant:

```python
import re


def test_visdrone_handoff_publishes_real_weight_delivery_contract() -> None:
    handoff = (
        MATERIAL / "experiments" / "VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md"
    ).read_text(encoding="utf-8")
    manifest = (
        MATERIAL / "experiments" / "VISDRONE_WEIGHT_ASSETS.sha256"
    ).read_text(encoding="utf-8")

    assert "visdrone-lrs-system-assets-v1" in handoff
    assert "STRICT_HISTORICAL" in handoff
    assert "STRICT_NEW_MATRIX" in handoff
    assert "HISTORICAL_UNAVAILABLE" in handoff
    assert "sha256sum -c -" in handoff
    assert "test ! -s \"$INITIAL_STATE.part\"" not in handoff
    assert re.search(
        r"https://github\.com/kkc236/icassp2027-fdr-bpdd-fia-material/"
        r"releases/download/visdrone-lrs-system-assets-v1/[a-z0-9._-]+\.pt",
        handoff,
    )
    assert re.fullmatch(
        r"[0-9A-F]{64}  visdrone-lrs-system-initial-state-[0-9a-f]{12}\.pt\n",
        manifest,
    )
    assert "missing historical LRS-FDR best disables the three-new-arm path" in handoff
```

- [ ] **Step 2: Run the new test and verify that it fails**

Run:

```powershell
python -m pytest -q tests/test_lrs_fdr_material.py `
  -k visdrone_handoff_publishes_real_weight_delivery_contract
```

Expected: one failure because the checksum manifest and real Release URL do not
yet exist.

- [ ] **Step 3: Commit the red test**

```powershell
git add -- tests/test_lrs_fdr_material.py
git commit -m "test: require downloadable VisDrone weight asset"
```

### Task 2: Resolve and classify the active initial-state artifact

**Files:**

- Read: active server run authority and process command line
- Read: `src/fdr_protocol.py`

- [ ] **Step 1: Bind the session-held SSH target without persisting credentials**

Set `TRAIN_HOST` and `TRAIN_USER` only in the active shell from the user-provided
connection details. Do not write their values to Git, Markdown, logs, or the
plan. Verify connectivity:

```powershell
ssh "$env:TRAIN_USER@$env:TRAIN_HOST" "hostname; id -un; date -Is"
```

Expected: one hostname, the expected Ubuntu user, and an ISO timestamp.

- [ ] **Step 2: Locate the exact initial-state path used by the active G arm**

Run read-only discovery over SSH:

```bash
set -euo pipefail
ps -eo pid=,args= | grep -E 'train_visdrone_lrs_system|train.*lrs.*bpdd' | grep -v grep
find /data/uav/runs -type f \( -name '*authority*.json' -o -name '*manifest*.json' \) \
  -print0 | xargs -0 grep -Il 'initial.state' | sort
```

Read the matching G authority and its launch command. Export the resolved file
as `ACTIVE_INITIAL_STATE`, then require:

```bash
test -f "$ACTIVE_INITIAL_STATE"
stat --printf='bytes=%s\n' "$ACTIVE_INITIAL_STATE"
sha256sum "$ACTIVE_INITIAL_STATE"
```

Expected: one regular file, a positive byte size, and one complete SHA-256.

- [ ] **Step 3: Search for an exact historical artifact before accepting a replacement**

Run:

```bash
set -euo pipefail
export HISTORICAL_INITIAL_SHA="51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D"
find /data/uav -type f \( -name '*.pt' -o -name '*.pth' \) -print0 \
  | while IFS= read -r -d '' candidate; do
      observed="$(sha256sum "$candidate" | awk '{print toupper($1)}')"
      if [ "$observed" = "$HISTORICAL_INITIAL_SHA" ]; then
        printf '%s\n' "$candidate"
      fi
    done
```

Expected: either one or more exact paths, or empty output. Empty output is
recorded as `HISTORICAL_UNAVAILABLE`; it is not treated as an error in the new
matrix.

- [ ] **Step 4: Validate the artifact and emit canonical fingerprints**

From the final source checkout containing `src/fdr_protocol.py`, run:

```bash
python - "$ACTIVE_INITIAL_STATE" <<'PY'
import json
import sys

import torch

from src.fdr_protocol import validate_fdr_initial_state

path = sys.argv[1]
artifact = torch.load(path, map_location="cpu", weights_only=False)
validate_fdr_initial_state(artifact)
print(json.dumps(artifact["fingerprints"], sort_keys=True, indent=2))
PY
```

Expected: exit code zero and a JSON object containing the artifact's canonical
fingerprints.

- [ ] **Step 5: Assign the comparison class**

Use only these deterministic rules:

- raw SHA equals `51AAB2...` and validation passed: `STRICT_HISTORICAL`;
- raw SHA differs, all frozen historical fingerprints are available and equal:
  `TENSOR_EQUIVALENT_ONLY`;
- otherwise, if every new arm uses the same raw SHA and fingerprints:
  `STRICT_NEW_MATRIX`;
- otherwise: `NON_STRICT` and stop before publishing a training route.

Do not classify a replacement as historically strict from matching source,
seed, or configuration alone.

### Task 3: Publish and independently verify the Release asset

**Files:**

- Create: `paper_material/experiments/VISDRONE_WEIGHT_ASSETS.sha256`
- External: GitHub Release `visdrone-lrs-system-assets-v1`

- [ ] **Step 1: Copy the verified source to a local staging directory**

Create a dedicated non-repository directory and copy without altering the
server source:

```powershell
$stage = Join-Path $env:TEMP 'visdrone-lrs-weight-assets-v1'
New-Item -ItemType Directory -Force -Path $stage | Out-Null
scp "$env:TRAIN_USER@$env:TRAIN_HOST`:$env:ACTIVE_INITIAL_STATE" $stage
```

Calculate `$actualSha`, `$sha12`, `$assetName`, and `$assetPath` from the copied
file:

```powershell
$copied = Get-ChildItem -LiteralPath $stage -File | Select-Object -First 1
$actualSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $copied.FullName).Hash
$sha12 = $actualSha.Substring(0, 12).ToLowerInvariant()
$assetName = "visdrone-lrs-system-initial-state-$sha12.pt"
$assetPath = Join-Path $stage $assetName
Move-Item -LiteralPath $copied.FullName -Destination $assetPath
```

Expected: `$actualSha` exactly equals the server-observed raw SHA.

- [ ] **Step 2: Create the release if absent**

```powershell
$repo = 'kkc236/icassp2027-fdr-bpdd-fia-material'
$tag = 'visdrone-lrs-system-assets-v1'
gh release view $tag --repo $repo 2>$null
if ($LASTEXITCODE -ne 0) {
  gh release create $tag --repo $repo `
    --title 'VisDrone LRS system weight assets v1' `
    --notes 'Verified checkpoint assets for the frozen VisDrone LRS-FDR/BPDD/FIA handoff.'
}
```

Expected: `gh release view` succeeds after the block.

- [ ] **Step 3: Refuse an ambiguous collision and upload the asset**

Query an existing same-name asset. If present, compare its byte size and a fresh
downloaded SHA; stop on any difference. If absent, run:

```powershell
gh release upload $tag $assetPath --repo $repo
```

Expected: GitHub reports one uploaded asset with the exact hash-bound name.

- [ ] **Step 4: Write the repository checksum manifest**

First generate and validate the exact line:

```powershell
$manifestLine = "$actualSha  $assetName"
if ($manifestLine -notmatch '^[0-9A-F]{64}  visdrone-lrs-system-initial-state-[0-9a-f]{12}\.pt$') {
  throw 'invalid weight manifest line'
}
$manifestLine
```

Use `apply_patch` to create
`paper_material/experiments/VISDRONE_WEIGHT_ASSETS.sha256` with exactly the
printed line plus one final newline. No template token is committed.

- [ ] **Step 5: Independently download and verify the public asset**

```powershell
$verifyDir = Join-Path $env:TEMP 'visdrone-lrs-weight-assets-v1-verify'
New-Item -ItemType Directory -Force -Path $verifyDir | Out-Null
gh release download $tag --repo $repo --pattern $assetName --dir $verifyDir
$downloaded = Join-Path $verifyDir $assetName
$downloadedSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $downloaded).Hash
if ($downloadedSha -ne $actualSha) { throw 'release download SHA-256 mismatch' }
```

Expected: no exception and exact source/download SHA equality.

### Task 4: Make the Markdown executable and comparison-safe

**Files:**

- Modify: `paper_material/experiments/VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md`

- [ ] **Step 1: Add the verified asset manifest section**

Immediately after section 5.2, add section `5.2.1 权重资产交付` containing:

- release tag;
- actual asset name, byte size, full raw SHA, public URL, destination;
- the canonical fingerprints JSON from Task 2;
- the assigned comparison class;
- historical `51AAB2...` availability;
- historical `BA5CDFFE...` status `HISTORICAL_UNAVAILABLE` unless exact bytes
  have been found and verified.

- [ ] **Step 2: Add download-before-train commands with atomic promotion**

Use the actual URL and actual SHA from Task 3 in this structure:

```bash
set -euo pipefail

export MATERIAL_ROOT="/data/uav/material/icassp2027-fdr-bpdd-fia-material"
export WEIGHT_MANIFEST="$MATERIAL_ROOT/paper_material/experiments/VISDRONE_WEIGHT_ASSETS.sha256"
export INITIAL_STATE="/data/uav/pretrained/visdrone-lrs-system-initial-state.pt"
read -r INITIAL_STATE_SHA256 INITIAL_STATE_ASSET < "$WEIGHT_MANIFEST"
export INITIAL_STATE_URL="https://github.com/kkc236/icassp2027-fdr-bpdd-fia-material/releases/download/visdrone-lrs-system-assets-v1/$INITIAL_STATE_ASSET"

mkdir -p "$(dirname "$INITIAL_STATE")"
curl --fail --location --retry 3 --output "$INITIAL_STATE.part" "$INITIAL_STATE_URL"
printf '%s  %s\n' "$INITIAL_STATE_SHA256" "$INITIAL_STATE.part" | sha256sum -c -
mv "$INITIAL_STATE.part" "$INITIAL_STATE"
test "$(sha256sum "$INITIAL_STATE" | awk '{print toupper($1)}')" = \
  "$INITIAL_STATE_SHA256"
```

The same section also includes the literal public URL returned by the GitHub API
as a clickable Markdown link. The executable block obtains the name and hash
from the committed checksum manifest so that its two identity values cannot
drift independently.

- [ ] **Step 3: Disable invalid historical fallback explicitly**

Add this exact English contract sentence for the machine test and a Chinese
explanation beside it:

```text
missing historical LRS-FDR best disables the three-new-arm path
```

State that the new four-arm matrix must use the published replacement asset in
all arms when the old best is unavailable. Do not describe those runs as
`STRICT_HISTORICAL` unless Task 2 proved exact raw identity.

- [ ] **Step 4: Remove the obsolete unconditional historical hash assertion**

The startup section must select the expected SHA from the verified asset table.
It must not continue to require `51AAB2...` when the only published route is a
different replacement asset. Preserve `51AAB2...` only in the historical row.

### Task 5: Verify, commit, and publish the handoff

**Files:**

- Test: `tests/test_lrs_fdr_material.py`
- Verify: all modified documentation and checksum files

- [ ] **Step 1: Run the focused red test and material suite**

```powershell
python -m pytest -q tests/test_lrs_fdr_material.py `
  tests/test_material_integrity.py `
  tests/test_dfine_equal_fia_material.py `
  tests/test_equal_material.py
```

Expected: all collected tests pass.

- [ ] **Step 2: Syntax-check every Bash block in the handoff**

Extract each fenced Bash block in PowerShell and pipe it to
`C:\Program Files\Git\bin\bash.exe -n`. Expected: every block exits zero.

- [ ] **Step 3: Run integrity and secret checks**

```powershell
git diff --check
rg -n 'github_pat_[A-Za-z0-9_]{40,}|ghp_[A-Za-z0-9]{36,}' `
  paper_material/experiments/VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md `
  paper_material/experiments/VISDRONE_WEIGHT_ASSETS.sha256
```

Expected: `git diff --check` exits zero and the credential scan prints nothing.

- [ ] **Step 4: Commit only the intended files**

```powershell
git add -- tests/test_lrs_fdr_material.py `
  paper_material/experiments/VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md `
  paper_material/experiments/VISDRONE_WEIGHT_ASSETS.sha256
git commit -m "docs: publish verified VisDrone weight asset"
```

- [ ] **Step 5: Push and verify local/remote identity**

```powershell
git push private-material HEAD:codex/lrs-fdr-material-freeze
$local = (git rev-parse HEAD).Trim()
$line = git ls-remote private-material refs/heads/codex/lrs-fdr-material-freeze
$remote = ($line -split '\s+')[0].Trim()
if ($local -ne $remote) { throw 'remote branch mismatch' }
if (git status --porcelain) { throw 'worktree is not clean' }
```

Expected: local and remote commits match and the worktree is clean.
