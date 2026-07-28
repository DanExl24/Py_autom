import { Locator } from "playwright";
import { ctx } from "../Class/sofiaContext";
import { By } from "../shared/get_by";
export const go_to_menu = async (linkName: string): Promise<Locator> => {
  if (!ctx.page) {
    throw new Error("ctx.page no ha sido inicializado.");
  }

  const page = ctx.page;

  await page.locator(By.id("seleccionRol:roles")).selectOption("17");

  const menu = page.getByRole("link", {
    name: linkName,
  });

  await menu.click();

  return menu;
};

export const goto_menu_child = async (
  parent: Locator,
  child: string,
): Promise<Locator> => {
  const menu = parent.getByRole("link", {
    name: child,
  });

  await menu.click();

  return menu;
};
