# Build and release

From `mobile/`: `npm install`, `npx expo start`, `npm run typecheck`. For a local Android artifact with Android SDK configured: `npx expo prebuild --platform android`, then `cd android; .\gradlew.bat assembleDebug`; copy `android/app/build/outputs/apk/debug/app-debug.apk` to `artifacts/shuffl-demo-v1.apk`.

The supplied environment had Node, npm, Python and Java, but no detected Android SDK, `adb`, or Gradle executable. Therefore no APK is claimed from this run.
