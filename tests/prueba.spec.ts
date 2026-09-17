import { chromium, FrameLocator } from "playwright";
import { configSofia } from "./config";
import { ctx } from "./Class/sofiaContext";
import { descargar_juicios_fichas } from "./reporte_juicios/descargar_JE";
const rellenarForm = async (frame: FrameLocator) => {
  const username = process.env.SOFIA_USERNAME || "";
  const password = process.env.SOFIA_PASSWORD || "";

  if (!username || !password) {
    throw new Error(
      "Credenciales no configuradas. Define SOFIA_USERNAME y SOFIA_PASSWORD en las variables de entorno o archivo .env."
    );
  }

  await frame.locator("#tipoId").selectOption("CC");
  await frame.locator("#username").fill(username);
  await frame.locator("[name='josso_password']").fill(password);
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
