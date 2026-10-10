import { expect, test } from "@playwright/test";

const HOST_PORT = Number(process.env.CA_E2E_HOST_PORT ?? 8098);
const API_PORT = Number(process.env.CA_E2E_PORT ?? 8099);

test("pane: sample → scorecard → filter → detail → copy report → download → delete", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("/");
  await expect(page.getByText("no cloud connectivity by design")).toBeVisible();
  await expect(page.locator("#status")).toHaveText("Ready");
  await expect(page.locator('input[type="password"]')).toHaveCount(0);
  await page.getByRole("button", { name: "Use the sample export" }).click();
  await expect(page.locator("#preview-summary")).toContainText("40 rows detected");
  await page.getByRole("button", { name: "Run assessment" }).click();
  await expect(page.getByRole("heading", { name: "2. Scorecard" })).toBeVisible({ timeout: 30_000 });
  await expect(page.locator("#cards")).toContainText("could not be assessed from an export");
  await expect(page.locator("#findings-count")).toContainText("95 of 95 findings");
  await page.locator("#f-severity").selectOption("critical");
  await page.locator("#f-state").selectOption("fail");
  await expect(page.locator("#findings-count")).toContainText("1 of 95 findings");
  await page.locator("tr.finding").first().click();
  await expect(page.locator("#detail")).toBeVisible();
  await expect(page.locator("#detail-list")).toContainText("CA-ZT-001");
  await expect(page.locator("#unknown-list")).toContainText("Budgets and cost alerts");
  await page.getByRole("button", { name: "Copy report" }).click();
  await expect(page.locator("#copy-note")).toContainText("copied");
  const clipboard = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboard).toContain("# Cloud assessment report");
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download bundle" }).click();
  expect((await download).suggestedFilename()).toMatch(/^assessment-[0-9a-f]{8}\.zip$/);
  page.once("dialog", (d) => d.accept());
  await page.getByRole("button", { name: "Delete my data now" }).click();
  await expect(page.getByRole("heading", { name: "2. Scorecard" })).toBeHidden();
  await expect(page.locator("#run-note")).toContainText("deleted");
});

test("pane copy never names vendors", async ({ page }) => {
  await page.goto("/");
  const text = (await page.locator("body").innerText()).toLowerCase();
  for (const word of ["cloudflare", "turnstile", "hostinger", "vps", "coder", "ttl"]) expect(text, word).not.toContain(word);
  await expect(page.locator("#notice")).toContainText("expires after two hours");
});

test("framed pane posts loading → ready → working → ready to the site origin under the production sandbox", async ({ page }) => {
  await page.goto(`http://127.0.0.1:${HOST_PORT}/host-page.html?addon=http://127.0.0.1:${API_PORT}`);
  const frame = page.frameLocator("#pane");
  await expect(frame.locator("#status")).toHaveText("Ready");
  await expect.poll(() => page.evaluate(() => (window as unknown as { __messages: string[] }).__messages)).toEqual(["loading", "ready"]);
  await expect(frame.locator("html")).toHaveClass(/dark/);
  await frame.getByRole("button", { name: "Use the sample export" }).click();
  await frame.getByRole("button", { name: "Run assessment" }).click();
  await expect(frame.getByRole("heading", { name: "2. Scorecard" })).toBeVisible({ timeout: 30_000 });
  await expect.poll(() => page.evaluate(() => (window as unknown as { __messages: string[] }).__messages)).toEqual(["loading", "ready", "working", "ready"]);
});

test("security headers and the health envelope", async ({ request }) => {
  const r = await request.get("/api/health");
  expect(r.status()).toBe(200);
  const body = await r.json();
  expect(body.id).toBe("cloud-assessment");
  expect(body.edition).toBe("lab");
  expect(body.azureConnectivity).toBe("disabled-by-design");
  expect(r.headers()["x-addon-id"]).toBe("cloud-assessment");
  expect(r.headers()["content-security-policy"]).toContain(`frame-ancestors http://127.0.0.1:${HOST_PORT}`);
  const missing = await request.post("/api/assessments", { data: { format: "arg-json", content: "[]" } });
  expect(missing.status()).toBe(422);
});
