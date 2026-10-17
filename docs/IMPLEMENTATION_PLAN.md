# SHUFFL MVP implementation plan

This plan follows the locked venue pipeline and keeps the database contract
separate from live Google display enrichment.

## Phase 1 — canonical venue data contract (implemented)

- Keep `admin_venues` as the lifecycle/publication root.
- Store structured SHUFFL-owned facts in `venue_identity`, `venue_scores`,
  `venue_tags`, `venue_sources`, `venue_time_slots`, and `venue_metros`.
- Backfill existing lifecycle records into the canonical tables.
- Preserve Google `place_id` and lookup URL, but do not persist Google address,
  coordinates, opening hours, rating, review text/distribution, or photos.
- Add normalized admin detail reads and full Excel export sheets.
- Keep manual admin overrides in the lifecycle record and reapply them during
  future pipeline syncs.

## Phase 2 — pipeline contract hardening (implemented)

- Area resolution now uses Nominatim first, Google Text Search fallback, and
  Overpass for anything still unresolved.
- Nearby discovery covers bar, nightclub, pub, restaurant, and café; results
  deduplicate by normalized Google `place_id` while retaining all categories
  and source areas.
- Overpass matches are fuzzy-name/geospatial secondary evidence and failures
  are written to `pipeline_failures.json`.
- Official-site enrichment follows same-domain linked menu, booking, events,
  about/contact, hours, schedule, and music pages.
- Gemini remains optional; deterministic scoring is still the required fallback.

Application authentication work added after the initial venue phases:

- email/password registration and login with PBKDF2 password hashes;
- bearer-token `/v1/auth` endpoints and mobile token persistence;
- profile, assessment, skeleton, privacy, and plan ownership are scoped to
  the authenticated user, with a development-only `demo-user` fallback;
- plan locking rejects duplicate, unpublished, unordered, or missing stops.

OTP delivery, refresh-token rotation, and production identity-provider setup
remain launch deployment work; the local MVP auth path is now real rather than
the former demo OTP.

## Phase 3 — admission and evidence quality (implemented)

- Admission now requires identity evidence, a supported category, five or more
  evidenced/not-specialised score factors, valid fit-out evidence, and valid
  review provenance.
- Missing evidence becomes `Insufficient evidence`; quality/business failures
  become `Rejected`.
- Only SHUFFL-owned review evidence from `config/shuffl_reviews.csv` is
  accepted as durable review evidence.
- Google rating/review count remain transient quality signals and Google review
  text is never written to the market-ready database.
- Each candidate receives an `evidence_audit` and each factor receives a
  score-evidence row plus a coverage audit.

## Phase 4 — admin operations (implemented)

- Admin list filters and pagination cover city, state, area, venue type,
  admission, publication, and verification state.
- Admin detail now returns normalized identity, sources, scores, tags, time
  slots, metro data, media rights, live preview, and history in one response.
- Draft/edit/publish/unpublish/archive lifecycle and audit history are wired.
- Manual single-venue create and workbook/CSV import use the same normalized
  sync path with Google-place deduplication.
- Optional human verification controls remain available without blocking the
  automatic pipeline.

## Phase 5 — mobile/public API (implemented)

- Public API returns only normalized, admitted, published venues.
- One-venue detail, live detail, and score-ranked stop-option endpoints are
  available.
- Google identity, opening hours, rating, reviews, coordinates, website, and
  photos are fetched live by `place_id` for detail/stop-option display.
- Live response failures return a usable normalized card with `live: null`;
  live responses are explicitly marked `persisted: false`.
- The mobile API service now consumes public catalogue cards and maps the
  canonical lower-case venue factors into the app's factor vocabulary.

## Phase 6 — production readiness

Implemented in this phase:

- portable JSON + Excel backup command at `backend/tools/backup_database.py`;
- migration/readiness checks at `GET /v1/health/readiness`;
- production secret/configuration validation;
- CORS allow-list support, request IDs, safe request logging, and per-client-IP
  rate limits, with a tighter limit for live stop-options enrichment;
- retry visibility through durable pipeline run records and the operations
  runbook at `docs/PHASE6_PRODUCTION_OPERATIONS.md`.

Still deployment-owned launch gates:

- configure Windows Task Scheduler/CI credentials and encrypted backup
  retention;
- run the full staging pipeline over every configured area and investigate all
  failures;
- confirm Google Places terms, photo/display requirements, billing limits, and
  the app privacy policy before public launch.

## Phase 7 — launch validation

Implemented:

- read-only pre-launch audit at `GET /v1/admin/ops/launch-audit`;
- CLI audit at `backend/tools/launch_audit.py`;
- checks for published/admitted lifecycle consistency, canonical identity,
  score coverage, source provenance, Google place identity, and prohibited
  persistent live-Google fields;
- automated tests for a complete record and a live-data retention violation.

## Phase 8 — data remediation (implemented)

- fixed legacy canonical sync so duplicate transient Google source rows are
  skipped and duplicate durable source IDs are made deterministic;
- fixed lifecycle-to-canonical backfill to use legacy root identity fields when
  older JSON payloads do not repeat them;
- added repeatable repair command at `backend/tools/repair_canonical.py`;
- repaired the connected MySQL database: 4,429 processed, 0 failed;
- final launch audit passes all hard gates. Five admitted venues still have a
  non-blocking missing-SHUFFL-tag warning for later editorial enrichment.

## Phase 9 — final MVP launch (implemented)

- added quota-safe API smoke test at `backend/tools/smoke_test.py`;
- added final launch, rollback, monitoring, and acceptance runbook at
  `docs/PHASE9_MVP_LAUNCH.md`;
- smoke coverage includes readiness, public discovery/catalogue, admin summary,
  and Excel export while intentionally skipping live Google stop-options calls.

## Screen and feature completion gate

The reference set in
`shuffl-docs/shuffl-spec-main/design/screens` is part of the launch scope. A
screen image existing in the repository does not count as implemented by
itself. Each reference screen must be mapped to a reachable mobile route and
must have working loading, empty, error, back-navigation, and data states.

The final gate must record, for every reference screen:

- the mobile route/feature mode that renders it;
- the API calls and persisted state used by that route;
- the user action that reaches the next screen;
- Android and iOS capture links at the target viewport;
- accessibility and interaction test results.

The current code has a broad route skeleton, but the following are not yet
allowed to be marked complete merely because a route or fixture exists:

- real authentication and user-scoped persistence;
- authoritative stop-by-stop selection and locked-plan mutation rules;
- durable multi-user rooms, invites, chat, and notifications;
- complete media/settings admin operations;
- venue pros/cons and every venue action;
- device-level visual parity across the reference set;
- production monitoring, restore, rollback, and store release evidence.

Phase completion is therefore sequential: a phase is marked complete only
after its automated tests pass and its referenced screens have an evidence row
in the screen-coverage checklist. The next phase can then start without
overwriting the locked venue catalogue.
