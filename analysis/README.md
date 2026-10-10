# Reproduce the frozen audit

Run from the repository root with the original listed input bytes in an external
cache. The cache is read only. Neither this execution nor the verifier fetches a
leaderboard. See PREREG.md and feasibility.md for all authoritative rules.

```bash
python3 -m unittest tests.test_audit -v
python3 -m analysis.freeze
python3 -m analysis.run --cache ../data_cache
python3 -m tests.check_artifacts
```

The pre-execution freeze already exists in the delivered run. For reproduction,
preserve that file and run the analysis directly; freeze refuses to overwrite
an existing record. Changes to execution code require a separately documented
execution epoch and a new preserved hash record before any new formal run.

Dependencies are pinned in requirements.txt. CPython and NumPy mismatches stop
both bootstrap designs. pdftotext mismatch fails S5 extraction. Version records
and source extraction failures remain explicit rather than substituted.

path_a.py and path_b.py each parse the original JSON independently. A directly
accumulates task trials; B groups job tasks before accumulation. They share only
fixed IDs and domain constants. Pure display rules in tools/audit_rules.py are
used after counting, never as a shared summation function. Predictions reside in
predictions.py solely for post-calculation comparison.

statistics.py performs Decimal and exact rational checks plus the two locked,
paired bootstrap designs. sources.py extracts the frozen HTML, RSC, rendered
record and PDF nodes. outputs.py produces only original aggregate artifacts,
the nine-point figure, the report and unpublished post drafts. No raw page,
PDF, JSON response, trace or environment configuration is copied into the repo.
