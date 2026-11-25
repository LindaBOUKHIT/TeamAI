"""SCRUM-36 : contrôles v16 des réponses d'un lot et extraction compacte pour la rédaction.

`--export` écrit, pour chaque exemple, la partie variable du prompt (faits,
chronologie, messages, causes autorisées), sans la consigne commune.
`--answers` fusionne un fichier {id, expected} dans le lot puis applique les
contrôles du runtime v16 : schéma fermé, contrat, faits, références, ancrage
des hypothèses, boucles, mots de chronologie et doublons de résumé.
"""
import argparse
import collections
import json
import re

from data.parse_hdfs import compile_templates
from teamai.paths import SAMPLE
from volet_b.slm.lora_data import schema_errors
from volet_b.slm.make_lots import DRAFTS
from volet_b.slm.v16.explain import repetition_errors
from volet_b.slm.v16.facts import prepare_block
from volet_b.slm.v16.runtime import INSTRUCTION, build_prompt, validate

TEMPOREL = re.compile(r"\b(puis|après|avant|à la suite|ensuite|finalement|se termine|provoqu\w*|génèr\w*|en raison de|entraîn\w*|à cause)\b", re.I)


def load(lot):
    """Lit les exemples d'un lot."""
    path = DRAFTS / f"lot_{lot}.jsonl"
    return path, [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def rebuild(example, templates):
    """Reconstruit le bloc v16 depuis les lignes du sample et vérifie le prompt."""
    numbered = []
    wanted = set(example["trace_lines"])
    with (SAMPLE / "HDFS_sample.log").open(encoding="utf-8") as stream:
        for number, raw in enumerate(stream, 1):
            raw = raw.rstrip("\r\n")
            if example["block_id"] in raw and raw in wanted:
                numbered.append((number, raw))
    block = prepare_block(example["block_id"], numbered, templates, split=example["split"])
    if build_prompt(block) != example["prompt"]:
        raise ValueError(f"{example['id']} : prompt différent de v16")
    return block


def check(example, block):
    """Liste les erreurs bloquantes et les alertes de relecture d'une réponse."""
    answer = example.get("expected")
    if not isinstance(answer, dict):
        return ["réponse absente"], []
    text = json.dumps(answer, ensure_ascii=False)
    contract, factual, review = validate(text, block)
    errors = list(schema_errors(answer, block)) + contract + factual
    prose = " ".join([answer.get("resume_evenements", "")] + answer.get("hypotheses", []) + answer.get("infos_manquantes", []))
    errors += repetition_errors(text, len(text) // 4)
    words = sorted({w.lower() for w in TEMPOREL.findall(prose)})
    if words:
        errors.append("mots de chronologie ou de causalité : " + ", ".join(words))
    return sorted(set(errors)), review


def main(argv=None):
    """Exporte les preuves d'un lot ou contrôle ses réponses ; code de sortie 1 si erreur."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lot", required=True)
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--answers", help="JSONL {id, expected} à fusionner avant contrôle")
    args = parser.parse_args(argv)
    path, examples = load(args.lot)
    if args.export:
        out = DRAFTS / f"preuves_{args.lot}.txt"
        parts = [f"### {ex['id']} ({ex['split']}, strate {ex['strate']})\n" + ex["prompt"].replace(INSTRUCTION, "").strip()
                 for ex in examples]
        out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        print(out)
        return
    if args.answers:
        answers = {}
        with open(args.answers, encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    row = json.loads(line)
                    answers[row["id"]] = row["expected"]
        for ex in examples:
            if ex["id"] in answers:
                ex["expected"] = answers[ex["id"]]
        path.write_text("".join(json.dumps(ex, ensure_ascii=False) + "\n" for ex in examples), encoding="utf-8")
    templates = compile_templates(SAMPLE / "HDFS.log_templates.csv")
    failed, flags = 0, collections.Counter()
    summaries = collections.Counter(json.dumps((ex.get("expected") or {}).get("resume_evenements")) for ex in examples)
    for ex in examples:
        errors, review = check(ex, rebuild(ex, templates))
        if summaries[json.dumps((ex.get("expected") or {}).get("resume_evenements"))] > 1 and ex.get("expected"):
            errors.append("résumé identique à un autre exemple")
        flags.update(review)
        if errors:
            failed += 1
            print(f"{ex['id']} : " + " | ".join(errors))
    with_hyp = sum(bool((ex.get("expected") or {}).get("hypotheses")) for ex in examples)
    print(json.dumps({"lot": args.lot, "n": len(examples), "en_erreur": failed, "avec_hypothese": with_hyp,
                      "alertes_relecture": dict(flags)}, ensure_ascii=False))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
