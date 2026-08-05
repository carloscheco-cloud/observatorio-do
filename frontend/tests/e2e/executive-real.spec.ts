import { expect, test, type Page } from "@playwright/test";

test.skip(process.env.PE08_REAL_E2E !== "true", "Requiere PostgreSQL y PE-07 locales controlados");

const completeInstitutions = [
  ["ministerio-de-administracion-publica", "Ministerio de Administración Pública", "76"],
  ["ministerio-de-hacienda-y-economia", "Ministerio de Hacienda y Economía", "91"],
  ["ministerio-de-educacion", "Ministerio de Educación", "83"],
  ["ministerio-de-salud-publica-y-asistencia-social", "Ministerio de Salud Pública y Asistencia Social", "68"],
  ["ministerio-de-medio-ambiente-y-recursos-naturales", "Ministerio de Medio Ambiente y Recursos Naturales", "91"],
] as const;

function observe(page: Page) {
  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];
  const badResponses: string[] = [];
  page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("requestfailed", request => failedRequests.push(`${request.method()} ${request.url()}`));
  page.on("response", response => { if (response.status() >= 400 && !response.url().includes("__nextjs")) badResponses.push(`${response.status()} ${response.url()}`); });
  return { consoleErrors, failedRequests, badResponses };
}

async function expectNoHorizontalOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
}

test("MVP conectado muestra resumen, directorio, filtros y metodología", async ({ page }) => {
  const observed = observe(page);
  await page.goto("/poder-ejecutivo");
  await expect(page.getByRole("heading", { name: "Poder Ejecutivo", exact: true })).toBeVisible();
  for (const value of ["25", "23", "5", "20"]) await expect(page.getByText(value, { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Desactivada", { exact: true })).toBeVisible();
  await expect(page.getByText(/La puntuación mide disponibilidad y calidad documental observada/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Directorio institucional" })).toBeVisible();
  await page.getByLabel("Buscar institución").fill("Agricultura");
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  await expect(page.getByRole("heading", { name: "Ministerio de Agricultura" })).toBeVisible();
  expect(observed).toEqual({ consoleErrors: [], failedRequests: [], badResponses: [] });
});

test("ficha parcial conserva cobertura y pendientes sin convertir ausencia en cero", async ({ page }) => {
  await page.goto("/poder-ejecutivo/instituciones/ministerio-de-agricultura");
  await expect(page.getByRole("heading", { name: "Ministerio de Agricultura", exact: true })).toBeVisible();
  await expect(page.getByText(/cobertura 45/).first()).toBeVisible();
  await expect(page.getByText(/partial/).first()).toBeVisible();
  await expect(page.getByText("Pendiente de evaluación", { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/No se localizaron datos estructurados|No disponible/).first()).toBeVisible();
});

for (const [slug, name, score] of completeInstitutions) {
  test(`${name} conserva evaluación PE-06D`, async ({ page }) => {
    const observed = observe(page);
    await page.goto(`/poder-ejecutivo/instituciones/${slug}`);
    await expect(page.getByRole("heading", { name, exact: true })).toBeVisible();
    await expect(page.getByText(new RegExp(`${score}(?:\\.0+)? de 100 puntos disponibles`))).toBeVisible();
    await expect(page.getByText(/cobertura 100/).first()).toBeVisible();
    await expect(page.getByText(/OED-TD-1\.1/).first()).toBeVisible();
    await expect(page.getByRole("progressbar")).toHaveCount(8);
    await expect(page.getByRole("heading", { name: "Limitaciones" }).first()).toBeVisible();
    await expect(page.getByText(/mejor institución|peor institución|\btop\b|\bpuesto\b|comparison_position|\brank\b/i)).toHaveCount(0);
    expect(observed).toEqual({ consoleErrors: [], failedRequests: [], badResponses: [] });
  });
}

test("MISPAS documenta estabilidad técnica sin afirmación acusatoria", async ({ page }) => {
  await page.goto("/poder-ejecutivo/instituciones/ministerio-de-salud-publica-y-asistencia-social");
  const stability = page.getByRole("heading", { name: /estabilidad/i }).locator("..");
  await expect(stability.getByText(/4 de 5/)).toBeVisible();
  await expect(stability.getByText(/limitación menor/i)).toBeVisible();
  await expect(page.getByText(/broken_link_confirmed/i)).toHaveCount(0);
});

test("autoridades, cambios, detalle y 404 son navegables", async ({ page }) => {
  await page.goto("/poder-ejecutivo/autoridades");
  await expect(page.getByRole("heading", { name: "Autoridades", exact: true })).toBeVisible();
  await page.getByLabel("Buscar").fill("Luis");
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  const detail = page.getByRole("link", { name: "Ver detalle" }).first();
  await expect(detail).toBeVisible(); await detail.click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.goto("/poder-ejecutivo/autoridades/00000000-0000-0000-0000-000000000000");
  await expect(page.getByRole("heading", { name: /Not Found|no localizada/i })).toBeVisible();
  await page.goto("/poder-ejecutivo/cambios");
  await expect(page.getByText(/no son noticias ni interpretaciones políticas/i)).toBeVisible();
  await page.getByLabel("Tipo").selectOption("new_assessment");
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  await expect(page.locator(".timeline li").first()).toBeVisible();
});

for (const viewport of [{width:360,height:800},{width:390,height:844},{width:768,height:1024},{width:1440,height:900}]) {
  test(`responsive ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport); await page.goto("/poder-ejecutivo");
    await expectNoHorizontalOverflow(page);
    await page.keyboard.press("Tab"); await expect(page.locator(":focus")).toBeVisible();
    await expect(page.getByLabel("Buscar institución")).toBeVisible();
  });
}

test("genera evidencia visual local con datos persistidos", async ({ page }) => {
  await page.setViewportSize({width:1440,height:900}); await page.goto("/poder-ejecutivo");
  await page.screenshot({path:"test-results/pe08-real-desktop.png",fullPage:true});
  await page.setViewportSize({width:390,height:844}); await page.goto("/poder-ejecutivo");
  await page.screenshot({path:"test-results/pe08-real-mobile.png",fullPage:true});
  await page.setViewportSize({width:1440,height:900}); await page.goto("/poder-ejecutivo/instituciones/ministerio-de-agricultura");
  await page.screenshot({path:"test-results/pe08-real-partial.png",fullPage:true});
  await page.goto("/poder-ejecutivo/instituciones/ministerio-de-administracion-publica");
  await page.screenshot({path:"test-results/pe08-real-complete.png",fullPage:true});
});
