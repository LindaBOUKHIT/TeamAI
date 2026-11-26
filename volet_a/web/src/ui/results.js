/**
 * SCRUM-27 : présentation des résultats et export CSV.
 * Les valeurs provenant des logs sont insérées comme texte.
 */

import { formatDecimal, plural } from "./format.js";

export function selectRows(rows, anomaliesOnly) {
    return anomaliesOnly
        ? rows.filter((row) => row.label === 1)
        : rows;
}

export function getWarnings(row) {
    const warnings = [];

    if (row.incompleteExample) {
        warnings.push("Exemple volontairement incomplet");
    } else {
        warnings.push("Complétude non vérifiée");
    }

    if (row.truncated > 0) {
        warnings.push(`${row.truncated} événement(s) tronqué(s)`);
    }

    if (row.unknown > 0) {
        warnings.push(`${row.unknown} événement(s) inconnu(s) encodé(s)`);
    }

    return warnings.join(" ; ");
}

export function searchRows(rows, query) {
    const needle = String(query ?? "").trim().toLowerCase();
    return needle
        ? rows.filter((row) => row.blockId.toLowerCase().includes(needle))
        : rows;
}

export function sortRows(rows, mode) {
    const sorted = [...rows];
    if (mode === "score-desc") {
        sorted.sort((a, b) => b.score - a.score);
    } else if (mode === "id") {
        sorted.sort((a, b) => a.blockId.localeCompare(b.blockId, "en"));
    }
    return sorted;
}

const COLUMNS = [
    "Bloc", "Classe", "Score", "Événements reçus",
    "Tronqués", "Inconnus encodés", "Avertissements",
];

function cell(label, className) {
    const td = document.createElement("td");
    td.dataset.label = label;
    if (className) td.className = className;
    return td;
}

function textNode(tag, className, text) {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = text;
    return element;
}

function displayWarnings(row) {
    const warnings = [row.incompleteExample
        ? ["Exemple volontairement incomplet", true]
        : ["Complétude non vérifiée", false]];
    if (row.truncated > 0) {
        warnings.push([plural(row.truncated, "événement tronqué", "événements tronqués"), true]);
    }
    if (row.unknown > 0) {
        warnings.push([plural(row.unknown, "événement inconnu encodé", "événements inconnus encodés"), true]);
    }
    return warnings;
}

export function renderRows(tbody, rows, population = rows, threshold = null) {
    const fragment = document.createDocumentFragment();

    const counts = new Map();
    for (const row of population) {
        for (const event of row.events ?? []) {
            counts.set(event, (counts.get(event) ?? 0) + 1);
        }
    }

    for (const row of rows) {
        const tr = document.createElement("tr");
        if (row.label === 1) tr.className = "anomaly";

        // Bloc et séquence dépliable.
        const block = cell(COLUMNS[0], "cell-block");
        block.appendChild(textNode("span", "block-id", row.blockId));
        if (row.events?.length) {
            const details = document.createElement("details");
            details.className = "sequence";
            const summary = document.createElement("summary");
            summary.textContent = `Voir la séquence (${row.events.length})`;
            details.appendChild(summary);
            const sequence = document.createElement("ol");
            sequence.className = "event-sequence";
            for (const event of row.events) {
                const item = document.createElement("li");
                const rare = counts.get(event) === 1 && event !== "UNK";
                item.textContent = rare ? `${event} (rare)` : event;
                if (rare) item.className = "rare";
                sequence.appendChild(item);
            }
            details.appendChild(sequence);
            block.appendChild(details);
        }

        // Classe.
        const verdict = cell(COLUMNS[1]);
        const [text, tone] = row.label === null
            ? ["Modèle factice", "badge-toy"]
            : row.label === 1 ? ["Anomalie", "badge-anomaly"] : ["Normal", "badge-normal"];
        verdict.appendChild(textNode("span", `badge ${tone}`, text));

        // Score et position par rapport au seuil.
        const score = cell(COLUMNS[2]);
        const wrap = document.createElement("div");
        wrap.className = "score";
        const value = textNode("span", "score-value", formatDecimal(row.score));
        // Deux décimales à l'écran ; la valeur complète au survol et dans le CSV.
        value.title = `Score exact : ${row.score.toFixed(8)}`;
        wrap.appendChild(value);
        const bar = document.createElement("span");
        bar.className = "score-bar";
        bar.setAttribute("aria-hidden", "true");
        bar.style.setProperty("--score", String(row.score));
        if (threshold !== null) {
            bar.style.setProperty("--threshold", String(threshold));
        } else {
            bar.classList.add("no-threshold");
        }
        bar.appendChild(document.createElement("span"));
        wrap.appendChild(bar);
        score.appendChild(wrap);

        tr.append(block, verdict, score);

        for (const [index, number] of [[3, row.length], [4, row.truncated], [5, row.unknown]]) {
            const td = cell(COLUMNS[index], "num");
            td.textContent = String(number);
            tr.appendChild(td);
        }

        // Avertissements accordés à l'écran ; getWarnings garde le format du CSV.
        const warnings = cell(COLUMNS[6]);
        const list = document.createElement("div");
        list.className = "warnings";
        for (const [warning, strong] of displayWarnings(row)) {
            list.appendChild(textNode("span", strong ? "tag tag-warn" : "tag", warning));
        }
        warnings.appendChild(list);
        tr.appendChild(warnings);

        fragment.appendChild(tr);
    }

    tbody.replaceChildren(fragment);
}

function csvCell(value) {
    let text = String(value ?? "");

    // Évite qu'une cellule textuelle soit interprétée comme une formule.
    if (/^\s*[=+\-@]/.test(text)) {
        text = `'${text}`;
    }

    return `"${text.replaceAll('"', '""')}"`;
}

export function makeCsv(rows, metadata) {
    const header = [
        "BlockId",
        "label",
        "p_anomaly",
        "length",
        "truncated",
        "unknown",
        "warnings",
        "threshold",
        "model_sha256",
    ];

    const records = rows.map((row) => [
        row.blockId,
        row.label,
        row.score,
        row.length,
        row.truncated,
        row.unknown,
        getWarnings(row),
        metadata.threshold,
        metadata.model_sha256 ?? "",
    ]);

    return [header, ...records]
        .map((record) => record.map(csvCell).join(","))
        .join("\r\n") + "\r\n";
}

export function downloadCsv(rows, metadata) {
    const content = "\uFEFF" + makeCsv(rows, metadata);
    const blob = new Blob([content], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "teamai-resultats-hdfs.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
}