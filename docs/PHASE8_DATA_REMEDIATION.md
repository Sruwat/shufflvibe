# SHUFFL Phase 8 — canonical data remediation

Phase 8 repairs older lifecycle records without calling external APIs or
persisting Google live data.

Run when a migration or legacy import has left normalized tables incomplete:

```powershell
python backend/tools/repair_canonical.py
```

The command is idempotent. It rebuilds canonical identity, scores, tags,
sources, time slots, and metro rows from the lifecycle payload while retaining
the lifecycle/publication records. It skips `google_live_display_only`
provenance rows, deduplicates durable source IDs, and uses legacy root name/
area fields when the older JSON shape did not include them.

The command ends by running the Phase 7 launch audit. Exit code `0` means all
hard launch gates pass; exit code `2` means the report still needs action.
Warnings are not silently promoted to hard failures. The current database
repair processed 4,429 venues with zero failures; five admitted venues remain
with a non-blocking missing-SHUFFL-tag warning.
