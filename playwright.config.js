const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  use: {
    headless: true,
  },
  projects: [
    {
      name: "design-frontend",
      testMatch: /design-frontend\.spec\.js/,
      use: { baseURL: "http://127.0.0.1:8765" },
    },
    {
      name: "web",
      testMatch: /web-app\.spec\.js/,
      use: { baseURL: "http://127.0.0.1:5174" },
    },
  ],
  webServer: [
    {
      command: "python -m http.server 8765",
      url: "http://127.0.0.1:8765/design-frontend/index.html",
      reuseExistingServer: true,
      timeout: 120000,
    },
    {
      command: "npm run dev --prefix web -- --host 127.0.0.1 --port 5174",
      url: "http://127.0.0.1:5174",
      reuseExistingServer: true,
      timeout: 120000,
    },
  ],
});
