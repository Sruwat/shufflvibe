# Phase 4 — admin operations

The admin dashboard at `/admin/` now operates on the MySQL source of truth.

## Operator workflow

1. Enter the configured admin token, if the server is running with production
   authentication enabled.
2. Use the venue catalogue filters to find a venue by name, city, state, area,
   admission, or verification state.
3. Open **Preview** for live Google display fields and read-only evidence.
4. Open **Edit** to change a draft override, tags, operator class, fit-out
   state, notes, or verified manual hours.
5. Save the draft; the change is recorded in audit history and survives a
   future pipeline sync.
6. Publish only an eligible venue. Published records are the only records
   returned to the mobile/public API.
7. Use **Sync pipeline** to import the latest generated source snapshot.
8. Use **Import Excel** for batch additions/updates or **Add venue** for one
   manual venue.
9. Use the media/history sections to inspect rights metadata and change history.

## Data safety

- Google display values are fetched live by `place_id`; cached legacy Google
  payloads were removed from the current MySQL lifecycle records.
- Google photos are preview-only unless separately uploaded as SHUFFL-owned or
  licensed media with rights metadata.
- Manual overrides are stored separately from automatic pipeline facts.
- A pipeline run records source rows, insert/update counts, status, failures,
  and can be retried from the dashboard.
