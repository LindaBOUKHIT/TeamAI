import { loadDetector } from "./model.js";

let detector;

self.addEventListener("message", async ({ data: { id, type, rows } }) => {
    try {
        detector ??= loadDetector();
        const loaded = await detector;
        const { meta, vocab, source, isToy } = loaded;

        const result = type === "load"
            ? { meta, vocab, source, isToy }
            : await loaded.predict(rows);

        self.postMessage({ id, result });
    } catch (error) {
        self.postMessage({ id, error: error.message });
    }
});