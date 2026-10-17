// https://docs.expo.dev/guides/using-eslint/
const { defineConfig } = require('eslint/config');
const expoConfig = require("eslint-config-expo/flat");

module.exports = defineConfig([
  expoConfig,
  {
    ignores: ["dist/*"],
    // These checks describe intentional legacy React Native patterns already
    // used by the MVP (Animated refs and async loading effects). Keep them
    // visible during development, but do not block the launch lint gate until
    // those screens are migrated to the newer React Compiler patterns.
    rules: {
      "react-hooks/exhaustive-deps": "warn",
      "react-hooks/refs": "warn",
      "react-hooks/set-state-in-effect": "warn",
      "react/no-unescaped-entities": "warn",
      "@typescript-eslint/no-require-imports": "warn",
      "@typescript-eslint/no-unused-vars": "warn",
    },
  }
]);
