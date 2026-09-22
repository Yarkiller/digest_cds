const { expect, test } = require("@playwright/test");

/**
 * Admin Digest SPA honesty gate (ADMIN-01, ADMIN-04, ADMIN-06, ADMIN-07, ADMIN-08;
 * D-77, D-80, D-85, D-86, D-87, D-90).
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
  // Reset module-level admin mocks between tests (Vite keeps singleton state).
  if (path.startsWith("/admin")) {
    await page.waitForFunction(() => Boolean(window.__DIGEST_ADMIN_HARNESS__));
    await page.evaluate((extra) => {
      window.__DIGEST_ADMIN_HARNESS__.resetAdminHarness();
      if (extra && typeof extra === "object") {
        for (const [key, value] of Object.entries(extra)) {
          window[key] = value;
        }
      }
    }, extraInit ?? null);
    await page.reload();
  }
}

async function approveReadyRows(page, indices) {
  const rows = page.getByTestId("admin-shortlist-row");
  for (const i of indices) {
    await rows.nth(i).getByRole("checkbox").check();
  }
  await page.getByRole("button", { name: /одобрить выбранные/i }).click();
  await expect(rows.nth(indices[0]).getByText("одобрен")).toBeVisible();
}

test.describe("Admin Digest — role gate (D-75, D-76, D-77, ADMIN-01)", () => {
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
    // D-77 / AUTH-03 remainder — Playwright employee deep-link proof
    await gotoAsRole(page, "employee", "/admin/digest");
    await expect(
      page.getByRole("heading", { name: "Недостаточно прав", exact: true }),
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

  test("/me network failure shows ServiceUnavailable not Forbidden", async ({
    page,
  }) => {
    // WR-03: transient /me outages must not look like 403
    await page.addInitScript(() => {
      window.__DIGEST_MOCK_ME_ROLE__ = "admin";
      window.__DIGEST_ME_FAIL_FETCH__ = true;
    });
    await page.goto("/admin/digest");
    await expect(page.getByTestId("service-unavailable")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Недостаточно прав", exact: true }),
    ).toHaveCount(0);
  });
});

test.describe("Admin Digest — shortlist triage (ADMIN-01…03, ADMIN-05, D-79, D-80)", () => {
  test("populated shortlist shows ≤5 rows with badges and score factors", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    await expect(
      page.getByRole("heading", { name: "Shortlist дайджеста", exact: true }),
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
      page.getByRole("heading", { name: "Кандидатов пока нет", exact: true }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: /обновить список/i })).toBeVisible();
    await expect(page.getByText(/пайплайн/i)).toHaveCount(0);
    await expect(page.getByTestId("admin-shortlist-row")).toHaveCount(0);
    // G-05-2: genuine empty (digest_rest=false) must not show post-send rest copy
    await expect(page.getByText(/дайджест успешно выпущен/i)).toHaveCount(0);
    await expect(page.getByTestId("admin-digest-rest")).toHaveCount(0);
  });

  test("loading shortlist does not flash empty success", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    // After harness reset+reload, assert we never land on empty copy while rows exist.
    await expect(page.getByTestId("admin-digest-page")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Кандидатов пока нет", exact: true }),
    ).toHaveCount(0);
    await expect(page.getByTestId("admin-shortlist-row")).toHaveCount(5);
  });

  test("Одобрить выбранные persists and shows одобрен caption", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    const firstRow = page.getByTestId("admin-shortlist-row").first();
    await firstRow.getByRole("checkbox").check();
    await page.getByRole("button", { name: /одобрить выбранные/i }).click();
    await expect(firstRow.getByText("одобрен")).toBeVisible();
  });

  test("Approve in-flight disables toolbar actions", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    const firstRow = page.getByTestId("admin-shortlist-row").first();
    await firstRow.getByRole("checkbox").check();
    const approveBtn = page.getByRole("button", { name: /одобрить выбранные/i });
    await approveBtn.click();
    // While request is in flight (mock delay), primary decision actions stay disabled.
    await expect(approveBtn).toBeDisabled();
    await expect(firstRow.getByText("одобрен")).toBeVisible();
  });
});

test.describe("Admin Digest — batch select + preview/send gate (ADMIN-04,06,07, D-85, D-86)", () => {
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

  test("preview failure keeps send locked", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest", {
      __DIGEST_ADMIN_FAIL_PREVIEW__: true,
    });
    await approveReadyRows(page, [0, 1]);

    const sendBtn = page.getByRole("button", { name: /отправить дайджест/i });
    await expect(sendBtn).toBeDisabled();

    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    await expect(emailDialog.getByText("Превью недоступно", { exact: true })).toBeVisible();
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();
    await expect(emailDialog).toHaveCount(0);

    await expect(page.getByText(/сначала откройте превью письма/i)).toBeVisible();
    await expect(sendBtn).toBeDisabled();
  });

  test("approved draft blocks send with draft hint (ADMIN-03/07, D-85)", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    const rows = page.getByTestId("admin-shortlist-row");
    // Rank 4 is draft in default mock batch
    await rows.nth(3).getByRole("checkbox").check();
    await page.getByRole("button", { name: /одобрить выбранные/i }).click();
    await expect(rows.nth(3).getByText("одобрен")).toBeVisible();

    await expect(
      page.getByTestId("admin-send-hint"),
    ).toContainText(/уберите черновики из одобренных или дождитесь ready/i);
    await expect(page.getByText(/· draft/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /отправить дайджест/i })).toBeDisabled();
    // Preview stays locked until there is ≥1 approved ready
    await expect(page.getByRole("button", { name: /предпросмотр письма/i })).toBeDisabled();
  });

  test("preview lists one approved-ready article (zero-one-many E4)", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    await approveReadyRows(page, [0]);

    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    await expect(emailDialog.getByText(/только одобренные ready/i)).toBeVisible();
    await expect(emailDialog.locator("li")).toHaveCount(1);
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();
  });

  test("Вводный текст appears in Превью письма (G-05-1 / ADMIN-04)", async ({
    page,
  }) => {
    const introPhrase = `Добрый день коллеги! G05-1-${Date.now()}`;
    await gotoAsRole(page, "admin", "/admin/digest");
    await page.getByLabel(/вводный текст/i).fill(introPhrase);
    await approveReadyRows(page, [0, 1]);

    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    await expect(emailDialog.getByTestId("email-preview-body")).toContainText(
      introPhrase,
    );
    await expect(emailDialog.locator("li")).toHaveCount(2);
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();
  });

  test("Блоки выпуска: reorder + interstitial text drive preview (G-05-1)", async ({
    page,
  }) => {
    const bridge = `Связка G05-1-${Date.now()}`;
    await gotoAsRole(page, "admin", "/admin/digest");
    await approveReadyRows(page, [0, 1]);

    const blocks = page.getByTestId("admin-issue-blocks");
    await expect(blocks).toBeVisible();
    // Primary control is reorderable blocks — schema free-text textarea is gone.
    await expect(page.getByLabel(/^блоки выпуска$/i)).toBeVisible();
    await expect(
      page.locator('section').filter({ hasText: 'Схема дайджеста' }).locator('textarea.font-mono'),
    ).toHaveCount(0);
    const materialBlocks = blocks.getByTestId("admin-issue-block-material");
    await expect(materialBlocks).toHaveCount(2);
    await expect(materialBlocks.nth(0)).toContainText(/Building Production RAG Systems/i);
    await expect(materialBlocks.nth(1)).toContainText(/Anomaly Detection in Audit Pipelines/i);

    await materialBlocks.nth(1).getByRole("button", { name: /выше|вверх|переместить вверх/i }).click();
    await expect(materialBlocks.nth(0)).toContainText(/Anomaly Detection in Audit Pipelines/i);
    await expect(materialBlocks.nth(1)).toContainText(/Building Production RAG Systems/i);

    await page.getByRole("button", { name: /добавить текст/i }).click();
    const textBlocks = blocks.getByTestId("admin-issue-block-text");
    await expect(textBlocks).toHaveCount(1);
    await textBlocks.first().getByRole("textbox").fill(bridge);

    // Place text between the two materials if it landed at the end: move up once.
    const textUp = textBlocks.first().getByRole("button", {
      name: /выше|вверх|переместить вверх/i,
    });
    if (await textUp.isEnabled()) {
      await textUp.click();
    }

    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    const previewLis = emailDialog.locator("li");
    await expect(previewLis).toHaveCount(2);
    await expect(previewLis.nth(0)).toContainText(/Anomaly Detection in Audit Pipelines/i);
    await expect(previewLis.nth(1)).toContainText(/Building Production RAG Systems/i);

    const body = emailDialog.getByTestId("email-preview-body");
    await expect(body).toContainText(bridge);
    const bodyText = await body.innerText();
    const anomalyAt = bodyText.indexOf("Anomaly Detection");
    const bridgeAt = bodyText.indexOf(bridge);
    const ragAt = bodyText.indexOf("Building Production");
    expect(anomalyAt).toBeGreaterThanOrEqual(0);
    expect(bridgeAt).toBeGreaterThan(anomalyAt);
    expect(ragAt).toBeGreaterThan(bridgeAt);

    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();
  });

  test("G-05-1: intro + interstitial in Превью письма; send records Отправка записана", async ({
    page,
  }) => {
    const introPhrase = `Привет! G05-1-${Date.now()}`;
    const bridge = `Связка между статьями G05-1-${Date.now()}`;
    await gotoAsRole(page, "admin", "/admin/digest");
    await page.getByLabel(/вводный текст/i).fill(introPhrase);
    await approveReadyRows(page, [0, 1]);

    const blocks = page.getByTestId("admin-issue-blocks");
    const materialBlocks = blocks.getByTestId("admin-issue-block-material");
    await expect(materialBlocks).toHaveCount(2);
    await materialBlocks.nth(1).getByRole("button", { name: /выше|вверх|переместить вверх/i }).click();

    await page.getByRole("button", { name: /добавить текст/i }).click();
    const textBlocks = blocks.getByTestId("admin-issue-block-text");
    await textBlocks.first().getByRole("textbox").fill(bridge);
    const textUp = textBlocks.first().getByRole("button", {
      name: /выше|вверх|переместить вверх/i,
    });
    if (await textUp.isEnabled()) {
      await textUp.click();
    }

    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    const body = emailDialog.getByTestId("email-preview-body");
    await expect(body).toContainText(introPhrase);
    await expect(body).toContainText(bridge);
    const bodyText = await body.innerText();
    const introAt = bodyText.indexOf(introPhrase);
    const anomalyAt = bodyText.indexOf("Anomaly Detection");
    const bridgeAt = bodyText.indexOf(bridge);
    const ragAt = bodyText.indexOf("Building Production");
    expect(introAt).toBeGreaterThanOrEqual(0);
    expect(anomalyAt).toBeGreaterThan(introAt);
    expect(bridgeAt).toBeGreaterThan(anomalyAt);
    expect(ragAt).toBeGreaterThan(bridgeAt);
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();

    const sendBtn = page.getByRole("button", { name: /отправить дайджест/i });
    await expect(sendBtn).toBeEnabled();
    await sendBtn.click();
    await page.getByRole("button", { name: /подтвердить отправку/i }).click();
    await expect(page.getByText("Отправка записана", { exact: true })).toBeVisible();
    const issueLink = page.getByRole("link", { name: /к выпуску/i });
    await expect(issueLink).toBeVisible();
    await expect(issueLink).toHaveAttribute("href", "/issues/15");
  });

  test("превью unlocks send; confirm records Отправка записана + issue link (D-90)", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    await approveReadyRows(page, [0, 1]);

    const sendBtn = page.getByRole("button", { name: /отправить дайджест/i });
    await expect(sendBtn).toBeDisabled();
    await expect(page.getByText(/сначала откройте превью письма/i)).toBeVisible();

    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    await expect(emailDialog.getByText(/только одобренные ready/i)).toBeVisible();
    await expect(emailDialog.locator("li")).toHaveCount(2);
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();
    await expect(emailDialog).toHaveCount(0);

    await expect(page.getByText(/превью просмотрено\. можно отправить/i)).toBeVisible();
    await expect(sendBtn).toBeEnabled();

    await sendBtn.click();
    await expect(
      page.getByRole("heading", { name: "Подтвердите отправку", exact: true }),
    ).toBeVisible();
    await page.getByRole("button", { name: /подтвердить отправку/i }).click();
    await expect(page.getByText("Отправка записана", { exact: true })).toBeVisible();
    // D-90 / ADMIN-08 — success surfaces same-origin issue path for returnUrl integrity
    const issueLink = page.getByRole("link", { name: /к выпуску/i });
    await expect(issueLink).toBeVisible();
    await expect(issueLink).toHaveAttribute("href", "/issues/15");

    // Second attempt locked — already sent
    await expect(page.getByTestId("admin-send-hint")).toContainText(/уже отправлено/i);
    await expect(sendBtn).toBeDisabled();
  });

  test("G-05-2: after Отправка записана shortlist hides; rest copy shown", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest");
    await approveReadyRows(page, [0, 1]);
    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();

    await page.getByRole("button", { name: /отправить дайджест/i }).click();
    await page.getByRole("button", { name: /подтвердить отправку/i }).click();

    await expect(page.getByText("Отправка записана", { exact: true })).toBeVisible();
    await expect(page.getByText(/дайджест успешно выпущен/i)).toBeVisible();
    await expect(
      page.getByText(/Следующие материалы будут подготовлены через 7 дней/i),
    ).toBeVisible();
    await expect(page.getByTestId("admin-shortlist")).toHaveCount(0);
    await expect(page.getByTestId("admin-shortlist-row")).toHaveCount(0);
    await expect(page.getByRole("checkbox")).toHaveCount(0);
    await expect(page.getByText("Кандидатов пока нет", { exact: true })).toHaveCount(0);
    await expect(page.getByTestId("admin-send-hint")).toContainText(/уже отправлено/i);
  });

  test("G-05-2: Уже отправлено enters rest hide without inactive checkboxes", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest", {
      __DIGEST_ADMIN_ALREADY_SENT__: true,
    });
    await approveReadyRows(page, [0]);
    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();
    await page.getByRole("button", { name: /отправить дайджест/i }).click();
    await page.getByRole("button", { name: /подтвердить отправку/i }).click();

    await expect(page.getByRole("status").filter({ hasText: "Уже отправлено" })).toBeVisible();
    await expect(page.getByText(/дайджест успешно выпущен/i)).toBeVisible();
    await expect(page.getByTestId("admin-shortlist")).toHaveCount(0);
    await expect(page.getByRole("checkbox")).toHaveCount(0);
  });

  test("G-05-2: cold load digest_rest shows rest instead of Кандидатов пока нет", async ({
    page,
  }) => {
    await gotoAsRole(page, "admin", "/admin/digest", {
      __DIGEST_ADMIN_DIGEST_REST__: true,
    });
    await expect(page.getByText(/дайджест успешно выпущен/i)).toBeVisible();
    await expect(
      page.getByText(/Следующие материалы будут подготовлены через 7 дней/i),
    ).toBeVisible();
    await expect(page.getByText("Кандидатов пока нет", { exact: true })).toHaveCount(0);
    await expect(page.getByTestId("admin-shortlist")).toHaveCount(0);
    await expect(page.getByRole("checkbox")).toHaveCount(0);
  });

  test("Уже отправлено when batch already sent", async ({ page }) => {
    await gotoAsRole(page, "admin", "/admin/digest", {
      __DIGEST_ADMIN_ALREADY_SENT__: true,
    });
    await approveReadyRows(page, [0]);
    await page.getByRole("button", { name: /предпросмотр письма/i }).click();
    const emailDialog = page.getByRole("dialog").filter({
      has: page.getByRole("heading", { name: "Превью письма", exact: true }),
    });
    await expect(emailDialog.getByText(/только одобренные ready/i)).toBeVisible();
    await emailDialog.getByRole("button", { name: "Закрыть", exact: true }).click();
    await expect(emailDialog).toHaveCount(0);

    await page.getByRole("button", { name: /отправить дайджест/i }).click();
    await page.getByRole("button", { name: /подтвердить отправку/i }).click();
    await expect(page.getByRole("status").filter({ hasText: "Уже отправлено" })).toBeVisible();
  });
});
