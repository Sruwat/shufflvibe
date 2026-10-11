# SHUFFL frontend implementation matrix

This matrix records the current client-demo frontend and the latest device checks collected
on 30 September 2026. “Code present” is not equivalent to a tested feature. Demo state is
local unless a row explicitly says otherwise; no backend contract is implied.

## Release and device evidence

| Check | Result | Evidence |
|---|---|---|
| Current live iteration | **Installed and tested; not the final APK.** Built 2026-09-30 and installed on the connected Realme RMX3511 running Android 13. | Device package `com.shuffl.demo`, v1.0.0; `adb install -r` succeeded and `am start -W` cold launch passed. |
| Current iteration artifact | [`artifacts/shuffl-live-iteration-64dp.apk`](../artifacts/shuffl-live-iteration-64dp.apk), SHA-256 `146B70C8B7E917E90C30222287A23E572AA9414DE7CB8996943F3CE58A2377EF`. | Release APK copied from the short-path build after safe-area and 64 dp feature-tab adjustments. A separate final APK is intentionally deferred until remaining work and checks are complete. |
| Live Home/Play/Chat checks | Passed on phone: Home → Explore, Play → “How are you going out?” with Host/Join/Create visible, Chat → Messages, then Home returned to Explore. | `artifacts/tab-play.xml`, `artifacts/tab-chat.xml`, `artifacts/tab-home.xml`; tap coordinates were derived from the current UI hierarchy. |
| Status bar and navigation insets | Header begins below the status-bar inset. Main tab hit regions: Home/Chat 54 dp, Play 58 dp. Feature tab hit regions: Home/Chat 49 dp, Play 57 dp on this 480-dpi device. | Current UIAutomator captures: `artifacts/live-iteration-touch-state.xml`, `artifacts/live-iteration-touch-venue.xml`; visible phone capture: `artifacts/order-screen.png`. One Android viewport tested; small-screen coverage remains pending. |
| Swipe-to-recommendation path | Passed for one local demo run: daily swipe → result (“Night Climber”) → Explore → Sidecar venue → dish/drink panel. “Order now · preview” opened the explicit “Demo only / Ordering and payment are not connected” alert. | `artifacts/live-iteration-result.xml`, `artifacts/live-iteration-discover-after-vibe.xml`, `artifacts/live-iteration-touch-venue.xml`, `artifacts/pair-content.xml`, `artifacts/order-alert.xml`. Five answer taps completed this adaptive test run; this is not proof of every assessment branch. |
| Runtime errors | Cold launch reached React Native; inspected logs showed no `FATAL EXCEPTION` or `Unable to load script` errors. | `adb logcat` after clearing logs and explicit cold launch. |
| Demo-only limitation | Dish/drink content and “86%” are illustrative mock data; no real menus, photos, matching service, order, or payment flow. | Visible disclosure in the preview panel and tested confirmation dialog. |
| Build | Passed: Gradle `:app:assembleRelease`; 210 actionable tasks (186 executed, 24 up-to-date), completed 2026-09-30 15:50 local. | Built in the active `mobile/android` checkout with `ANDROID_HOME` set to the installed SDK and Gradle cache at `C:\g2`. Native CMake targets completed; Expo bundled the JS entry point. |
| Artifact | [`artifacts/shuffl-lineup-food-drink-preview-release.apk`](../artifacts/shuffl-lineup-food-drink-preview-release.apk), 150,313,623 bytes, SHA-256 `0B5DAB922AA2B55AA3903F1D85D1863126A1451DB5B75394EDB2339C8E2E5BE8`. | Copied from this checkout’s successful release output; new artifact built after the venue/active-plan recommendation preview changes. |
| Identity | `com.shuffl.demo`, versionName `1.0.0`, versionCode `1`; source base HEAD `1c285eb99021bdf1b17f968ebe8b0b3da3b1c254`, plus uncommitted frontend changes. | `aapt dump badging`, `git rev-parse HEAD`. |
| Package contents | Packaged `assets/index.android.bundle`, 281 image resources, 52 native `.so` libraries, and 19 font resources. | APK archive listing. This confirms packaging, not that every flow or asset renders correctly. |
| Earlier install / launch (29 Sep artifact) | Historical check only; superseded by the live iteration rows above. | Exact earlier artifact `shuffl-lineup-navfix3-release.apk` was installed and cold-started on the RMX3511. |
| Bottom navigation interactions | Home → Explore, Play → “How are you going out?” (Host/Join/Create visible), Chat → Messages all responded to taps on the latest build. | Tap tests at device coordinates (102,2188), (540,2185), (864,2188); accessible screen content verified in `artifacts/navfix3-play.xml`, `artifacts/navfix3-home-return.xml`, `artifacts/navfix3-chat.xml`. |
| Navigation layout (29 Sep artifact) | Historical finding; the edge-to-edge clipping was reproduced and then corrected in the installed live iteration above. | Earlier `artifacts/navfix3-home.xml` showed 18–30 px tab bounds. |
| Startup errors | Latest cold launch reached React Native; inspected app log had no `FATAL EXCEPTION` or `Unable to load script` match. | `adb logcat` after clearing logs. Earlier malformed Monkey invocation printed tombstone notices; explicit `am start` was used for final cold-start check. |
| Visible rendering | Visually inspected for the venue pairing/footer state on the current iteration. Other screens and viewport sizes remain unreviewed visually. | `artifacts/order-screen.png` captured from the RMX3511. |

