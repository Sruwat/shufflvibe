# SHUFFL Admin Dashboard — CTO Remediation & Responsive UAT Plan

## Objective

Bring the admin dashboard from a locally usable prototype to a reliable, responsive operations console. The finished dashboard must show truthful pipeline state, protect admin credentials, expose complete venue evidence without duplication, support safe editorial actions, and remain usable at 320px, 768px, 1024px, 1440px and wide desktop sizes.

## Current baseline from UAT

- Local dashboard and MySQL-backed admin APIs load successfully.
- 4,429 venue records and 165 configured areas are visible.
- Authentication behavior is present: authorized requests succeed and unauthenticated summary access returns 401.
- Venue list, filters, pagination, preview, cached Google display data, photos, reviews, hours and Add Venue close behavior were exercised.
- The latest pipeline run is failed, but the UI still presents Pipeline as `LIVE`.
- The full backend pytest command did not finish within the UAT window; test health is therefore not green.
- Google photo proxy works, but the current browser URL carries the admin token as a query parameter.
- Preview currently renders cached Google and live Google sections together, creating duplicate evidence and photos.
- `admin_dashboard/app.js` contains multiple later overrides of `loadVenues` and `openEditor`; `styles.css` contains repeated theme and media-rule blocks. This makes behavior and responsive regression risk high.

## Non-negotiable product rules

1. The dashboard must never show `LIVE` unless a pipeline run is actually `RUNNING`.
2. Failed, partial and stale runs must be visible with error details, last-success timestamp and a safe retry action.
3. Admin tokens must not appear in image URLs, browser history, referrers or copied markup.
4. Google display data must be clearly separated from SHUFFL-owned, rights-cleared media.
5. Preview is read-only; Edit is the only mode that enables controls.
6. Publishing must be blocked when eligibility/evidence rules fail, with a human-readable reason.
7. Every loading, empty, error and stale-data state needs a visible UI treatment.
8. Mobile layouts must not depend on horizontal page scrolling; only intentionally scrollable controls such as filter chips, tabs or data tables may scroll.

## Implementation phases

### Phase 0 — Safety baseline and architecture cleanup

**Purpose:** create a stable surface before feature fixes.

- Split the monolithic `admin_dashboard/app.js` into explicit modules or, at minimum, one authoritative implementation per concern:
  - API client and auth
  - application state / URL state
  - overview and pipeline
  - venue list/grid
  - venue studio/modal
  - add/import venue
  - media rendering
- Remove duplicate function declarations and wrapper overrides for `loadVenues` and `openEditor`.
- Add a single `escapeHtml`, error-normalization and request-cancellation path.
- Consolidate `styles.css` into one token block, one component block and one responsive section. Remove superseded light-theme rules and duplicate media rules.
- Add a development-only diagnostics panel or console namespace that records route, request, render and modal errors without exposing secrets.

**Exit criteria:** one source of truth for each event handler/render path; JS syntax check passes; no duplicate listeners after navigating between views; existing list/preview/add flows still work.

### Phase 1 — Pipeline truthfulness and operations UX

**Backend/UI changes:**

- Add a normalized pipeline status model: `QUEUED`, `RUNNING`, `SUCCEEDED`, `PARTIAL`, `FAILED`, `CANCELLED`.
- Return latest run, last successful run, duration, processed/succeeded/failed counts, checkpoint, source snapshot and sanitized error summary from one admin endpoint.
- Change sidebar and overview indicators to derive from that response. `LIVE` becomes `RUNNING`; failed runs show `FAILED`; no run shows `NOT RUN`.
- Add a pipeline card with:
  - current status and timestamp
  - records processed / failed
  - last successful sync
  - stale warning when data exceeds the configured freshness window
  - `Retry failed run` only when retry is valid
  - `View run details` with checkpoint and error rows
- Disable duplicate starts while a run is queued/running.
- Use polling with backoff while running; stop polling after terminal state.
- Keep retry idempotent and preserve manual overrides/publication state.

**Exit criteria:** seeded failed run visibly fails in UI; retry creates a new run; successful run changes status to succeeded; stale data is not presented as live.

### Phase 2 — Venue catalogue and source-health clarity

- Replace ambiguous `Live Google only` with a source-health badge based on actual fields:
  - `SHUFFL media attached`
  - `Google cached`
  - `Official source verified`
  - `Needs source review`
  - `No usable source`
- Keep venue name, area, city, admission, verification, publication and source health visible in list view.
- Add server-backed filters for publication, eligibility, source health and updated date; preserve filters and pagination in URL query state.
- Add a compact mobile card/list alternative rather than forcing six-column table compression.
- Add skeleton rows/cards, no-results state with clear reset action, API error state with retry, and a stale-data banner.
- Ensure grid and list use the same data and action handlers; changing view must not refetch unnecessarily.

**Exit criteria:** every row has a meaningful source label; filters are shareable via URL; list/grid parity passes on the same venue set.

### Phase 3 — Venue studio and evidence model

- Make Preview and Edit two explicit modes with separate render contracts.
- Preview tabs:
  1. Overview — identity, location, admission, eligibility, publication
  2. Evidence & scores — source provenance, scores, confidence and failed evidence rules
  3. Media & rights — SHUFFL-owned media only, Google display references separately labeled
  4. History — audit events and publication versions
- Render cached Google data once. If a fresh live fetch is requested, show it in a clearly labeled refresh state and merge only non-duplicate fields.
- Add `Last refreshed`, source, rights and retention labels for every external field group.
- Show a photo error placeholder, retry action and alt text; never silently render broken images.
- Add sticky modal header/footer only when viewport height allows it; keep the content body independently scrollable.
- On close: revoke browser object URLs, cancel in-flight requests, restore focus to the triggering button and clear transient modal state.
- Disable or remove editor controls in Preview DOM, not only via the `disabled` attribute.

