import { loadDetector } from "./worker-client.js";
import { compileVocab, preprocess } from "./preprocess.js";
import {
    selectRows,
    searchRows,
    sortRows,
    renderRows,
    downloadCsv,
} from "./ui/results.js";
import { formatDecimal, formatInteger, plural } from "./ui/format.js";

const BASE = import.meta.env.BASE_URL;
const MAX_BYTES = 10 * 1024 * 1024;
const BATCH = 64;
const INCOMPLETE_EXAMPLE = "04_bloc_incomplet.log";

const $ = (id) => document.getElementById(id);
const elements = Object.fromEntries(
    [
        "status", "status-text", "warning", "logs", "file", "dropzone", "line-count",
        "source", "clear", "analyze", "progress-wrap", "progress", "message",
        "results", "results-title", "empty", "report", "summary",
        "kpi-blocks", "kpi-anomalies", "kpi-anomalies-card", "kpi-lines",
        "kpi-ignored", "kpi-time", "anomalies-only", "search", "sort", "export",
        "result-count", "rows", "no-match", "model-info", "theme",
    ].map((id) => [id, $(id)])
);
const chips = [...document.querySelectorAll("[data-example]")];
const steps = Object.fromEntries(
    [...document.querySelectorAll(".stepper [data-step]")]
        .map((item) => [item.dataset.step, item])
);


let detector;
let compiled;
let rows = [];
let busy = false;
let incompleteExample = false;

// --- États de l'interface ------------------------------------------------

function showMessage(text, { error = false, tone = "" } = {}) {
    elements.message.textContent = text;
    elements.message.dataset.error = String(error);
    elements.message.dataset.tone = tone;
}

function setStatus(state, text) {
    elements.status.dataset.state = state;
    elements["status-text"].textContent = text;
}

function setStep(current) {
    const order = ["input", "analyze", "results"];
    const index = order.indexOf(current);
    order.forEach((name, position) => {
        const item = steps[name];
        if (!item) return;
        if (position < index) item.dataset.state = "done";
        else if (position === index) item.dataset.state = "current";
        else delete item.dataset.state;
        if (position === index) item.setAttribute("aria-current", "step");
        else item.removeAttribute("aria-current");
    });
}

function setProgress(done, total) {
    elements["progress-wrap"].hidden = total === 0;
    elements.progress.max = Math.max(total, 1);
    elements.progress.value = done;
}

function displayedRows() {
    const filtered = searchRows(
        selectRows(rows, elements["anomalies-only"].checked),
        elements.search.value
    );
    return sortRows(filtered, elements.sort.value);
}

function updateControls() {
    const unavailable = !detector || busy;
    const hasText = elements.logs.value.trim().length > 0;
    const hasRows = rows.length > 0;

    elements.logs.disabled = !detector;
    elements.logs.readOnly = busy;
    elements.file.disabled = unavailable;
    for (const chip of chips) chip.disabled = unavailable;
    elements.clear.disabled = unavailable || (!hasText && !hasRows);
    elements.analyze.disabled = unavailable || !hasText;
    elements.analyze.setAttribute("aria-busy", String(busy && Boolean(detector)));

    elements["anomalies-only"].disabled =
        unavailable || !hasRows || Boolean(detector?.isToy);
    elements.search.disabled = unavailable || !hasRows;
    elements.sort.disabled = unavailable || !hasRows;
    elements.export.disabled = unavailable || displayedRows().length === 0;
}

function refreshTable() {
    const displayed = displayedRows();
    renderRows(
        elements.rows, displayed, rows,
        detector && !detector.isToy ? detector.meta.threshold : null
    );
    elements["result-count"].textContent =
        `${plural(displayed.length, "bloc affiché", "blocs affichés")} sur ${formatInteger(rows.length)}.`;
    elements["no-match"].hidden = !(rows.length > 0 && displayed.length === 0);
    updateControls();
}

function clearResults() {
    rows = [];
    elements["anomalies-only"].checked = false;
    elements.search.value = "";
    elements.summary.textContent = "";
    elements.report.hidden = true;
    elements.empty.hidden = false;
    refreshTable();
}

// --- Saisie ----------------------------------------------------------------

let countTimer;
function updateLineCount() {
    clearTimeout(countTimer);
    countTimer = setTimeout(() => {
        const text = elements.logs.value;
        const lines = text ? text.split(/\r?\n/).filter((line) => line.trim()).length : 0;
        const blocks = new Set(text.match(/blk_-?\d+/g) ?? []).size;
        elements["line-count"].textContent =
            `${plural(lines, "ligne")} · ${plural(blocks, "bloc repéré", "blocs repérés")}`;
    }, 120);
}

function setSource(text, example = null) {
    elements.source.textContent = text;
    for (const chip of chips) {
        chip.setAttribute("aria-pressed", String(chip.dataset.example === example));
    }
}

