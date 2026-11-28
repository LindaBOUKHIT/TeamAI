// Recette multi-navigateurs du site en production (SCRUM-50).
import { chromium, firefox, webkit, devices } from "playwright";
import fs from "node:fs";

const URL = process.env.SITE ?? "https://lindaboukhit.github.io/TeamAI/";
const OUT = process.env.OUT ?? "out";
fs.mkdirSync(OUT, { recursive: true });

const EXAMPLES = ["Bloc normal", "Bloc avec anomalie", "Plusieurs blocs", "Bloc incomplet", "Lignes invalides"];

const configs = [
    { id: "chromium-desktop", type: chromium, ctx: { viewport: { width: 1366, height: 900 } } },
    { id: "edge-desktop", type: chromium, launch: { channel: "msedge" }, ctx: { viewport: { width: 1366, height: 900 } } },
    { id: "firefox-desktop", type: firefox, ctx: { viewport: { width: 1366, height: 900 } } },
    { id: "webkit-desktop", type: webkit, ctx: { viewport: { width: 1366, height: 900 } } },
    { id: "webkit-iphone", type: webkit, ctx: { ...devices["iPhone 13"] } },
    { id: "chromium-pixel", type: chromium, ctx: { ...devices["Pixel 7"] } },
    { id: "webkit-ipad", type: webkit, ctx: { ...devices["iPad (gen 7)"] } },
    { id: "firefox-mobile-375", type: firefox, ctx: { viewport: { width: 375, height: 812 } } },
    // Connexion lente : profil « Fast 3G » de Chrome DevTools, cache vide.
    { id: "chromium-3g", type: chromium, ctx: { viewport: { width: 1366, height: 900 } }, throttle: { latency: 562.5, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8 } },
];

const only = process.argv.slice(2);
const results = [];

for (const c of configs) {
    if (only.length && !only.includes(c.id)) continue;
    const r = { id: c.id, errors: [], failed: [] };
    let browser;
    try {
        browser = await c.type.launch(c.launch ?? {});
        r.version = `${c.type.name()} ${browser.version()}`;
        const context = await browser.newContext(c.ctx);
        const page = await context.newPage();
        page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") r.errors.push(`${m.type()}: ${m.text()}`); });
        page.on("pageerror", (e) => r.errors.push(`pageerror: ${e.message}`));
        page.on("requestfailed", (q) => r.failed.push(`${q.url()} ${q.failure()?.errorText}`));
        page.on("response", (s) => { if (s.status() >= 400) r.failed.push(`${s.status()} ${s.url()}`); });
        if (c.throttle) {
            const cdp = await context.newCDPSession(page);
            await cdp.send("Network.enable");
            await cdp.send("Network.emulateNetworkConditions", { offline: false, ...c.throttle });
        }
        const t0 = Date.now();
        await page.goto(URL, { waitUntil: "load", timeout: 180000 });
        r.load_ms = Date.now() - t0;
        await page.waitForFunction(() => ["ready", "error"].includes(document.getElementById("status")?.dataset.state), null, { timeout: 180000 });
        r.ready_ms = Date.now() - t0;
        r.status = await page.locator("#status-text").textContent();
        r.model_info = await page.locator("#model-info").textContent();
        r.ua = await page.evaluate(() => navigator.userAgent);
        r.examples = [];
        for (const name of EXAMPLES) {
            await page.getByRole("button", { name, exact: true }).click();
            await page.waitForFunction(() => document.getElementById("source").textContent.includes("exemple"));
            await page.locator("#analyze").click();
            await page.waitForFunction(() => /Analyse terminée|Erreur|échou/i.test(document.getElementById("message").textContent), null, { timeout: 30000 });
            const k = await page.evaluate(() => ({
                msg: document.getElementById("message").textContent.replace(/\s+/g, " ").trim(),
                blocs: document.getElementById("kpi-blocks").textContent,
                anomalies: document.getElementById("kpi-anomalies").textContent,
                lignes: document.getElementById("kpi-lines").textContent,
                ignorees: document.getElementById("kpi-ignored").textContent,
                inference: document.getElementById("kpi-time").textContent,
            }));
            r.examples.push({ name, ...k });
            await page.evaluate(() => document.getElementById("source").textContent = "");
        }
        r.layout = await page.evaluate(() => ({
            viewport: innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            overflow: [...document.querySelectorAll("body *")].filter((e) => { const b = e.getBoundingClientRect(); return b.width > 0 && b.right > innerWidth + 1; }).length,
        }));
        // Défilement fait par l'application après l'analyse (scroll-margin de la barre supérieure).
        await page.waitForTimeout(2000);
        await page.screenshot({ path: `${OUT}/${c.id}.png` });
        await context.close();
    } catch (e) {
        r.fatal = String(e.message ?? e).split("\n")[0];
    } finally {
        await browser?.close();
    }
    results.push(r);
    console.log(JSON.stringify(r));
}
fs.writeFileSync(`${OUT}/recette.json`, JSON.stringify(results, null, 2));
