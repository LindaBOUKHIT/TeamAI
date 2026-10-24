import test from "node:test";
import assert from "node:assert/strict";
import {
    selectRows,
    getWarnings,
    makeCsv,
} from "../src/ui/results.js";

const normal = {
    blockId: "blk_1",
    label: 0,
    score: 0.1,
    length: 12,
    truncated: 0,
    unknown: 0,
    incompleteExample: false,
};

const anomaly = {
    ...normal,
    blockId: "blk_2",
    label: 1,
    score: 0.995,
};

const metadata = {
    threshold: 0.99,
    model_sha256: "hash-modele",
};

test("filtre : conserve uniquement les anomalies sans modifier les résultats", () => {
    const rows = [normal, anomaly, { ...normal, label: null }];

    assert.deepEqual(selectRows(rows, true), [anomaly]);
    assert.equal(selectRows(rows, false).length, 3);
    assert.equal(rows.length, 3);
    assert.deepEqual(selectRows([normal], true), []);
});

test("CSV filtré : en-tête et anomalie avec score, seuil et hash", () => {
    const csv = makeCsv(selectRows([normal, anomaly], true), metadata);
    const lines = csv.trimEnd().split("\r\n");

    assert.equal(lines.length, 2);
    assert.ok(lines[0].includes('"BlockId","label","p_anomaly"'));
    assert.ok(lines[1].startsWith('"blk_2","1","0.995"'));
    assert.ok(lines[1].endsWith('"0.99","hash-modele"'));
    assert.ok(!csv.includes('"blk_1"'));
});

test("CSV : échappe les guillemets et neutralise les formules", () => {
    const csv = makeCsv(
        [{ ...normal, blockId: '=HYPERLINK("exemple")' }],
        metadata
    );

    assert.ok(csv.includes(`"'=HYPERLINK(""exemple"")"`));
});

test("avertissements : signale bloc incomplet, troncature et inconnus", () => {
    const warning = getWarnings({
        ...normal,
        incompleteExample: true,
        truncated: 4,
        unknown: 2,
    });

    assert.ok(warning.includes("Exemple volontairement incomplet"));
    assert.ok(warning.includes("4 événement(s) tronqué(s)"));
    assert.ok(warning.includes("2 événement(s) inconnu(s)"));
    assert.equal(getWarnings(normal), "Complétude non vérifiée");
});

test("CSV : un modèle factice ne reçoit pas de label normal", () => {
    const csv = makeCsv([{ ...normal, label: null }], metadata);
    assert.ok(csv.split("\r\n")[1].startsWith('"blk_1","","0.1"'));
});