**Exit criteria:** no duplicate Google section; preview cannot mutate data; Edit save/publish/unpublish flows are distinct and auditable; Escape, close button, backdrop policy and focus restoration work.

### Phase 4 — Photo security and media foundation

- Remove `?token=...` from photo URLs.
- Preferred implementation: authenticated `fetch` with `X-Admin-Token`, convert response to a browser object URL, and revoke it on cleanup.
- Alternative for production CDN: short-lived signed media URLs with narrow scope and expiry.
- Add request timeouts, retry once for transient failures, and `loading="lazy"` with dimensions to prevent layout shift.
- Make rights status explicit: `unknown`, `review_required`, `licensed`, `owned`, `rejected`.
- Keep Google photos display-only until an authorized, rights-cleared upload is added to SHUFFL media.
- Do not call paid live enrichment on every preview if a fresh cache exists; expose an explicit `Refresh external data` action with cost warning and permission check.

**Exit criteria:** browser DOM/network logs contain no admin token in URLs; photo failures are recoverable; owned-media and Google-reference counts are distinguishable.

### Phase 5 — Responsive UI system

**Breakpoints to verify:** 320px, 375px, 768px, 1024px, 1440px and 1920px.

- Mobile navigation: convert desktop sidebar into a compact top bar or accessible drawer with active-page title and menu button. Do not keep a full horizontal nav as the only navigation model.
- Topbar: stack page title, token/auth controls and actions; hide or move low-priority controls behind an overflow menu.
- Metrics: 1 column at 320px, 2 columns from approximately 480px, 4 columns on desktop.
- Toolbar: search full width; filters become horizontally scrollable chips or a filter drawer; preserve visible active-filter count.
- Venue table: use responsive card rows under 768px; keep table only at tablet/desktop widths. Never require page-level horizontal scroll.
- Grid cards: 1 column at 320px, 2 at tablet, fluid 3–5 columns at desktop; preserve image aspect ratio and consistent card height.
- Dialogs: near-full-screen sheet on phones, centered studio on desktop; `max-height: 100dvh`; safe-area padding; body scroll lock while open.
- Detail grids: 1 column on phones, 2 on tablet, 3 on desktop; long IDs and URLs wrap safely.
- Sticky actions: ensure Publish/Save/Close remain reachable and do not cover content or browser UI.
- Touch targets: minimum 44px; visible focus rings; keyboard and screen-reader labels for icon-only controls.
- Respect `prefers-reduced-motion` and avoid hover-only information.

**Exit criteria:** no clipped controls or text at all target widths; no accidental horizontal body scroll; keyboard navigation and touch targets pass.

### Phase 6 — Accessibility, reliability and performance

- Add dialog semantics: `aria-modal`, `aria-labelledby`, initial focus, focus trap and return focus.
- Add live regions for toasts, pipeline status and save results.
- Ensure status is conveyed with text plus color/icon, not color alone.
- Add abort controllers for navigation/filter/preview requests to prevent stale response overwrites.
- Virtualize or paginate large result sets; do not render all 4,429 venues at once.
- Add performance marks for initial load, list fetch, preview open and image completion.
- Run browser console-error scan, keyboard pass and axe-style accessibility scan.

**Exit criteria:** no uncaught console errors in core flows; no stale request overwrites; first meaningful dashboard render and venue list remain responsive on a normal laptop/mobile viewport.

### Phase 7 — Test and release gate

**Automated tests:**

- API contract tests for auth, summary, venues, pipeline status/retry, media and publish transitions.
- Unit tests for status mapping, source-health mapping, duplicate Google merge and URL/token redaction.
- Browser tests for overview, failed pipeline, retry, search/filter/pagination, list/grid, preview/edit, modal close/Escape, add venue validation and photo error handling.
- Responsive screenshots at all target breakpoints with visual diff review.
- Accessibility checks for navigation, tables/cards, forms and dialogs.
- Run backend tests individually with `-vv --maxfail=1` to locate the existing hang before declaring the suite green.

**Release gates:**

- No P0/P1 issue open.
- Latest pipeline state is truthful and retryable.
- No secret in URL, DOM, logs or export.
- Core UAT passes at 320/768/1024/1440px.
- Full backend and browser suites complete within agreed timeout.
- Production deployment has managed secrets, object storage, worker/scheduler, monitoring and rollback procedure.

## CTO issue taxonomy for execution

- **P0:** security leak, wrong publication data, destructive mutation, dashboard unavailable.
- **P1:** pipeline state misleading, preview/edit mutation ambiguity, data duplication, broken primary workflow, test suite not runnable.
- **P2:** responsive clipping, source label confusion, weak empty/error states, accessibility gaps, slow rendering.
- **P3:** copy polish, micro-animation, minor spacing and visual refinement.

## Recommended execution order

1. Phase 0 architecture cleanup.
2. Phase 1 pipeline truthfulness.
3. Phase 4 photo security.
4. Phase 3 studio/evidence consolidation.
5. Phase 2 catalogue/source health.
6. Phase 5 responsive system.
7. Phase 6 accessibility/performance.
8. Phase 7 automated regression and release gate.

This order prevents visual work from masking correctness and security failures, while still allowing responsive work to proceed against stable components.

## Definition of done

The dashboard is complete only when an operator can safely discover, inspect, edit, publish, unpublish, retry pipeline work and review media rights from desktop and mobile-sized viewports, with truthful status, no credential leakage, no duplicate evidence, complete error recovery, and a passing automated/browser UAT suite.
