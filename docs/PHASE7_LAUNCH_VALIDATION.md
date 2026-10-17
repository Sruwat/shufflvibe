# SHUFFL Phase 7 — launch validation

Phase 7 provides a read-only final audit before the MVP is exposed to users.
It does not call Google, Gemini, Overpass, or any other external provider.

Run it from the repository root:

```powershell
python backend/tools/launch_audit.py
```

Exit code `0` means no hard launch failures. Exit code `2` means the report
needs action. The audit checks:

- published venues are admitted and have a Google `place_id`;
- admitted venues have canonical identity, at least five score rows, and source
  provenance;
- persistent payloads do not contain live Google reviews, hours, coordinates,
  address, or photo fields;
- warnings such as missing SHUFFL tags are visible separately from hard gates.

The same report is available to an authenticated admin at:

```text
GET /v1/admin/ops/launch-audit
```

This is a validation gate, not an automatic publisher. Fix failures through
the pipeline or admin dashboard, rerun the audit, then confirm provider terms,
billing limits, backups, and privacy policy before launch.
