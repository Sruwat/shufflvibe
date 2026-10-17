# SHUFFL App MVP Launch Audit and Implementation Plan

Date: 2026-10-15

## Executive decision

The venue catalogue is treated as locked for this release. The app is **not yet MVP-launch ready**.
It is a strong interactive prototype with working mobile typecheck/tests and a working catalogue/API
surface, but the most important MVP loop is not aligned with the latest product decision:

```text
Draw the night shape
  -> receive 5–10 matching venues per stop that are open at that hour
  -> user/host selects one venue per stop
  -> room members see the selected stop list
  -> lock and follow the plan
```

The current mobile code still has a `plans/generate` path and can fall back to an in-memory
`DemoService`. Those two issues must be resolved before calling the release production-ready.

## Scope authority

Use the documents in this order:

1. `shuffl-docs/shuffl-spec-main/specs/MVP_INSTRUCTIONS.md` — release scope and cuts.
2. `shuffl-docs/shuffl-spec-main/design/SCREENS.md` — screen intent and visual reference.
3. Other specs and `VIEW_FLOW.md` — implementation detail only when not contradicted by the first two.

The Gold screens (20–26) are explicitly post-MVP. The Messages SHUFFL button, group-learning flow,
and insights panel are also cut from the first release.

## Current state

| Area | Status | Meaning |
|---|---|---|
| Locked venue database | Green | Pipeline lock is enabled; manual admin edits remain possible. |
| Public venue API | Green/Amber | Catalogue can be served, but final launch must verify the locked admitted count and area coverage against the agreed NCR target. |
| Venue stop options | Amber/Red | Backend route exists; the mobile picker flow is not yet the authoritative MVP flow. |
| Mobile build | Green | Typecheck passes; the existing automated suite passes 16 tests. |
| Mobile-to-backend selection | Red | App can use `DemoService` when `EXPO_PUBLIC_API_URL` is missing. |
| Auth and durable user state | Amber/Red | OTP/login, rooms, chats, plans and notifications need production persistence/auth checks. |
| Screen implementation | Amber | Many routes/components exist, but several are generic, partial, or not connected to the locked catalogue. |
| Pixel/visual parity | Not proven | A code audit was done; screenshot-by-screenshot visual QA still needs to be run. |

## Screen-by-screen audit

Status meanings: **Ready** means the route/component exists and is close to the intended MVP job;
**Partial** means a route exists but the product contract or persistence is incomplete; **Missing**
means a dedicated flow is still required; **Post-MVP** means do not block launch on it.

