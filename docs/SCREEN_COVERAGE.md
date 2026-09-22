# Screen and spec coverage

Status describes the current implementation, not the ambition of the full SHUFFL spec. “Demo flow” means the screen is reachable and its primary interactions use local or seeded state; it does not imply production integrations or complete backend contracts.

| Area | Current status | Evidence / gap |
|---|---|---|
| Onboarding and demo sign-in | Demo flow | Local identity only; no authentication provider. |
| Profile and preference assessment | Partial demo flow | Preference deck and badges exist; persistence and full profile editing are incomplete. |
| Daily vibe assessment | Core logic implemented; visual/demo flow | Seven-factor adaptive cards, four scores, deferral, timeout/away handling, Back, forced choice, latency ranking. Full spec parity and durable session storage still need audit. |
| Vibe naming | Core rules implemented | V4 pole words, strongest-factor choice, tie override, second-factor thresholds, latency and weight fallbacks. Name freezing/persistence needs backend integration. |
| Discovery lock/unlock | Local demo flow | Control Centre toggle; not connected to production eligibility. |
| Search and filters | Partial / shell | Navigable screen; provider-backed search and complete filter behavior are not implemented. |
| Venue detail and preference fit | Local demo flow | Seeded venue attributes; no live inventory, routing, booking, or real maps. |
| Plan/chemistry algorithms | Partial | Prototype chemistry and venue ranking exist. Repository’s full two-stage shape/fill, bend/fairness, venue constraints, and feedback loop are not fully implemented or parity-tested. |
| Plans and arrival consent | API-backed when configured; in-memory demo otherwise | Plan creation/lock and global plus per-plan approximate-presence consent are wired. Feedback is still local; no GPS location is collected. |
| Rooms, join requests, capsules | Local demo states | Seeded interactions; no real-time collaboration or persistence. |
| Notifications, inbox, chat | Local demo states | No push transport or chat service. |
| Privacy & safety | Partial functional demo flow | Visibility, discoverability, approximate presence, global location permission, plan-specific consent, report submission, and block/unblock state have UI/service/API paths and contract tests. State is in-memory; auth, real enforcement, moderation, and audit remain incomplete. |
| Visitor/profile history/report/support | Mixed demo flows and shells | Report/block screen now supports target, reason, details, report submission, and block/unblock. Durable profiles/history, account-scoped enforcement, moderation, and complete support actions need implementation. |
| FastAPI boundary | Partial | Endpoints and tests exist; not all mobile screens use backend services and production auth/data integrations are absent. |
| Android APK | CI build | GitHub Actions assembles a debug APK; packaging success is not a 100% feature-coverage claim. |
