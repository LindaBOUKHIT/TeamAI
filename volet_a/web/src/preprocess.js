// SCRUM-26 — Logs bruts HDFS → séquences d'EventId → indices C2, dans le navigateur.
//
// Miroir exact de teamai/data/preprocess.py : mêmes regex (celles de public/vocab.json, plus
// HEADER_REGEX et BLOCK_REGEX recopiées à l'identique), même priorité (premier EventId qui
// correspond, dans l'ordre numérique), même traitement des lignes invalides et inconnues.
// Toute modification doit garder tests/parity.test.js et tests/test_preprocess.py au vert.

export const UNKNOWN_EVENT = "UNK";

// En-tête HDFS : date (6 chiffres), heure (6), PID, niveau, composant, puis « : » et le message.
const HEADER_REGEX = /^\d{6}\s+\d{6}\s+\d+\s+\w+\s+[^:]+:\s*(.*)$/;
const BLOCK_REGEX = /blk_-?\d+/g;

/**
 * Prépare le vocabulaire C2 : regex compilées triées par id, et table EventId → id.
 * @param {object} vocab contenu de public/vocab.json
 */
export function compileVocab(vocab) {
    const entries = Object.entries(vocab.events).sort((a, b) => a[1].id - b[1].id);
    return {
        ...vocab,
        patterns: entries.map(([eventId, spec]) => [eventId, new RegExp(spec.regex)]),
        ids: Object.fromEntries(entries.map(([eventId, spec]) => [eventId, spec.id])),
    };
}

/**
 * Lignes brutes → séquences d'EventId par bloc, dans l'ordre d'apparition.
 * Une ligne d'en-tête invalide ou sans bloc est comptée puis ignorée ; une ligne valide qu'aucun
 * template ne reconnaît donne UNKNOWN_EVENT ; une ligne qui cite plusieurs blocs compte pour chacun.
 * @param {string|string[]} input texte complet ou tableau de lignes
 * @param {object} compiled résultat de compileVocab()
 * @returns {{sequences: Map<string, string[]>, stats: object}}
 */
export function parseLines(input, compiled) {
    const lines = Array.isArray(input) ? input : input.split(/\r?\n/);
    const sequences = new Map();
    const stats = { lines: 0, empty: 0, invalid_header: 0, without_block: 0, matched: 0, unknown: 0 };

    for (const rawLine of lines) {
        const line = rawLine.replace(/\r$/, "");
        if (!line.trim()) {
            stats.empty += 1;
            continue;
        }
        stats.lines += 1;
        const header = HEADER_REGEX.exec(line);
        if (!header) {
            stats.invalid_header += 1;
            continue;
        }
        const message = header[1];
        const blockIds = [...new Set(message.match(BLOCK_REGEX) ?? [])];
        if (blockIds.length === 0) {
            stats.without_block += 1;
            continue;
        }
        const found = compiled.patterns.find(([, pattern]) => pattern.test(message));
        const event = found ? found[0] : UNKNOWN_EVENT;
        stats[found ? "matched" : "unknown"] += 1;
        for (const blockId of blockIds) {
            if (!sequences.has(blockId)) sequences.set(blockId, []);
            sequences.get(blockId).push(event);
        }
    }
    return { sequences, stats };
}

/**
 * Séquence d'EventId → indices C2 : 50 premiers événements, complétés à droite par pad_id.
 * Jamais triée ni dédupliquée ; un EventId inconnu devient unk_id.
 * @returns {{ids: number[], length: number, truncated: number, unknown: number}}
 */
export function encode(events, compiled) {
    const kept = events.slice(0, compiled.max_len);
    const ids = kept.map((eventId) => compiled.ids[eventId] ?? compiled.unk_id);
    const unknown = ids.filter((id) => id === compiled.unk_id).length;
    while (ids.length < compiled.max_len) ids.push(compiled.pad_id);
    return { ids, length: events.length, truncated: Math.max(0, events.length - compiled.max_len), unknown };
}

/**
 * Point d'entrée du site : texte collé ou fichier → un enregistrement par bloc, prêt pour le modèle.
 * Lève une erreur explicite si aucun bloc n'est reconnu : une trace vide n'est jamais classée normale.
 * @returns {{blocks: {blockId: string, events: string[], ids: number[], length: number,
 *            truncated: number, unknown: number}[], stats: object}}
 */
export function preprocess(text, compiled) {
    const { sequences, stats } = parseLines(text, compiled);
    if (sequences.size === 0) {
        throw new Error(
            `Aucun bloc HDFS reconnu (${stats.lines} ligne(s) lue(s), ${stats.invalid_header} en-tête(s) invalide(s), ` +
            `${stats.without_block} ligne(s) sans identifiant blk_). Vérifiez le format des logs.`
        );
    }
    const blocks = [...sequences].map(([blockId, events]) => ({ blockId, events, ...encode(events, compiled) }));
    return { blocks, stats };
}
