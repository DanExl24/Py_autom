import { chromium, FrameLocator } from "playwright";
import { configSofia } from "./config";
import { ctx } from "./Class/sofiaContext";
import { descargar_juicios_fichas } from "./reporte_juicios/descargar_JE";
const rellenarForm = async (frame: FrameLocator) => {
  await frame.locator("#tipoId").selectOption("CC");
  await frame.locator("#username").fill("1014302196");
  await frame.locator("[name='josso_password']").fill("Jd1014302196*2026");
  await frame.getByRole("button", { name: "Ingresar" }).click();
};

(async () => {
  const { page } = await configSofia();
  await page.goto("http://senasofiaplus.edu.co/sofia-public/");
  ctx.page = page;
  if (!page.url().includes("/principal.faces")) {
    const frame = page.frameLocator("#registradoBox1");
    await rellenarForm(frame);

    await page.waitForURL(
      "http://senasofiaplus.edu.co/sofia/home/principal.faces",
    );

    await page.context().storageState({
      path: "auth.json",
    });
  }
  await descargar_juicios_fichas();
})();
