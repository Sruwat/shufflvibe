const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// This project is also built in restricted Windows environments where Metro
// worker child-process creation can be denied. A single worker keeps the
// release bundle deterministic and includes the same complete module graph.
config.maxWorkers = 1;

module.exports = config;
