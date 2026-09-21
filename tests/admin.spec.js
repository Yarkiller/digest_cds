const { expect, test } = require("@playwright/test");

/**
 * Admin Digest SPA contracts (D-75, D-76, ADMIN-01…07).
 * Role harness: sticky window.__DIGEST_MOCK_ME_ROLE__ (employee default).
 */

async function gotoAsRole(page, role, path = "/", extraInit) {
  await page.addInitScript(
    ({ r, extra }) => {
      window.__DIGEST_MOCK_ME_ROLE__ = r;
      if (extra && typeof extra === "object") {
        for (const [key, value] of Object.entries(extra)) {
          window[key] = value;
        }
      }
    },
    { r: role, extra: extraInit ?? null },
  );
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

test.describe("Admin Digest — shortlist triage (ADMIN-01…03, ADMIN-05, D-79, D-80)", () => {
  test("populated shortlist shows ≤5 rows with badges and score factors", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    await expect(
      page.getByRole("heading", { name: "Shortlist дайджеста" }),
    ).toBeVisible();
    const list = page.getByTestId("admin-shortlist");
    await expect(list).toBeVisible();
    const rows = page.getByTestId("admin-shortlist-row");
    await expect(rows).toHaveCount(5);
    await expect(rows.first()).toContainText(/ready/i);
    await expect(page.getByText("обоснование недоступно").first()).toBeVisible();
    await expect(page.getByText(/relevance · freshness/i).first()).toBeVisible();
  });

  test("empty shortlist shows Кандидатов пока нет without пайплайн", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest", {
      __DIGEST_ADMIN_EMPTY__: true,
    });
    await expect(
      page.getByRole("heading", { name: "Кандидатов пока нет" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: /обновить список/i })).toBeVisible();
    await expect(page.getByText(/пайплайн/i)).toHaveCount(0);
    await expect(page.getByTestId("admin-shortlist-row")).toHaveCount(0);
  });

  test("Одобрить выбранные persists and shows одобрен caption", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    const firstRow = page.getByTestId("admin-shortlist-row").first();
    await firstRow.getByRole("checkbox").check();
    await page.getByRole("button", { name: /одобрить выбранные/i }).click();
    await expect(firstRow.getByText("одобрен")).toBeVisible();
  });
});

test.describe("Admin Digest — batch select + preview/send gate (ADMIN-04,06,07)", () => {
  test("Выбрать все and Оставить топ-3 update checkboxes", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    const rows = page.getByTestId("admin-shortlist-row");
    await expect(rows).toHaveCount(5);

    await page.getByRole("button", { name: /выбрать все/i }).click();
    for (let i = 0; i < 5; i += 1) {
      await expect(rows.nth(i).getByRole("checkbox")).toBeChecked();
    }

    await page.getByRole("button", { name: /оставить топ-3/i }).click();
    for (let i = 0; i < 3; i += 1) {
      await expect(rows.nth(i).getByRole("checkbox")).toBeChecked();
    }
    await expect(rows.nth(3).getByRole("checkbox")).not.toBeChecked();
    await expect(rows.nth(4).getByRole("checkbox")).not.toBeChecked();

    await rows.nth(1).getByRole("checkbox").uncheck();
    await expect(rows.nth(0).getByRole("checkbox")).toBeChecked();
    await expect(rows.nth(1).getByRole("checkbox")).not.toBeChecked();
    await expect(rows.nth(2).getByRole("checkbox")).toBeChecked();
  });

  test("превью unlocks send; confirm records Отправка записана", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    const rows = page.getByTestId("admin-shortlist-row");
    // Approve two ready rows (ranks 1 and 2)
    await rows.nth(0).getByRole("checkbox").check();
    await rows.nth(1).getByRole("checkbox").check();
    await page.getByRole("button", { name: /одобрить выбранные/i }).click();
    await expect(rows.nth(0).getByText("одобрен")).toBeVisible();

    const sendBtn = page.getByRole("button", { name: /отправить дайджест/i });
    await expect(sendBtn).toBeDisabled();
    await expect(page.getByText(/сначала откройте превью письма/i)).toBeVisible();

    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    await expect(page.getByRole("heading", { name: "Превью письма" })).toBeVisible();
    await page.getByRole("button", { name: "Закрыть" }).click();

    await expect(page.getByText(/превью просмотрено\. можно отправить/i)).toBeVisible();
    await expect(sendBtn).toBeEnabled();

    await sendBtn.click();
    await expect(page.getByRole("heading", { name: "Подтвердите отправку" })).toBeVisible();
    await page.getByRole("button", { name: /подтвердить отправку/i }).click();
    await expect(page.getByText("Отправка записана")).toBeVisible();
  });

  test("Уже отправлено when batch already sent", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest", {
      __DIGEST_ADMIN_ALREADY_SENT__: true,
    });
    const rows = page.getByTestId("admin-shortlist-row");
    await rows.nth(0).getByRole("checkbox").check();
    await page.getByRole("button", { name: /одобрить выбранные/i }).click();
    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    await expect(page.getByRole("heading", { name: "Превью письма" })).toBeVisible();
    await page.getByRole("button", { name: "Закрыть" }).click();

    await page.getByRole("button", { name: /отправить дайджест/i }).click();
    await page.getByRole("button", { name: /подтвердить отправку/i }).click();
    await expect(page.getByText("Уже отправлено")).toBeVisible();
  });
});
