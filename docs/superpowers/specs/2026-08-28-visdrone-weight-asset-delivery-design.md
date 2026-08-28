# VisDrone Weight Asset Delivery Design

**Date:** 2026-08-28

**Status:** Approved approach; awaiting written-spec review

**Target repository:** `kkc236/icassp2027-fdr-bpdd-fia-material`

**Target branch:** `codex/lrs-fdr-material-freeze`

## Goal

Make every weight referenced by
`paper_material/experiments/VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md` retrievable
or explicitly unavailable. A new server must be able to download a real asset,
verify its SHA-256, and stop before training if the required bytes are absent or
incorrect.

## Current Evidence

- The material repository and its GitHub Releases contain no asset matching the
  historical formal initial-state SHA-256
  `51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D`.
- They also contain no asset matching the historical LRS-FDR best SHA-256
  `BA5CDFFE8E2A0E147CE0D6D30CCBD3A0D25E31A7DCF69F8B247D2A079B492DFA`.
- The active server reportedly created a replacement initial state and started
  the G arm from it. That file is the only immediately uploadable candidate,
  subject to server-side existence and hash verification.
- The historical hashes remain provenance records. They must not be reassigned
  to replacement files.

## Chosen Design

Use public GitHub Release assets for large binary weights and keep the Markdown
file as the authoritative asset manifest. Do not commit checkpoint binaries to
normal Git history and do not create a Git LFS dependency.

Create or reuse one release tag:

`visdrone-lrs-system-assets-v1`

Asset names bind role and actual hash prefix. Construct the initial-state name by
appending the first 12 lowercase SHA-256 characters and `.pt` to
`visdrone-lrs-system-initial-state-`; construct the control name in the same way
from `visdrone-lrs-fdr-seed0-best-`.

The second asset is published only after a same-protocol LRS-FDR control run
finishes. The unavailable historical `BA5CDFFE...` file is never replaced under
the same identity.

## Asset Manifest Contract

For every asset, the handoff Markdown records:

- semantic role;
- protocol generation (`historical` or `replacement-v1`);
- exact file name;
- byte size;
- complete SHA-256;
- immutable GitHub Release download URL;
- expected server destination;
- one download command;
- one SHA-256 verification command;
- availability state: `AVAILABLE`, `PENDING_RETRAIN`, or
  `HISTORICAL_UNAVAILABLE`.

No row may contain a guessed URL, inherited size, shortened-only hash, or a path
that was not verified on the active server.

## Data Flow

1. Read the active run authority to resolve the replacement initial-state path.
2. Verify the file exists and calculate its actual byte size and SHA-256 on the
   server.
3. Ensure that all already-started replacement-protocol arms bind the same hash.
4. Transfer the file without renaming its identity prematurely.
5. Create the public release if absent and upload the hash-bound asset.
6. Query the GitHub Release API to verify asset name, byte size, and public URL.
7. Download the published asset to a separate temporary path and verify the
   complete SHA-256.
8. Update the handoff Markdown with the verified manifest row and executable
   download/check commands.
9. Mark the historical initial state and historical LRS-FDR best as
   `HISTORICAL_UNAVAILABLE` until their exact bytes are recovered.
10. Require a replacement-protocol LRS-FDR control run. After its val-selected
    best checkpoint exists, repeat steps 2-8 for the control asset.

## Training Gate

The handoff must make the following policy unambiguous:

- If the replacement initial-state asset is absent or its SHA differs, no arm
  may start.
- If the historical LRS-FDR best is absent, the compute-limited three-new-arm
  path is disabled.
- In that case the only valid path is a new four-arm matrix using the same
  replacement initial state: LRS-FDR, LRS-FDR+BPDD, LRS-FDR+FIA, and Full.
- G/H/I runs that use a different initial-state hash cannot be compared as a
  strict matrix.
- Dry-run does not replace default-off tensor parity or the real-batch smoke
  test.

## Security and Publication Boundary

- The release contains only model checkpoint bytes and a checksum manifest.
- It contains no PAT, SSH key, password, environment dump, dataset image,
  annotation, or private server path beyond the documented destination example.
- GitHub authentication uses the existing local `gh` credential. No credential
  is written into Markdown, commands, release notes, or shell history.
- The public repository and release are intentional user-authorized outputs.

## Failure Handling

- Missing server file: do not upload a substitute; report `UNAVAILABLE`.
- Hash mismatch: stop and preserve both observed and expected hashes in the
  audit note; do not rename the file to the expected hash.
- Release asset name collision: compare size and downloaded SHA before deciding;
  never overwrite silently.
- Interrupted upload: delete only the incomplete release asset after confirming
  the exact asset ID, then retry once from the verified local/server source.
- Post-upload verification failure: remove the failed asset, keep the Markdown
  unchanged, and report the failure.

## Verification

Completion requires fresh evidence for all of the following:

- target server source file exists;
- source SHA-256 and byte size recorded;
- GitHub API reports the expected asset name and size;
- a fresh download matches the source SHA-256;
- Markdown contains the real URL and full hash;
- credential scan is clean;
- all Bash code blocks pass `bash -n`;
- material integrity tests pass;
- Git worktree is clean after commit;
- local commit equals the remote branch commit.

## Non-Goals

- Recovering the unavailable historical `51AAB2...` or `BA5CDFFE...` bytes by
  guessing or reconstructing their identity.
- Treating a replacement initial state as numerically identical to historical
  runs.
- Uploading the VisDrone dataset.
- Changing model architecture, training parameters, or experiment results.