## Flow coverage

| Flow / feature | Status | What is evidenced / remaining |
|---|---|---|
| Welcome → context → demo sign-in | Device-tested, partial | “Start exploring”, “Continue”, and “Continue as Aarav” advanced to Profile. Demo identity is seeded local state, not authentication. |
| Profile → preferences | Device-tested, partial | Name entry and pronoun selection updated the UI hierarchy. After scrolling the CTA into view, “Continue to preferences” opened the preference deck. |
| Preference game | Device-tested, partial | Six preference answers advanced; the saved-preferences screen and “Continue to tonight” opened the daily-vibe intro. Responses were seeded test choices; full deck semantics were not independently audited. |
| Daily vibe intro / adaptive swipe | Device-tested, partial | “Let’s go” opened the deck. Four answer choices were exposed as controls; selecting “UP FOR IT” advanced. A few answers reached a result. A forced tie-break case was not tested. |
| Vibe result → Home | Device-tested, partial | Result screen displayed a generated name and seven factor scores; its completion action reached Explore/Home. This is one demo path, not exhaustive naming or tie-break validation. |
| Home and Play navigation | Device-tested, partial | Home exposed seeded Delhi venue cards, search and profile controls. Play opened “How are you going out?” and Host/Join/Create were visible. The footer hit targets remain clipped to a narrow strip; visual layout is unverified. |
| Chat navigation | Device-tested, partial | Bottom Chat opened Messages with Search and Invites visible. A personal conversation/message send was not tested. The footer hit target remains clipped. |
| Search / filters | Code present; device-unverified | No current-build search or filter interaction test recorded. |
| Host, Join, Create, room and capsule | Code present; device-unverified | Play menu exposes Host/Join/Create. No room lifecycle, multi-user, host/co-host, or capsule approval test recorded. |
| Plans, active plan, venue and arrival | Code present; device-unverified | No complete plan-to-arrival device pass recorded. |
| Profile, privacy, social, messages, music | Demo UI/code present; provider behavior unverified | Local mock state only where present. No claim of real messaging, playback, location, identity, or live data. |
| Dish/drink recommendations | Interactive demo UI present; not algorithmically or device verified | Active-plan stops now link to a venue detail pairing panel with illustrative, seeded suggestions and simulated order CTA. Matches are marked “Demo”; suggestions are not read from a vibe database or venue menu, include no verified food/drink photos, do not calculate a real percentage, and do not connect to a payment gateway. |
| Relaunch persistence | Device-tested, partial | After completing the demo vibe and reaching Home, the new chunked SecureStore build restored Explore/Home on two consecutive force-stop/cold-start cycles. Fresh app-process logs had no 2 KB SecureStore warning and no script-load error. Other feature state/persistence is not exhaustive. |
| Responsive sizes / accessibility visuals | Not verified | One RMX3511 screen only; black ADB captures blocked visual comparison and no small/large viewport device matrix was run. |

## Specification variance and limits

The repository’s current `frontend/VIEW_FLOW.md` and assessment specifications call for an
adaptive seven-factor daily deck without a visible card count. Earlier supplied material
mentions fixed 28/18-card flows and an eight-factor set. The implementation follows the
current repository assessment specification; this conflict must be resolved against the
client’s chosen spec before claiming full parity.

The release is a standalone Android APK at the packaging level (bundle, images and native
libraries are inside it, and it launched with no Metro listener). Backend, API, authentication,
provider integrations, multi-account behavior, and offline behavior with network radios disabled
were not validated here. Do not interpret a successful build or the device startup check as
100% frontend/spec completion.
