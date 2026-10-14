// Construction statique pour GitHub Pages (npm run build → dist/).
// base "./" : liens relatifs, le site fonctionne sous /TeamAI/ comme en local.
// Chaque page HTML présente à la racine de volet_a/web devient une entrée (index.html dès SCRUM-23).
import { readdirSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig } from "vite";

const root = import.meta.dirname;
const pages = Object.fromEntries(
    readdirSync(root)
        .filter((name) => name.endsWith(".html"))
        .map((name) => [name.replace(/\.html$/, ""), resolve(root, name)])
);

export default defineConfig({
    base: "./",
    build: { rollupOptions: { input: pages } },
});
