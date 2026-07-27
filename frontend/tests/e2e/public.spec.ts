import { expect, test } from "@playwright/test";
test("home, search, profile and public domains are navigable", async ({ page }) => {
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: /Datos trazables/i })).toBeVisible();
  await page.getByLabel("Buscar en el Estado").fill("Ayuntamiento ficticio");
  await page.getByRole("button", { name: "Buscar" }).click();
  await expect(page).toHaveURL(/buscar/);
  await page.goto("/instituciones/00000000-0000-0000-0000-000000000001");
  await expect(page.getByRole("heading", { name: "Institución" })).toBeVisible();
  await page.goto("/presupuesto");
  await expect(page.getByRole("heading", { name: "Presupuesto" })).toBeVisible();
  await page.goto("/compras");
  await expect(page.getByRole("heading", { name: "Compras públicas" })).toBeVisible();
});
