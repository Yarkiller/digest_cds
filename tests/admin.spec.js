const { expect, test } = require("@playwright/test");

/**
 * Admin Digest SPA contracts (D-75, D-76, ADMIN-01…07).
 * Role harness: sticky window.__DIGEST_MOCK_ME_ROLE__ (employee default).
 */

async function gotoAsRole(page, role, path = "/") {
  await page.addInitScript((r) => {
    window.__DIGEST_MOCK_ME_ROLE__ = r;
  }, role);
  await page.goto(path);
}

test.describe("Admin Digest — role gate (D-75, D-76, ADMIN-01)", () => {
  test("employee never sees Админ nav link", async ({ page }) => {
    await gotoAsRole(page, "employee", "/");
    await expect(page.getByRole("navigation", { name: /основная навигация/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /^Админ$/ })).toHaveCount(0);
  });

  test("admin sees Админ nav linking to /admin/digest", async ({ page }) => {
    await gotoAsRole(page, "admin", "/");
    const adminLink = page.getByRole("link", { name: /^Админ$/ });
    await expect(adminLink).toBeVisible();
    await expect(adminLink).toHaveAttribute("href", "/admin/digest");
  });

  test("employee deep-link /admin/digest shows 403 Недостаточно прав", async ({
    page,
  }) => {
    await gotoAsRole(page, "employee", "/admin/digest");
    await expect(
      page.getByRole("heading", { name: "Недостаточно прав" }),
    ).toBeVisible();
    await expect(
      page.getByText(/этот раздел доступен только администраторам digest cds/i),
    ).toBeVisible();
    const cta = page.getByRole("link", { name: /на выпуск/i });
    await expect(cta).toBeVisible();
    await expect(cta).toHaveAttribute("href", "/");
    await expect(page.getByText(/shortlist дайджеста/i)).toHaveCount(0);
    await expect(page.getByTestId("admin-shortlist")).toHaveCount(0);
  });
});
