import { ctx } from "../prueba.spec";
import { By } from "./get_by";
import { modal_buscar_ficha } from "./sofia_ids";
import { Locator } from "@playwright/test";
export const abrir_modal = async (
  boton: string | Locator,
  id_iframe: string,
) => {
  const locator =
    typeof boton === "string" ? ctx.mainFrame.locator(By.id(boton)) : boton;

  await locator.waitFor();
  await locator.click();

  return ctx.mainFrame.frameLocator(By.id(id_iframe));
};

export const consultar_ficha = async (
  boton: string | Locator,
  id_iframe: string,
  ficha?: string,
) => {
  const id_ficha = ficha ?? ctx.currentProgram?.ficha;

  if (!id_ficha) {
    throw new Error("No hay ficha para consultar");
  }
  const frame_modal = await abrir_modal(boton, id_iframe);
  await frame_modal.locator(By.id(modal_buscar_ficha.fichaInput)).waitFor();
  await frame_modal
    .locator(By.id(modal_buscar_ficha.fichaInput))
    .fill(id_ficha);
  await frame_modal.locator(By.id(modal_buscar_ficha.btnBuscar)).click();
  await frame_modal
    .getByRole("row", { name: id_ficha })
    .getByRole("link")
    .click();
};
