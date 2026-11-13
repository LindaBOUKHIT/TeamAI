/**
 * SCRUM-27 : présentation des résultats et export CSV.
 * Les valeurs provenant des logs sont insérées comme texte.
 */

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

export function renderRows(tbody, rows) {
    const fragment = document.createDocumentFragment();

    for (const row of rows) {
        const tr = document.createElement("tr");
        if (row.label === 1) tr.className = "anomaly";

        const values = [
            row.blockId,
            row.label === null
                ? "Modèle factice"
                : row.label === 1 ? "Anomalie" : "Normal",
            row.score.toFixed(8),
            row.length,
            row.truncated,
            row.unknown,
            getWarnings(row),
        ];

        for (const value of values) {
            const td = document.createElement("td");
            td.textContent = String(value);
            tr.appendChild(td);
        }

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