const { expect, test } = require("@playwright/test");

test.describe("web app main flows", () => {
  test("opens a material from the issue table of contents", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: /новости ds для сва/i })).toBeVisible();
    await page.getByRole("link", { name: /building production rag systems/i }).click();

    await expect(page).toHaveURL(/\/materials\/rag-systems/);
    await expect(page.getByRole("heading", { name: /building production rag systems/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /резюме/i })).toBeVisible();
  });

  test("lets a reader pick a voting topic and confirm", async ({ page }) => {
    await page.goto("/voting");

    const confirm = page.getByTestId("confirm-vote");
    await expect(confirm).toBeDisabled();

    await page.getByRole("radio", { name: /RAG в корпоративной среде/i }).click();
    await expect(confirm).toBeEnabled();
    await confirm.click();

    await expect(confirm).toHaveAttribute("data-state", "success");
    await expect(page.getByRole("status")).toContainText(/ваш голос:\s*RAG в корпоративной среде/i);
  });

  test("filters knowledge materials by tag facet", async ({ page }) => {
    await page.goto("/knowledge");

    await page.getByLabel("Теги").selectOption("SQL");
    await expect(page.getByText(/показано \d+ из \d+/i)).toBeVisible();
    await expect(page.getByRole("link", { name: /anomaly detection/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /building production rag systems/i })).toHaveCount(0);
  });
});

test.describe("web app UI states", () => {
  test("confirms a vote with loading then success state", async ({ page }) => {
    await page.goto("/voting");

    await page.getByRole("radio", { name: /RAG в корпоративной среде/i }).click();
    const confirm = page.getByTestId("confirm-vote");
    await confirm.click();

    await expect(confirm).toHaveAttribute("data-state", "loading");
    await expect(confirm).toHaveAttribute("data-state", "success");
    await expect(confirm).toHaveText(/голос принят/i);
    await expect(page.getByRole("status")).toContainText(/ваш голос:/i);
  });

  test("shows empty-state recovery when knowledge search misses", async ({ page }) => {
    await page.goto("/knowledge");

    await page.getByRole("searchbox", { name: /поиск по базе знаний/i }).fill("zzz-no-such-material");
    await expect(page.getByRole("heading", { name: /ничего не нашли/i })).toBeVisible();

    await page.getByRole("button", { name: /сбросить фильтры/i }).click();
    await expect(page.getByRole("heading", { name: /ничего не нашли/i })).toHaveCount(0);
    await expect(page.getByText(/показано \d+ из \d+/i)).toBeVisible();
  });

  test("loads more knowledge results after a loading state", async ({ page }) => {
    await page.goto("/knowledge");

    const loadMore = page.getByRole("button", { name: /загрузить ещё/i });
    await expect(loadMore).toBeVisible();
    await loadMore.click();

    await expect(page.getByTestId("kb-skeleton")).toBeVisible();
    await expect(page.getByRole("link", { name: /SQL-дашборды для аудиторской отчётности/i })).toBeVisible();
    await expect(loadMore).toBeHidden();
  });

  test("keeps header search as an enlarged inline field without a modal", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("dialog")).toHaveCount(0);
    const headerSearch = page.getByRole("searchbox", { name: /поиск digest cds/i });
    await expect(headerSearch).toBeVisible();

    const box = await headerSearch.boundingBox();
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
    expect(box?.width ?? 0).toBeGreaterThanOrEqual(240);

    await page.keyboard.press("Control+k");
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(headerSearch).toBeFocused();

    await headerSearch.fill("RAG");
    await headerSearch.press("Enter");
    await expect(page).toHaveURL(/\/knowledge/);
    await expect(page.getByRole("searchbox", { name: /поиск по базе знаний/i })).toHaveValue("RAG");
  });
});

test.describe("web app edge and error cases", () => {
  test("shows not-found recovery for an unknown material id", async ({ page }) => {
    await page.goto("/materials/does-not-exist");

    await expect(page.getByRole("heading", { name: /материал не найден/i })).toBeVisible();
    await page.getByRole("link", { name: /к выпуску/i }).click();
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole("heading", { name: /новости ds для сва/i })).toBeVisible();
  });

  test("keeps confirm vote disabled when no topic is selected", async ({ page }) => {
    await page.goto("/voting");

    const confirm = page.getByTestId("confirm-vote");
    await expect(confirm).toBeDisabled();
    await expect(page.getByRole("status")).toContainText(/не отдан/i);
  });

  test("shows vote error state and recovers on retry", async ({ page }) => {
    await page.goto("/voting?simulateError=1");

    await page.getByRole("radio", { name: /RAG в корпоративной среде/i }).click();
    const confirm = page.getByTestId("confirm-vote");
    await confirm.click();

    await expect(confirm).toHaveAttribute("data-state", "loading");
    await expect(confirm).toHaveAttribute("data-state", "error");
    await expect(confirm).toHaveText(/повторить/i);

    const alert = page.getByRole("alert");
    await expect(alert).toBeVisible();
    await expect(alert.getByRole("heading", { name: /ошибка сохранения/i })).toBeVisible();
    await expect(alert).toContainText(/временно недоступен|соединен/i);
    await expect(alert).toContainText(/попытка 1/i);

    await confirm.click();
    await expect(confirm).toHaveAttribute("data-state", "success");
    await expect(confirm).toHaveText(/голос принят/i);
    await expect(page.getByRole("status")).toContainText(/ваш голос:/i);
    await expect(page.getByRole("alert")).toHaveCount(0);
  });
});

test.describe("web app responsive", () => {
  test("keeps mobile shell usable without horizontal overflow", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });

    for (const path of ["/", "/knowledge", "/voting"]) {
      await page.goto(path);

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollWidth, `overflow on ${path}`).toBeLessThanOrEqual(overflow.clientWidth + 1);

      await expect(page.getByRole("navigation", { name: /основная навигация/i })).toBeVisible();
      await expect(page.getByRole("searchbox", { name: /поиск digest cds/i })).toBeVisible();
      await expect(page.getByText("Мария Сидорова")).toBeHidden();
    }

    await page.goto("/");
    await page.screenshot({
      path: "docs/digest-cds/responsive-evidence/mobile-390-issue.png",
      fullPage: true,
    });
  });

  test("avoids horizontal overflow on a narrow 320px phone", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("/");

    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);

    const search = page.getByRole("searchbox", { name: /поиск digest cds/i });
    await expect(search).toBeVisible();
    const box = await search.boundingBox();
    expect(box?.width ?? 0).toBeLessThanOrEqual(320);

    await page.screenshot({
      path: "docs/digest-cds/responsive-evidence/mobile-320-issue.png",
      fullPage: true,
    });
  });

  test("shows desktop identity and a wider header search", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("/");

    await expect(page.getByText("Мария Сидорова")).toBeVisible();

    const box = await page.getByRole("searchbox", { name: /поиск digest cds/i }).boundingBox();
    expect(box?.width ?? 0).toBeGreaterThanOrEqual(280);

    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);

    await page.screenshot({
      path: "docs/digest-cds/responsive-evidence/desktop-1280-issue.png",
      fullPage: true,
    });
  });

  test("keeps voting confirm reachable on a phone viewport", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/voting");

    await page.getByRole("radio", { name: /RAG в корпоративной среде/i }).click();
    const confirm = page.getByTestId("confirm-vote");
    await expect(confirm).toBeVisible();
    await expect(confirm).toBeInViewport();

    await page.screenshot({
      path: "docs/digest-cds/responsive-evidence/mobile-390-voting.png",
      fullPage: true,
    });
  });
});
