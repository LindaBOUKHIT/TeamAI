import { loadDetector } from "./model.js";
import { compileVocab, preprocess } from "./preprocess.js";
import {
    selectRows,
    renderRows,
    downloadCsv,
} from "./ui/results.js";

const BASE = import.meta.env.BASE_URL;
const MAX_BYTES = 10 * 1024 * 1024;

const elements = Object.fromEntries(
    [
        "status", "warning", "logs", "file", "example", "load-example",
        "source", "analyze", "message", "summary", "anomalies-only",
        "export", "result-count", "rows",
    ].map((id) => [id, document.getElementById(id)])
);

let detector;
let compiled;
let rows = [];
let busy = false;
let incompleteExample = false;

function showMessage(text, error = false) {
    elements.message.textContent = text;
    elements.message.dataset.error = String(error);
}

function updateControls() {
    const unavailable = !detector || busy;
    elements.logs.disabled = unavailable;
    elements.file.disabled = unavailable;
    elements.example.disabled = unavailable;
    elements["load-example"].disabled = unavailable;
    elements.analyze.disabled = unavailable;
    elements["anomalies-only"].disabled =
        unavailable || rows.length === 0 || detector.isToy;

    const displayed = selectRows(
        rows, elements["anomalies-only"].checked
    );
    elements.export.disabled = unavailable || displayed.length === 0;
}

function refreshTable() {
    const displayed = selectRows(
        rows, elements["anomalies-only"].checked
    );
    renderRows(elements.rows, displayed);
    elements["result-count"].textContent =
        `${displayed.length} bloc(s) affiché(s) sur ${rows.length}.`;
    updateControls();
}

function clearResults() {
    rows = [];
    elements["anomalies-only"].checked = false;
    elements.summary.textContent = "Aucune analyse effectuée.";
    refreshTable();
}

elements.logs.addEventListener("input", () => {
    incompleteExample = false;
    elements.file.value = "";
    elements.source.textContent = "Source : saisie libre.";
    clearResults();
    showMessage("");
});

elements.file.addEventListener("change", async () => {
    const file = elements.file.files[0];
    if (!file) return;

    busy = true;
    clearResults();
    elements.logs.value = "";
    incompleteExample = false;
    updateControls();

    try {
        if (file.size > MAX_BYTES) {
            throw new Error("Fichier trop volumineux : maximum 10 Mo.");
        }
        elements.logs.value = await file.text();
        elements.source.textContent = `Source : fichier ${file.name}.`;
        showMessage("Fichier chargé. Cliquez sur « Analyser les logs ».");
    } catch (error) {
        elements.source.textContent = "Aucun fichier chargé.";
        showMessage(error.message, true);
    } finally {
        busy = false;
        updateControls();
    }
});

elements["load-example"].addEventListener("click", async () => {
    busy = true;
    clearResults();
    elements.logs.value = "";
    elements.file.value = "";
    incompleteExample = false;
    updateControls();

    try {
        const name = elements.example.value;
        const response = await fetch(`${BASE}examples/${name}`);
        if (!response.ok) {
            throw new Error(`Exemple indisponible : HTTP ${response.status}`);
        }
        elements.logs.value = await response.text();
        incompleteExample = name === "04_bloc_incomplet.log";
        elements.source.textContent =
            `Source : exemple de validation ${name}.`;
        showMessage("Exemple chargé. Cliquez sur « Analyser les logs ».");
    } catch (error) {
        elements.source.textContent = "Aucun exemple chargé.";
        showMessage(error.message, true);
    } finally {
        busy = false;
        updateControls();
    }
});

elements.analyze.addEventListener("click", async () => {
    if (!detector || busy) return;

    busy = true;
    clearResults();
    updateControls();
    showMessage("Analyse en cours…");

    try {
        const text = elements.logs.value;
        if (new Blob([text]).size > MAX_BYTES) {
            throw new Error("Texte trop volumineux : maximum 10 Mo.");
        }

        const { blocks, stats } = preprocess(text, compiled);
        const completed = [];
        const started = performance.now();

        // Inférence par petits lots. Le Worker sera ajouté dans SCRUM-40.
        for (let offset = 0; offset < blocks.length; offset += 64) {
            const batch = blocks.slice(offset, offset + 64);
            const scores = await detector.predict(batch.map((block) => block.ids));

            batch.forEach((block, index) => {
                const score = scores[index];
                completed.push({
                    blockId: block.blockId,
                    length: block.length,
                    truncated: block.truncated,
                    unknown: block.unknown,
                    incompleteExample,
                    score,
                    label: detector.isToy
                        ? null
                        : Number(score >= detector.meta.threshold),
                });
            });

            showMessage(
                `Analyse : ${completed.length} / ${blocks.length} blocs.`
            );
            await new Promise((resolve) => setTimeout(resolve, 0));
        }

        rows = completed;
        const elapsed = performance.now() - started;
        const ignored = stats.invalid_header + stats.without_block;
        const truncated = rows.reduce((sum, row) => sum + row.truncated, 0);
        const unknown = rows.reduce((sum, row) => sum + row.unknown, 0);
        const anomalies = rows.filter((row) => row.label === 1).length;

        elements.summary.textContent = [
            `${rows.length} bloc(s) analysé(s).`,
            detector.isToy
                ? "Modèle factice : aucune classification interprétable."
                : `${anomalies} anomalie(s) selon le seuil ${detector.meta.threshold}.`,
            `${stats.lines} ligne(s) non vide(s) ; ${ignored} ignorée(s)`,
            `(${stats.invalid_header} en-tête(s) invalide(s),`,
            `${stats.without_block} sans identifiant de bloc).`,
            `${stats.empty} ligne(s) vide(s).`,
            `${stats.unknown} ligne(s) avec événement inconnu.`,
            `${truncated} événement(s) tronqué(s),`,
            `${unknown} événement(s) inconnu(s) encodé(s) au total par bloc.`,
            `Traitement : ${elapsed.toFixed(1)} ms, hors prétraitement.`,
        ].join(" ");

        showMessage("Analyse terminée.");
    } catch (error) {
        clearResults();
        showMessage(error.message, true);
        console.error(error);
    } finally {
        busy = false;
        refreshTable();
    }
});

elements["anomalies-only"].addEventListener("change", refreshTable);

elements.export.addEventListener("click", () => {
    const displayed = selectRows(
        rows, elements["anomalies-only"].checked
    );
    if (displayed.length && detector) {
        downloadCsv(displayed, detector.meta);
    }
});

async function start() {
    updateControls();

    try {
        detector = await loadDetector();
        compiled = compileVocab(detector.vocab);

        elements.status.textContent =
            `Modèle ${detector.meta.version} — seuil ${detector.meta.threshold}` +
            ` — source : ${detector.source}.`;

        if (detector.isToy) {
            elements.warning.hidden = false;
            elements.warning.textContent =
                "MODÈLE FACTICE : les scores ne permettent pas de détecter " +
                "des anomalies réelles.";
        }

        showMessage("Prêt. Collez des logs, importez un fichier ou essayez un exemple.");
    } catch (error) {
        detector = null;
        elements.status.textContent = "Échec du chargement du modèle.";
        showMessage(error.message, true);
        console.error(error);
    } finally {
        updateControls();
    }
}

start();