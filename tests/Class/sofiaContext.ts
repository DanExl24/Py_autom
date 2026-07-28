import { FrameLocator, Page } from "@playwright/test";
import type { Ficha } from "../shared/sofiaTypes.types";
class SofiaContext {
  page!: Page;
  currentProgram?: Ficha;
  get mainFrame(): FrameLocator {
    return this.page.frameLocator('iframe[name="contenido"]');
  }
}

export const ctx = new SofiaContext();
