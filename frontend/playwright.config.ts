import { defineConfig } from "@playwright/test";
const externalServers = process.env.PLAYWRIGHT_EXTERNAL_SERVERS === "true";
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";
export default defineConfig({
  testDir: "./tests/e2e",
  webServer: externalServers ? undefined : { command: "npm run dev", port: 3000, reuseExistingServer: true },
  use: { baseURL },
  outputDir: "test-results",
});
