// Browser suite for the pane. Runs the real lab API (CA_ALLOW_NO_TURNSTILE=1, site origin = this harness) and a host
// page that frames the pane with the production sandbox. CI job `e2e` in .github/workflows/ci.yml; locally `make e2e`
// (needs a Playwright chromium: `npx --yes playwright@1.63.0 install --with-deps chromium`).
import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";

const ROOT = resolve(__dirname, "../..");

const API_PORT = Number(process.env.CA_E2E_PORT ?? 8099);
const HOST_PORT = Number(process.env.CA_E2E_HOST_PORT ?? 8098);

export default defineConfig({
  testDir: ".",
  testMatch: /.*\.spec\.ts/,
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  use: { baseURL: `http://127.0.0.1:${API_PORT}`, trace: "retain-on-failure" },
  webServer: [
    {
      command: `uv run python -m cloud_assessment_lab`,
      cwd: ROOT,
      url: `http://127.0.0.1:${API_PORT}/api/health`,
      reuseExistingServer: !process.env.CI,
      env: {
        PORT: String(API_PORT),
        CA_ALLOW_NO_TURNSTILE: "1",
        CA_LOG_SILENT: "1",
        CA_SITE_ORIGINS: `http://127.0.0.1:${HOST_PORT}`,
        CA_FRAME_ANCESTORS: `http://127.0.0.1:${HOST_PORT}`,
      },
    },
    {
      command: `uv run python -m http.server ${HOST_PORT} --bind 127.0.0.1 --directory tests/e2e`,
      cwd: ROOT,
      url: `http://127.0.0.1:${HOST_PORT}/host-page.html`,
      reuseExistingServer: !process.env.CI,
    },
  ],
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
});
