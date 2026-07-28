import { chromium } from "playwright";
import fs from "node:fs";
import { ctx } from "./Class/sofiaContext";

export const configSofia = async () => {
  const browser = await chromium.launch({ headless: false });

  const context = await browser.newContext(
    fs.existsSync("auth.json") ? { storageState: "auth.json" } : {},
  );

  const page = await context.newPage();

  return { browser, context, page };
};