function resetInput() {
    clearResults();
    incompleteExample = false;
    setProgress(0, 0);
    setStep("input");
}

elements.logs.addEventListener("input", () => {
    resetInput();
    elements.file.value = "";
    setSource("Source : saisie libre.");
    showMessage("");
    if (elements.logs.value.trim()) setStep("analyze");
    updateLineCount();
    updateControls();
});

elements.logs.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        if (!elements.analyze.disabled) elements.analyze.click();
    }
});

async function loadFile(file) {
    if (!file || busy || !detector) return;

    busy = true;
    resetInput();
    elements.logs.value = "";
    updateControls();

    try {
        if (file.size > MAX_BYTES) {
            throw new Error("Fichier trop volumineux : maximum 10 Mo.");
        }
        elements.logs.value = await file.text();
        setSource(`Source : fichier ${file.name}.`);
        showMessage("Fichier chargé. Lancez l'analyse.");
        setStep("analyze");
    } catch (error) {
        setSource("Aucun fichier chargé.");
        showMessage(error.message, { error: true });
    } finally {
        busy = false;
        updateLineCount();
        updateControls();
    }
}

elements.file.addEventListener("change", () => loadFile(elements.file.files[0]));

for (const type of ["dragenter", "dragover"]) {
    elements.dropzone.addEventListener(type, (event) => {
        event.preventDefault();
        if (!elements.file.disabled) elements.dropzone.dataset.over = "true";
    });
}
for (const type of ["dragleave", "drop"]) {
    elements.dropzone.addEventListener(type, () => {
        delete elements.dropzone.dataset.over;
    });
}
elements.dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    if (elements.file.disabled) return;
    const file = event.dataTransfer?.files?.[0];
    elements.file.value = "";
    loadFile(file);
});
// Un fichier lâché à côté de la zone ne doit pas remplacer la page.
window.addEventListener("dragover", (event) => event.preventDefault());
window.addEventListener("drop", (event) => event.preventDefault());

for (const chip of chips) {
    chip.addEventListener("click", async () => {
        if (busy || !detector) return;
        const name = chip.dataset.example;

        busy = true;
        resetInput();
        elements.logs.value = "";
        elements.file.value = "";
        updateControls();

        try {
            const response = await fetch(`${BASE}examples/${name}`);
            if (!response.ok) {
                throw new Error(`Exemple indisponible : HTTP ${response.status}`);
            }
            elements.logs.value = await response.text();
            incompleteExample = name === INCOMPLETE_EXAMPLE;
            setSource(`Source : exemple de validation ${name}.`, name);
            showMessage(`Exemple « ${chip.textContent.trim()} » chargé. Lancez l'analyse.`);
            setStep("analyze");
        } catch (error) {
            setSource("Aucun exemple chargé.");
            showMessage(error.message, { error: true });
        } finally {
            busy = false;
            updateLineCount();
            updateControls();
        }
    });
}

elements.clear.addEventListener("click", () => {
    elements.logs.value = "";
    elements.file.value = "";
    resetInput();
    setSource("Source : saisie libre.");
    showMessage("");
    updateLineCount();
    updateControls();
    elements.logs.focus();
});

// --- Analyse ---------------------------------------------------------------

function renderReport(stats, elapsed) {
    const ignored = stats.invalid_header + stats.without_block;
    const truncated = rows.reduce((sum, row) => sum + row.truncated, 0);
    const unknown = rows.reduce((sum, row) => sum + row.unknown, 0);
    const anomalies = rows.filter((row) => row.label === 1).length;

    elements["kpi-blocks"].textContent = formatInteger(rows.length);
    elements["kpi-anomalies"].textContent = detector.isToy ? "—" : formatInteger(anomalies);
    elements["kpi-anomalies-card"].dataset.tone =
        detector.isToy ? "" : anomalies > 0 ? "danger" : "ok";
    elements["kpi-lines"].textContent = formatInteger(stats.lines);
    elements["kpi-ignored"].textContent = formatInteger(ignored);
    elements["kpi-time"].textContent = `${formatDecimal(elapsed)} ms`;

    elements.summary.textContent = [
        `${plural(rows.length, "bloc analysé", "blocs analysés")}.`,
        detector.isToy
            ? "Modèle factice : aucune classification interprétable."
            : `${plural(anomalies, "anomalie")} selon le seuil ${formatDecimal(detector.meta.threshold)}.`,
        `${plural(stats.lines, "ligne non vide", "lignes non vides")}, dont ${plural(ignored, "ignorée", "ignorées")}`,
        `(${plural(stats.invalid_header, "en-tête invalide", "en-têtes invalides")},`,
        `${plural(stats.without_block, "sans identifiant", "sans identifiant")} de bloc).`,
        `${plural(stats.empty, "ligne vide", "lignes vides")}.`,
        `${plural(stats.unknown, "ligne", "lignes")} avec un événement inconnu.`,
        `Au total : ${plural(truncated, "événement tronqué", "événements tronqués")},`,
        `${plural(unknown, "événement inconnu encodé", "événements inconnus encodés")}.`,
        `Inférence : ${formatDecimal(elapsed)} ms, hors prétraitement.`,
    ].join(" ");

    // Anomalies en tête par défaut : ce sont elles que l'on vient chercher.
    elements.sort.value = "score-desc";
    elements.empty.hidden = true;
    elements.report.hidden = false;

    return { anomalies, ignored };
}

