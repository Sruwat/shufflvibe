# SHUFFL reference-screen coverage checklist

This checklist is the launch evidence register for the 55 reference screens in
`shuffl-docs/shuffl-spec-main/design/screens`. It is intentionally separate
from the venue database lock: venue data can remain locked while app routes are
completed and tested.

## Required evidence per screen

For each row, record:

1. reference image;
2. reachable mobile route/feature mode;
3. API/data dependency;
4. next-action wiring;
5. loading, empty and error states;
6. Android capture;
7. iOS capture;
8. accessibility result;
9. owner and date.

## Current implementation rule

`Implemented` means the screen is reachable with real API-backed state and its
primary actions persist correctly. A static fixture, demo fallback, or a route
that only renders a placeholder is `Partial`, not `Implemented`.

## Phase gates

- Phase 1: all reference files are present and every screen has an owner/route
  row.
- Phase 2: authentication and user-scoped persistence are wired to the rows.
- Phase 3: assessment and skeleton rows persist and survive restart.
- Phase 4: stop-by-stop venue selection rows create and lock an authoritative
  plan.
- Phase 5: venue detail/action rows use the published catalogue and live-only
  enrichment correctly.
- Phase 6: room/invite/capsule rows work for more than one real user.
- Phase 7: chat/notification/profile rows are durable and scoped per user.
- Phase 8: Android/iOS captures pass visual and accessibility review.
- Phase 9: production build, monitoring, backup/restore, rollback, and store
  release evidence are attached.

The checklist must not be marked fully complete until every row has evidence.