| # | Screen | Status | Launch action |
|---:|---|---|---|
| 01 | Home | Partial | Connect real user/friends/activity data and verify the locked-catalogue entry points. |
| 02 | SHUFFL locked | Partial | Wire the locked state to the real daily assessment/session state. |
| 03 | SHUFFL | Partial / blocker | Replace auto-plan behavior with shape → suggested venues → user builds the night. |
| 04 | Skeleton game | Partial | Persist stops/energy/crowd and pass the shape to ranking. |
| 05 | Host | Partial | Connect venue search and host creation to durable rooms and real user identity. |
| 06 | Host room | Partial | Implement member status, merged skeleton, host-only venue selection, and live refresh. |
| 07 | Join place or people | Partial | Connect search/filter/ranking to real rooms; show labels instead of join gates. |
| 08 | Room player | Partial | Persist room membership, chemistry, plan-fit ranking, and read-only member view. |
| 09 | Capsule waiting | Partial | Persist capsule membership/approval state and handle refresh/reconnect. |
| 10 | Plan card | Partial / blocker | Render the user-built stop list; do not imply that the app invented a timed outing. |
| 11 | Active plan | Partial | Persist the locked plan and implement next-stop/arrival state from backend data. |
| 12 | Messages | Partial | Keep DMs, group chats, and search only; remove the retired SHUFFL button/insights path. |
| 13 | Profile | Partial | Connect real profile/preferences/chemistry data; remove demo-only identity assumptions. |
| 14 | Capsule approval member | Partial | Complete member approval state, loading, errors, and refresh behavior. |
| 15 | Capsule approval creator | Partial | Complete creator controls and durable approval transitions. |
| 16 | Two rooms | Missing/Partial | Decide whether this remains in MVP; if retained, implement room switching and independent state. |
| 17 | Venue | Partial / important | Connect venue detail to the locked catalogue, live hours, map link, media, tags, scores, and evidence. |
| 18 | Go here card | Partial | Implement warning-first copy, live hours, directions, and both available actions. |
| 19 | Stop list | Missing / blocker | Build the core per-stop 5–10 venue picker, open-at-hour filter, scoring sort, and selection state. |
| 20 | Gold offer | Post-MVP | Defer until the December/funding Gold campaign. |
| 21 | Gold capture photos | Post-MVP | Defer; do not block launch. |
| 22 | Gold capture swipes | Post-MVP | Defer; do not block launch. |
| 23 | Gold verified | Post-MVP | Defer; do not block launch. |
| 24 | Gold in search | Post-MVP | Defer; do not block launch. |
| 25 | Gold failed | Post-MVP | Defer; do not block launch. |
| 26 | Gold in room plan | Post-MVP | Defer; do not block launch. |
| 27 | Member stop list | Partial | Make the host-selected list explicitly read-only for members. |
| 28 | Preset opened | Partial | Keep presets as a shortcut into the same shape/stop-selection flow. |
| 29 | Inside a room | Partial | Connect room identity, blend, icons, and plan provenance to durable room data. |
| 30 | Customise room | Partial | Provide explicit room filters/customisation and persist changes. |
| 31 | Friends activity | Missing/Partial | Add a real activity feed backed by user/friend events; do not use static cards. |
| 32 | Venue pros/cons | Missing/Partial | Add evidence-backed strengths/limitations from venue data without inventing facts. |
| 33 | Add friends | Partial | Finish search, invite, duplicate handling, and chat creation. |
| 34 | Name gathering | Partial | Keep one authoritative gathering-name step; remove the retired duplicate Messages path. |
| 35 | Gathering waiting | Partial | Add waiting/reconnect/empty/error states and durable member updates. |
| 36 | Capsule room | Partial | Connect capsule room to the same room/plan source of truth. |
| 37 | Wheel mirror | Missing | Either implement the wheel flow or mark it post-MVP in product scope. |
| 38 | Wheel request | Missing | Same decision as screen 37; no hidden dead-end route. |
| 39 | No wheel | Missing | Add the explicit fallback state if wheel remains in launch scope. |
| 40 | Build empty | Partial | Make this the empty state before venue choices exist. |
| 41 | Build search | Partial | Make search filter the locked catalogue and preserve the current stop context. |
| 42 | Build filled | Partial | Persist selected venues and allow replacement without losing other stops. |
| 43 | Built night | Partial | Render the final user-built night, then lock it durably. |
| 44 | Waiting locked | Partial | Wire locked/waiting states to backend transitions and reconnect behavior. |
| 45 | A proposal | Missing/Partial | Decide if proposals are MVP; otherwise remove from launch navigation. |
| 46 | Proposals panel | Missing/Partial | Same decision as screen 45; no placeholder panel in the release. |
| 47 | Cold open | Partial | Verify first-run routing, copy, and no-data states against the actual onboarding. |
| 48 | The invite | Partial | Complete invite link/deep-link/share behavior and expiry/error states. |
| 49 | Home locked | Partial | Connect to the same session lock used by screen 02. |
| 50 | Notifications all | Partial | Persist notification read state and deep links; handle empty/error states. |
| 51 | Confidence marks | Missing/Partial | Add only if still in MVP scope; marks must come from evidence/confidence fields. |
| 52 | Meters applied | Partial | Verify the meters reflect the actual assessment and ranking data, not demo values. |
| 53 | Plan dormant | Partial | Define dormant/expired plan state and persist it. |
| 54 | Plan insights | Post-MVP for the retired group-learning path | Do not block MVP; remove from Messages navigation. |
| 55 | A ditch | Missing/Partial | Decide launch scope; if retained, implement a clear safe exit/abandon flow. |

## Implementation order

### Phase 1 — Freeze scope and release contract

- Keep `VENUE_PIPELINE_LOCKED=1`; pipeline sync is disabled while admin edits remain available.
- Freeze the public venue contract: identity, area, category, scores, tags, map URL,
  source/evidence links, and display-time opening hours.
- Confirm the launch coverage decision: current admitted catalogue versus the approximately 360 NCR
  target in the spec. A locked catalogue is not automatically target-complete.
- Remove or feature-flag Gold screens 20–26 and the retired Messages SHUFFL/insights routes.

**Done when:** product scope, venue fields, launch catalogue, and navigation exclusions are signed off.

### Phase 2 — Connect the app to the real backend

- Require `EXPO_PUBLIC_API_URL` in release builds; never silently switch to `DemoService`.
- Add real auth/session identity and secure restore/logout behavior.
- Persist rooms, memberships, plans, messages, notifications, and invites in MySQL.
- Add API loading, empty, validation, conflict, retry, and offline states.

**Done when:** a fresh build cannot show demo data and all core state survives app/backend restart.

### Phase 3 — Complete the vibe assessment and skeleton

