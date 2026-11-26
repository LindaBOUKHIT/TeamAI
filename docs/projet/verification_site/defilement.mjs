import { chromium, firefox, webkit, devices } from "playwright";
const URL = process.env.SITE ?? "https://lindaboukhit.github.io/TeamAI/";
for (const [t, name, ctx] of [[chromium, "pixel", devices["Pixel 7"]], [webkit, "iphone", devices["iPhone 13"]], [chromium, "desktop", { viewport: { width: 1366, height: 900 } }], [webkit, "ipad", devices["iPad (gen 7)"]]]) {
  const b = await t.launch(); const p = await (await b.newContext(ctx)).newPage();
  await p.goto(URL);
  await p.waitForFunction(() => document.getElementById("status").dataset.state === "ready");
  for (const ex of ["Lignes invalides", "Plusieurs blocs"]) {
    await p.getByRole("button", { name: ex, exact: true }).click();
    await p.waitForTimeout(300);
    await p.locator("#analyze").click(); await p.waitForTimeout(2500);
    console.log(name, ex, JSON.stringify(await p.evaluate(() => ({
      topbar: Math.round(document.querySelector(".topbar").getBoundingClientRect().bottom),
      results: Math.round(document.getElementById("results").getBoundingClientRect().top),
      title: Math.round(document.getElementById("results-title").getBoundingClientRect().top),
      scrollY: Math.round(scrollY), margin: getComputedStyle(document.getElementById("results")).scrollMarginTop,
      active: document.activeElement?.id }))));
  }
  await b.close();
}
