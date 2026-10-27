// SCRUM-26 — Parité du prétraitement JavaScript avec Loghub et avec Python (node --test).
//
// 1. Sur les 2 000 blocs de data/sample/, la séquence JS == colonne Features de Event_traces.csv.
// 2. Les cas limites de tests/parity_cases.json (partagés avec tests/test_preprocess.py) donnent
//    exactement les mêmes séquences et compteurs qu'en Python.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import { compileVocab, encode, parseLines, preprocess, UNKNOWN_EVENT } from "../src/preprocess.js";

const here = new URL(".", import.meta.url);
const readText = (relative) => readFileSync(new URL(relative, here), "utf-8");

const vocab = compileVocab(JSON.parse(readText("../public/vocab.json")));
const cases = JSON.parse(readText("./parity_cases.json")).cases;

/** Colonne Features de Event_traces.csv : BlockId → liste d'EventId. */
function loadFeatures(csvText) {
    const features = new Map();
    for (const line of csvText.split(/\r?\n/).slice(1)) {
        const match = /^(blk_-?\d+),[^,]*,[^,]*,"\[([^\]]*)\]"/.exec(line);
        if (match) features.set(match[1], match[2].split(","));
    }
    return features;
}

test("vocab.json : 29 événements C2, ids 1 à 29, pad 0, unk 30, longueur 50", () => {
    assert.equal(vocab.patterns.length, 29);
    assert.deepEqual(vocab.patterns.map(([eventId]) => eventId), Array.from({ length: 29 }, (_, i) => `E${i + 1}`));
    assert.equal(vocab.pad_id, 0);
    assert.equal(vocab.unk_id, 30);
    assert.equal(vocab.max_len, 50);
});

test("échantillon : séquences JS identiques à Event_traces.csv sur tous les blocs", () => {
    const expected = loadFeatures(readText("../../../data/sample/Event_traces.csv"));
    const { sequences, stats } = parseLines(readText("../../../data/sample/HDFS_sample.log"), vocab);
    assert.equal(expected.size, 2000);
    assert.equal(stats.unknown, 0);
    assert.equal(sequences.size, expected.size);
    for (const [blockId, events] of expected) {
        assert.deepEqual(sequences.get(blockId), events, blockId);
    }
});

for (const parityCase of cases) {
    test(`parité Python : ${parityCase.name}`, () => {
        const { sequences, stats } = parseLines(parityCase.lines, vocab);
        assert.deepEqual(Object.fromEntries(sequences), parityCase.expected_sequences);
        assert.deepEqual(stats, parityCase.expected_stats);
    });
}

test("encode : padding à droite jusqu'à 50, ordre conservé, inconnu → 30", () => {
    const out = encode(["E5", "E22", UNKNOWN_EVENT, "E5"], vocab);
    assert.equal(out.ids.length, 50);
    assert.deepEqual(out.ids.slice(0, 5), [5, 22, 30, 5, 0]);
    assert.equal(out.unknown, 1);
    assert.equal(out.truncated, 0);
});

test("encode : une séquence longue garde ses 50 premiers événements et signale la troncature", () => {
    const events = Array.from({ length: 60 }, (_, i) => (i < 50 ? "E5" : "E21"));
    const out = encode(events, vocab);
    assert.deepEqual(out.ids, Array(50).fill(5));
    assert.equal(out.length, 60);
    assert.equal(out.truncated, 10);
});

test("preprocess : une entrée sans bloc reconnu est rejetée avec un message, jamais classée", () => {
    assert.throws(() => preprocess("", vocab), /Aucun bloc HDFS reconnu/);
    assert.throws(() => preprocess("pas un log\nencore rien", vocab), /2 ligne\(s\) lue\(s\)/);
});

test("preprocess : les exemples du site sont tous découpés en blocs", () => {
    for (const name of ["01_normal", "02_anomalie", "03_plusieurs_blocs", "04_bloc_incomplet", "05_lignes_invalides"]) {
        const { blocks } = preprocess(readText(`../public/examples/${name}.log`), vocab);
        assert.ok(blocks.length > 0, name);
        for (const block of blocks) assert.equal(block.ids.length, 50, `${name} ${block.blockId}`);
    }
});
