const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  use: {
    baseURL: "http://127.0.0.1:8765",
    headless: true,
  },
  webServer: {
    command: "python -m http.server 8765",
    url: "http://127.0.0.1:8765/design-frontend/index.html",
    reuseExistingServer: true,
    timeout: 120000,
  },
});
