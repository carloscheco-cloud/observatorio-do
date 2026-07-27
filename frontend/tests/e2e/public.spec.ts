import { expect, test } from "@playwright/test";

const api = "http://127.0.0.1:8000/api/v1/public";

test("inicio, búsqueda y perfil institucional usan datos reales", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Datos trazables/i })).toBeVisible();
  await page.getByLabel("Buscar en el Estado").fill("Ayuntamiento");
  await page.getByRole("button", { name: "Buscar" }).click();
  await expect(page).toHaveURL(/buscar/);
  const result = page.getByRole("link", { name: /Ayuntamiento Municipal de Bonao/i });
  await expect(result).toBeVisible();
  await result.click();
  await expect(page.getByRole("heading", { name: /Ayuntamiento Municipal de Bonao/i })).toBeVisible();
  for (const heading of ["Estructura", "Nómina", "Presupuesto", "Compras", "Deuda", "Patrimonio", "Fuentes"]) {
    await expect(page.getByRole("heading", { name: heading, exact: true })).toBeVisible();
  }
});

test("dominios, comparador, fuentes y metodología son navegables", async ({ page }) => {
  for (const [path, heading] of [
    ["/nomina", "Nómina pública"],
    ["/presupuesto", "Presupuesto"],
    ["/compras", "Compras públicas"],
    ["/deuda", "Deuda pública"],
    ["/patrimonio", "Patrimonio público"],
    ["/alertas", "Alertas públicas"],
    ["/comparar", "Comparar"],
    ["/fuentes", "Fuentes"],
    ["/metodologia", "Metodología"],
  ]) {
    await page.goto(path);
    await expect(page.getByRole("heading", { name: heading, exact: true })).toBeVisible();
  }
});

test("exportación CSV y privacidad pública", async ({ request }) => {
  const csv = await request.get(`${api}/export?resource=institutions&format=csv`);
  expect(csv.ok()).toBeTruthy();
  expect(csv.headers()["content-type"]).toContain("text/csv");
  const body = (await csv.text()).toLowerCase();
  for (const forbidden of ["raw_payload", "national_id_hash", "vin_hash", "serial_hash", "policy_hash"]) {
    expect(body).not.toContain(forbidden);
  }
});

test("las rutas internas no forman parte de la superficie pública", async ({ request }) => {
  const response = await request.get(`${api}/internal/source-catalog`);
  expect(response.status()).toBe(404);
});