- Finish screens 01–04, 47, 49, and 52 against the current design references.
- Persist the six identity factors, daily check-in, assessment result, and drawn skeleton.
- Validate latency, daily lock, empty states, accessibility labels, and returning-user restore.
- Pass stops, energy, crowd, and timing context into the ranking API.

**Done when:** a new user can complete onboarding, assessment, and skeleton creation end-to-end.

### Phase 4 — Build the real venue-selection loop

- Implement screens 03, 19, 27, 28, and 40–43 as one shared stop-list state machine.
- For every stop, call stop-options with the stop shape and intended hour.
- Filter opening status at display time; do not permanently store Google hours/reviews.
- Return 5–10 matching venues, rank with shape distance and evidence-backed SHUFFL scores, and
  explain why a venue fits.
- Let the user select/reselect each stop; host selects in a room and members remain read-only.
- Persist the selected list and render screens 10/11 from the locked plan.

**Done when:** the app never invents a venue schedule and a user can build a complete night manually.

### Phase 5 — Finish rooms, capsules, joining, and invites

- Complete screens 05–09, 14–16, 29, 30, 33–36, 44, and 48.
- Implement host creation, join discovery, capsule approval, member status, invite links, and
  reconnect behavior.
- Rank rooms by chemistry plus actual plan fit, aligned by clock rather than stop index.
- Keep join gates as visible labels/warnings, not hard filters.

**Done when:** host and members can create/join a room, agree on a plan, and see the same durable state.

### Phase 6 — Complete venue detail and action flows

- Finish screens 17, 18, and 32 plus venue-related states in 11, 19, and 27.
- Show official identity, photos/media, map link, website/social links, tags, scores, evidence,
  pros/limitations, and live-hours freshness.
- Implement Go Here, directions, arrival, report, privacy, safety, and support flows.
- Use `unknown`, `not_specialised`, or “not available” instead of inventing missing evidence.

**Done when:** every published venue has a useful detail page and every action has safe success/error states.

### Phase 7 — Messages, notifications, profile, and user lifecycle

- Finish screens 12, 13, 31, 50, and the profile/settings routes.
- Keep Messages limited to DMs, group chats, and search; do not restore the removed SHUFFL button.
- Persist unread/read state, deep links, friend activity, profile preferences, privacy, and account
  deletion/reporting flows.
- Replace generic feature-route placeholders with real product screens or remove them from navigation.

**Done when:** users can communicate and manage their account without demo-only data or dead-end routes.

### Phase 8 — Visual parity, accessibility, and reliability QA

- Capture every in-scope screen at target mobile sizes and compare with `design/screens`.
- Test loading, populated, empty, error, offline/retry, long text, and no-image states for every route.
- Test safe areas, keyboard behavior, touch targets, screen readers, contrast, reduced motion, and
  network recovery on Android and iOS.
- Test new user, returning user, host, member, rejected invite, expired plan, missing hours, and
  locked catalogue scenarios.
- Resolve all P0/P1 defects and record any intentional design deviations.

**Done when:** screenshot comparison and accessibility/reliability checklist are signed off.

### Phase 9 — Production launch gate and handoff

- Run locked-database smoke tests: discovery, venue detail, stop-options, room creation, plan lock,
  messages, notifications, admin edit, and Excel export.
- Verify environment variables, API URL, auth secrets, MySQL migrations, backups, rate limits,
  logging, monitoring, and rollback instructions.
- Build a release candidate and test it against the production-like backend, not the demo service.
- Confirm analytics/crash reporting, privacy copy, support contact, and app-store metadata.
- Freeze the release branch, tag the candidate, and prepare the launch/runbook document.

**Done when:** all MVP launch gates below pass and the release candidate can be restored and rolled back.

## MVP launch gate

Launch only when all of these are true:

- The app cannot silently use demo data in a release build.
- A user can draw a shape and select real venues stop-by-stop from 5–10 open choices.
- A host can choose the room's venues and members see the list read-only.
- A locked plan survives app restart and backend restart.
- Venue detail and display-time hours work from the locked catalogue/API.
- Login, room membership, chat, invites, and notifications have durable state.
- Post-MVP Gold and retired group-learning routes are not exposed in launch navigation.
- Every launch screen has verified loading, empty, error, and accessibility states.
- The screenshot comparison has been completed; code presence alone is not visual parity.

## Bottom line

With the venue database locked, the next work is not more venue scraping. The launch-critical work is
to connect the mobile app to the real backend, replace auto-generated outing behavior with the
shape-to-stop-selection loop, make rooms/plans/messages durable, and complete the screen states that
are currently partial or generic. The current test pass is a good engineering baseline, but it does
not by itself prove MVP readiness or exact design-screen parity.
