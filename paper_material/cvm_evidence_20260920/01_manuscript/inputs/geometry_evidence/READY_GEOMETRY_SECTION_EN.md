# Geometry: representability and observed corrections

We examine archived numerical regression records to separate geometric representability from detection accuracy. Under CPU bfloat16 autocast, a six-layer decoder-wrapper test with mocked edge distances of -4 produced zero decoded widths and heights in the pre-fix assertion output. The same named test passed after the precision-safe decoding revision, checking FP32 boxes, positive extents, and a successful backward pass. Separate post-fix tests cover nominal reference sizes of 0.1 and 1e-8 across float16, bfloat16, float32, and float64: all eight cases satisfy positive extents after corner conversion and finite-gradient checks. The float16 cast of 1e-8 underflows to zero, so this case probes underflow handling rather than a strictly positive represented reference. An additional float64 test checks that an ordinary feasible box is unchanged and that an asymmetric correction preserves its decoded center. These controlled tests exercise synthetic inputs and decoder fixtures; they establish the checked numerical properties, rather than an accuracy improvement or the frequency of failures in final detections. The archived reports identify the same regression test but do not preserve identical initial tensors for a paired numerical effect estimate.

## Optional separate training-context sentence

An archived training-diagnostic summary reports that, during epochs 91--100 of the LRS-GFDR base run, 0.004483% of horizontal and 0.005329% of vertical layer/query observations fell below the relative extent threshold. These pooled counts include all recorded query types and use a positive threshold; they are not strictly negative-size or final-detection failure rates. The original epoch logs were unavailable for recomputation in this revision.

## Source use notes

- Prefer the numerical regression paragraph as the main mechanism evidence. The optional training-context sentence is explicitly secondary evidence and can remain in supplementary provenance instead of the paper.
- `archived_correctness/red.xml`: BF16 same-name failure with zero extents; do not describe the missing-function failures of other tests as measured numerical failures.
- `archived_correctness/numerical.xml`: same BF16 test passes; no exact output sizes are persisted.
- `archived_correctness/regression-final.xml`: same tests pass again; 177 total tests, 0 failures/errors, 1 skipped, therefore 176 passed. Do not count all 176 as geometry tests.
- `source_f56b210/tests/test_fdr_feasible_geometry.py`: six-layer decoder wrapper uses identity decoder layers and mocked Integral output of -4 per edge; this is not a trained end-to-end detector evaluation.
- `source_f56b210/tests/test_no_server_correctness.py`: numerical-size/dtype cases and ordinary/asymmetric-box assertions.
- Commit: f56b210798acab96d628308a5127a2e1399d00dc. Hashes and temporal/source caveats: `geometry_evidence_manifest.json`.
- No new training, model inference, or synthetic numerical execution was performed; the preparation parsed existing records and froze existing source.
