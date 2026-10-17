import * as ort from "onnxruntime-web";

ort.env.wasm.numThreads = 1;

const BASE = import.meta.env.BASE_URL;
const CACHE_NAME = "teamai-models-v1";

async function readJson(path) {
    const response = await fetch(`${BASE}${path}`, { cache: "no-cache" });
    if (!response.ok) {
        throw new Error(`${path} : HTTP ${response.status}`);
    }
    return response.json();
}

async function sha256(bytes) {
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest))
        .map((value) => value.toString(16).padStart(2, "0"))
        .join("");
}

async function loadModelBytes(meta) {
    const url = new URL(`${BASE}model/detector.onnx`, location.origin);

    // Un modèle entraîné est identifié par son hash.
    // Le spike est revalidé sur le réseau pour éviter un modèle périmé.
    if (meta.model_sha256) {
        url.searchParams.set("sha256", meta.model_sha256);
    }

    let cache = null;
    try {
        if ("caches" in window) {
            cache = await caches.open(CACHE_NAME);
        }
    } catch (error) {
        console.warn("Cache indisponible :", error);
    }

    let response = meta.model_sha256
        ? await cache?.match(url.href)
        : null;
    let source = response ? "cache navigateur" : "réseau";

    if (!response) {
        response = await fetch(url.href, { cache: "no-cache" });
        if (!response.ok) {
            throw new Error(`Modèle : HTTP ${response.status}`);
        }
    }

    const bytes = await response.arrayBuffer();

    if (meta.model_sha256) {
        const actual = await sha256(bytes);
        if (actual !== meta.model_sha256.toLowerCase()) {
            await cache?.delete(url.href);
            throw new Error("Le hash du modèle ne correspond pas aux métadonnées.");
        }
    }

    // Une erreur de stockage ne bloque pas une inférence valide.
    try {
        await cache?.put(url.href, new Response(bytes));
    } catch (error) {
        console.warn("Modèle chargé, mais non mis en cache :", error);
    }

    return { bytes, source };
}

export async function loadDetector() {
    const [meta, vocabResponse] = await Promise.all([
        readJson("model/detector.meta.json"),
        fetch(`${BASE}vocab.json`, { cache: "no-cache" }),
    ]);

    if (!vocabResponse.ok) {
        throw new Error(`Vocabulaire : HTTP ${vocabResponse.status}`);
    }

    const vocabBytes = await vocabResponse.arrayBuffer();
    const vocab = JSON.parse(new TextDecoder().decode(vocabBytes));

    if (
        vocab.max_len !== 50 ||
        vocab.pad_id !== 0 ||
        vocab.unk_id !== 30
    ) {
        throw new Error("Vocabulaire incompatible avec le contrat C2.");
    }

    for (const field of ["max_len", "pad_id", "unk_id"]) {
        if (meta[field] !== undefined && meta[field] !== vocab[field]) {
            throw new Error(`Modèle et vocabulaire incompatibles : ${field}.`);
        }
    }

    if (meta.vocab_sha256) {
        const actual = await sha256(vocabBytes);
        if (actual !== meta.vocab_sha256.toLowerCase()) {
            throw new Error("Le vocabulaire ne correspond pas au modèle.");
        }
    }

    if (
        !Number.isFinite(meta.threshold) ||
        meta.threshold < 0 ||
        meta.threshold > 1
    ) {
        throw new Error("Seuil du modèle invalide.");
    }

    const { bytes, source } = await loadModelBytes(meta);
    const session = await ort.InferenceSession.create(bytes, {
        executionProviders: ["wasm"],
    });

    if (
        session.inputNames.length !== 1 ||
        session.inputNames[0] !== "event_ids" ||
        session.outputNames.length !== 1 ||
        session.outputNames[0] !== "p_anomaly"
    ) {
        await session.release();
        throw new Error("Noms des entrées/sorties incompatibles avec C3.");
    }

    return {
        meta,
        vocab,
        source,
        isToy:
            meta.trained_on === "none-random-weights" ||
            meta.version === "spike",

        async predict(rows) {
            if (
                !Array.isArray(rows) ||
                rows.length === 0 ||
                rows.some(
                    (row) =>
                        !Array.isArray(row) ||
                        row.length !== 50 ||
                        row.some(
                            (id) => !Number.isInteger(id) || id < 0 || id > 30
                        )
                )
            ) {
                throw new Error("Entrée attendue : séquences de 50 indices entre 0 et 30.");
            }

            const input = new ort.Tensor(
                "int64",
                BigInt64Array.from(rows.flat(), (id) => BigInt(id)),
                [rows.length, 50]
            );

            const outputs = await session.run({ event_ids: input });
            const output = outputs.p_anomaly;

            if (
                !output ||
                output.type !== "float32" ||
                output.dims.length !== 1 ||
                output.dims[0] !== rows.length
            ) {
                throw new Error("Type ou dimensions de sortie incompatibles avec C3.");
            }

            const scores = Array.from(output.data);

            if (scores.some((p) => !Number.isFinite(p) || p < 0 || p > 1)) {
                throw new Error("Le modèle a retourné un score invalide.");
            }

            return scores;
        },
    };
}