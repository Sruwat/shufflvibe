# SHUFFL Phase 8 QA Checklist

Phase 8 covers reliability and accessibility around the locked venue catalogue.
It does not unlock or resync the venue pipeline.

## Implemented in code

- API GET requests have a 10-second timeout and one safe retry for network/5xx failures.
- Venue detail has loading, missing-data, error, and retry states.
- Inbox and notifications have loading, empty, error, and retry states.
- Chat has an API error state and a real message composer.
- Venue photos are rendered only when an actual HTTPS media URL exists; otherwise the UI says media is unavailable.
- Opening hours, rating, review count, address, and website fall back to “not available” instead of invented values.
- Interactive controls have accessibility roles/labels for navigation, forms, radio/checkbox controls, venue actions, messages, and safety actions.
- Long venue names, long report text, and long chat text are allowed to wrap inside scrollable cards.
- Support, report, privacy, arrival, and account-reset flows expose user-visible success/error states.

## Manual screen matrix

| Area | Populated | Empty | Error/offline | Accessibility |
|---|---|---|---|---|
| Discovery | venue cards and stop options | no published venues | retry API | card/action labels |
| Venue detail | official data + live hours | unknown hours/photos/tags | retry venue details | website, maps, report labels |
| Custom outing | 5–10 choices per stop | no matching venues | retry stop options | radio selection labels |
| Active plan | locked selected stops | no plan | locked/expired plan message | stop action labels |
| Host/join | room, stop list, requests | no hosted rooms/requests | API retry/error | request decision labels |
| Capsule | member approvals | no selected members | approval error | approval button labels |
| Inbox/chat | conversations/messages | no conversations | retry inbox/send error | search, message, send labels |
| Notifications | read/unread items | no notifications | retry notifications | unread text + icon |
| Profile/privacy | saved profile/settings | unset optional fields | save/delete error | labelled inputs/toggles |
| Safety/support | report/block/support | no prior reports | submission/open-email error | radio/input/action labels |

## Required device QA before launch

1. Test Android and iOS at 320px-equivalent narrow width and normal phone width.
2. Test keyboard focus/order for profile, report, search, chat, and custom outing inputs.
3. Test screen reader labels for venue actions, radio choices, switches, and message send.
4. Turn off network, open venue detail/inbox/notifications, confirm retry controls appear.
5. Test a venue with no hours, no photos, no tags, and an overlong official name.
6. Restart the app after locking a plan and confirm the same stops remain visible.
7. Test host, member, declined request, empty capsule, expired/missing plan, and locked-catalogue states.
8. Capture the in-scope screens and compare against `shuffl-docs/shuffl-spec-main/design/screens`.

## Intentional deviations

- Exact screenshot parity still requires device captures; source code cannot prove pixel parity.
- Real authentication and production identity are not added by this phase; the MVP API currently uses the existing `demo-user` session model.
- Google live fields remain request-scoped and are never written to the permanent venue tables.