elements.analyze.addEventListener("click", async () => {
    if (!detector || busy) return;

    busy = true;
    clearResults();
    setStep("analyze");
    setStatus("busy", "Analyse en cours…");
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
        setProgress(0, blocks.length);

        // Inférence par lots dans le Web Worker (SCRUM-40).
        for (let offset = 0; offset < blocks.length; offset += BATCH) {
            const batch = blocks.slice(offset, offset + BATCH);
            const scores = await detector.predict(batch.map((block) => block.ids));

            batch.forEach((block, index) => {
                const score = scores[index];
                completed.push({
                    blockId: block.blockId,
                    length: block.length,
                    truncated: block.truncated,
                    unknown: block.unknown,
                    incompleteExample,
                    events: block.events.slice(0, compiled.max_len),
                    score,
                    label: detector.isToy
                        ? null
                        : Number(score >= detector.meta.threshold),
                });
            });

            setProgress(completed.length, blocks.length);
            showMessage(`Analyse : ${formatInteger(completed.length)} / ${plural(blocks.length, "bloc")}.`);
            await new Promise((resolve) => setTimeout(resolve, 0));
        }

        rows = completed;
        const { anomalies, ignored } = renderReport(stats, performance.now() - started);

        const verdict = detector.isToy
            ? "Analyse terminée (modèle factice)."
            : anomalies > 0
                ? `Analyse terminée : ${plural(anomalies, "bloc suspect", "blocs suspects")} sur ${formatInteger(rows.length)}.`
                : `Analyse terminée : aucun bloc suspect sur ${formatInteger(rows.length)}.`;
        showMessage(
            ignored ? `${verdict} ${plural(ignored, "ligne ignorée", "lignes ignorées")}.` : verdict,
            { tone: "ok" }
        );
        setStep("results");
        // Masquer la progression avant le défilement : sinon la page remonte
        // ensuite et le titre des résultats passe sous la barre supérieure (mobile).
        setProgress(0, 0);
        elements.results.scrollIntoView({
            behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
            block: "start",
        });
        elements["results-title"].focus({ preventScroll: true });
    } catch (error) {
        clearResults();
        setStep("input");
        showMessage(error.message, { error: true });
        console.error(error);
    } finally {
        busy = false;
        setProgress(0, 0);
        if (detector) setStatus("ready", "Modèle prêt");
        refreshTable();
    }
});

// --- Résultats -------------------------------------------------------------

elements["anomalies-only"].addEventListener("change", refreshTable);
elements.sort.addEventListener("change", refreshTable);
elements.search.addEventListener("input", refreshTable);

elements.export.addEventListener("click", () => {
    const displayed = displayedRows();
    if (displayed.length && detector) {
        downloadCsv(displayed, detector.meta);
    }
});

// --- Thème -----------------------------------------------------------------

elements.theme.addEventListener("click", () => {
    const root = document.documentElement;
    const current = root.dataset.theme
        ?? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try {
        localStorage.setItem("teamai-theme", next);
    } catch { /* stockage indisponible : le choix vaut pour la session */ }
});

// --- Démarrage -------------------------------------------------------------

async function start() {
    updateControls();

    try {
        detector = await loadDetector();
        compiled = compileVocab(detector.vocab);

        const { meta } = detector;
        setStatus(detector.isToy ? "error" : "ready",
            detector.isToy ? "Modèle factice" : "Modèle prêt");
        elements.status.title =
            `Modèle ${meta.version} — seuil ${meta.threshold} — source : ${detector.source}.`;
        elements["model-info"].textContent =
            `Modèle ${meta.model ?? ""} ${meta.version} · seuil ${formatDecimal(meta.threshold)}` +
            ` · source : ${detector.source}` +
            (meta.model_sha256 ? ` · SHA-256 ${meta.model_sha256.slice(0, 12)}…` : "");

        if (detector.isToy) {
            elements.warning.hidden = false;
            elements.warning.textContent =
                "MODÈLE FACTICE : les scores ne permettent pas de détecter " +
                "des anomalies réelles.";
        }

        showMessage("Prêt. Collez des logs, importez un fichier ou essayez un exemple.");
    } catch (error) {
        detector = null;
        setStatus("error", "Échec du chargement");
        elements["model-info"].textContent = "Le modèle n'a pas pu être chargé.";
        showMessage(error.message, { error: true });
        console.error(error);
    } finally {
        updateControls();
    }
}

start();
