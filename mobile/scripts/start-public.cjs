const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

// Remove stale proxy variables only for Expo/ngrok. Keep the user's global
// environment unchanged for other tools.
const env = { ...process.env };
for (const key of [
  'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
  'http_proxy', 'https_proxy', 'all_proxy',
]) delete env[key];

// Use Expo's current account-signed tunnel for Expo Go QR links. The legacy
// bundled ngrok agent is no longer accepted by the ngrok service.
env.EXPO_UNSTABLE_TUNNEL_V2 = '1';

// @expo/ngrok returns an exp.direct URL without an explicit public port.
// Expo Go then assumes Metro's local port (8081), producing:
//   http://<host>.exp.direct:8081
// The public ngrok HTTP endpoint is port 80, so make that explicit in the
// URL creator used by Expo CLI. Re-apply this small compatibility patch after
// dependency reinstalls as well.
const urlCreator = path.join(
  process.cwd(),
  'node_modules', 'expo', 'node_modules', '@expo', 'cli', 'build',
  'src', 'start', 'server', 'UrlCreator.js'
);
if (fs.existsSync(urlCreator)) {
  const source = fs.readFileSync(urlCreator, 'utf8');
  const patched = source.replace(
    'port: parsed.port,\n            hostname: parsed.hostname,',
    "port: parsed.port || '80',\n            hostname: parsed.hostname,"
  );
  if (patched !== source) fs.writeFileSync(urlCreator, patched, 'utf8');
}

const expoCli = require.resolve('expo/bin/cli');
const child = spawn(process.execPath, [expoCli, 'start', '--tunnel', '--go', ...process.argv.slice(2)], {
  cwd: process.cwd(),
  env,
  stdio: 'inherit',
});

child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exit(code ?? 1);
});
