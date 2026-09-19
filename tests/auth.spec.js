const { expect, test } = require("@playwright/test");

test.describe("SPA auth contracts", () => {
  test("rejects disallowed email domain without creating a session", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel(/^email$/i).fill("user@gmail.com");
    await page.getByLabel(/^пароль$/i).fill("any-password");
    await page.getByRole("button", { name: /войти/i }).click();

    await expect(
      page.getByText(/вход только с корпоративного домена сва/i),
    ).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByTestId("auth-sign-in-calls")).toHaveAttribute(
      "data-count",
      "0",
    );
  });

  test("navigates to current issue after successful login without returnUrl", async ({
    page,
  }) => {
    await page.goto("/login");

    await page.getByLabel(/^email$/i).fill("analyst@sberbank.ru");
    await page.getByLabel(/^пароль$/i).fill("correct-horse");
    await page.getByRole("button", { name: /войти/i }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(
      page.getByRole("heading", { name: /новости ds для сва/i }),
    ).toBeVisible();
  });

  test("redirects protected route to login with returnUrl when auth gate is on", async ({
    page,
  }) => {
    await page.addInitScript(() => {
      window.__DIGEST_FORCE_AUTH_GATE__ = true;
    });

    await page.goto("/voting");

    await expect(page).toHaveURL(/\/login\?returnUrl=%2Fvoting/);
    await expect(page.getByRole("heading", { name: /digest cds/i })).toBeVisible();
  });

  test("returns to returnUrl path after successful login", async ({ page }) => {
    await page.goto("/login?returnUrl=/voting");

    await page.getByLabel(/^email$/i).fill("analyst@sberbank.ru");
    await page.getByLabel(/^пароль$/i).fill("correct-horse");
    await page.getByRole("button", { name: /войти/i }).click();

    await expect(page).toHaveURL(/\/voting$/);
    await expect(page.getByTestId("confirm-vote")).toBeVisible();
  });

  test("shows retryable network banner when sign-in fails", async ({ page }) => {
    await page.goto("/login");
    await page.waitForFunction(() => Boolean(window.__DIGEST_AUTH_HARNESS__));
    await page.evaluate(() => window.__DIGEST_AUTH_HARNESS__.armFailNextSignIn());

    await page.getByLabel(/^email$/i).fill("analyst@sberbank.ru");
    await page.getByLabel(/^пароль$/i).fill("correct-horse");
    await page.getByRole("button", { name: /войти/i }).click();

    await expect(page.getByRole("alert")).toContainText(/сервис входа временно недоступен/i);
    await expect(page.getByRole("button", { name: /повторить/i })).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test("shows mock CurrentUser identity and accepts platform ping", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel(/^email$/i).fill("analyst@sberbank.ru");
    await page.getByLabel(/^пароль$/i).fill("correct-horse");
    await page.getByRole("button", { name: /войти/i }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByTestId("platform-me")).toContainText(/analyst@sberbank\.ru/i);

    await page.getByRole("button", { name: /проверить ping/i }).click();
    await expect(page.getByTestId("platform-ping")).toContainText(/ok/i);
  });
});
