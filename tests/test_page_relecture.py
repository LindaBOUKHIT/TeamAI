"""Pré-contrôle de la page de relecture SCRUM-35, sur des exemples synthétiques (aucune donnée de test)."""
import csv
import json
import shutil
import subprocess

import pytest

from eval.volet_b.page_relecture import apply_corrections, parse, precheck
from teamai.paths import EVAL_VOLET_B


def record(faits, resume="Le bloc est reçu.", hypotheses=(), infos=(), abstention=False):
    """Construit un enregistrement C5 synthétique de quatre lignes."""
    return {"events": ["E5", "E9", "E9", "E4"],
            "trace_lines": ["INFO Receiving blk_1", "INFO Received blk_1 of size 67108864",
                            "INFO Received blk_1 of size 67108864", "WARN Got exception while serving blk_1 to /10.0.0.1:"],
            "expected": {"resume_evenements": resume, "faits_observes": list(faits), "hypotheses": list(hypotheses),
                         "infos_manquantes": list(infos), "sources": [], "abstention": abstention}}


def test_coherent_case_has_no_alert():
    """Un corrigé cohérent avec sa trace ne déclenche aucune alerte."""
    checks = precheck(record(["E9 : deux réceptions de 67108864 octets.", "E4 : un avertissement d'exception vers 10.0.0.1."]))
    assert checks["alerts"] == []
    assert any("E9 = 2" in ok for ok in checks["ok"])


def test_wrong_count_missing_code_and_unknown_number_are_flagged():
    """Effectif faux, code absent et nombre inconnu sont signalés."""
    alerts = precheck(record(["E9 : trois réceptions.", "E26 : enregistrement.", "E5 : réception de 999999 octets."]))["alerts"]
    assert any("annonce 3" in a for a in alerts)
    assert any("E26" in a for a in alerts)
    assert any("999999" in a for a in alerts)


def test_contract_and_warn_rules():
    """Les règles C5 d'abstention, le conditionnel et les WARN non mentionnés sont contrôlés."""
    alerts = precheck(record(["E5 : réception."], resume="Le bloc est reçu.", hypotheses=["Le disque est plein."],
                             abstention=True))["alerts"]
    assert any("Abstention vraie mais hypothèses" in a for a in alerts)
    assert any("sans information manquante" in a for a in alerts)
    assert any("conditionnel" in a for a in alerts)
    assert any("WARN/ERROR" in a for a in alerts)


def test_absence_facts_are_checked_as_absences():
    """Un fait d'absence n'exige pas de code ; il est contredit si le code ou l'erreur figure dans la trace."""
    checks = precheck(record(["E5 : réception.", "Aucun événement E26 n'apparaît dans la trace.",
                              "E9 : le bloc absent du cache est reçu deux fois."]))
    assert not any("Fait 2" in a or "Fait 3" in a for a in checks["alerts"])
    assert any("Fait 2 : absence cohérente" in o for o in checks["ok"])
    alerts = precheck(record(["Aucun événement E9 n'apparaît.", "Aucun message d'erreur n'apparaît dans la trace."]))["alerts"]
    assert any("absence de E9, pourtant présent" in a for a in alerts)
    assert any("absence d'erreur" in a for a in alerts)

def test_parse_reads_sections_and_meta():
    """Le découpage du Markdown retrouve identifiants, métadonnées et sections."""
    md = "# Titre\n\n## test-0001 — blk_1\n\n**Label officiel :** 0\n\n### Trace originale\n\n```text\n[E5] ligne\n```\n\n### Faits observés\n\n- E5 : réception.\n\n---\n"
    (case,) = parse(md)
    assert case["id"] == "test-0001" and case["block_id"] == "blk_1"
    assert case["meta"]["Label officiel"] == "0"
    assert case["sections"]["Faits observés"] == "- E5 : réception."


def write_jsonl(path, rows):
    """Écrit des lignes JSON au format du fichier d'annotations."""
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8", newline="\n")


def annotations(tmp_path):
    """Crée un fichier d'annotations synthétique de deux cas."""
    rows = [dict(record(["E5 : réception."]), id=f"test-000{i}", block_id=f"blk_{i}", label=0) for i in (1, 2)]
    path = tmp_path / "annotations_travail.jsonl"
    write_jsonl(path, rows)
    return path, rows


def correction(case_id, block_id, **changes):
    """Construit une ligne de corrections au format exporté par la page."""
    expected = dict(record(["E9 : deux réceptions."])["expected"], **changes)
    return {"id": case_id, "block_id": block_id, "corrige_par": "Alain", "date": "2026-11-13",
            "motif": "effectif corrigé", "expected": expected}


def test_apply_corrections_replaces_expected_and_logs(tmp_path):
    """Une correction valide remplace le corrigé, garde le reste et alimente le journal."""
    path, rows = annotations(tmp_path)
    corr = tmp_path / "corrections_Alain.jsonl"
    write_jsonl(corr, [correction("test-0002", "blk_2")])
    log = tmp_path / "corrections_journal.csv"
    assert apply_corrections([corr], path, log) == 1
    new = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
    assert new[0] == rows[0]
    assert new[1]["expected"]["faits_observes"] == ["E9 : deux réceptions."]
    assert {k: v for k, v in new[1].items() if k != "expected"} == {k: v for k, v in rows[1].items() if k != "expected"}
    assert b"\r\n" not in path.read_bytes()
    with log.open(encoding="utf-8", newline="") as f:
        assert [r["id"] for r in csv.DictReader(f)] == ["test-0002"]


@pytest.mark.parametrize("bad, message", [
    ({"block_id": "blk_9"}, "inconnu"),
    ({"expected": {"resume_evenements": "x"}}, "champs attendus"),
    ({"abstention": True}, "C5"),
    ({"corrige_par": ""}, "auteur"),
])
def test_apply_corrections_rejects_invalid_lines(tmp_path, bad, message):
    """Bloc inconnu, champs manquants, règle C5 ou auteur absent bloquent l'application sans rien écrire."""
    path, _ = annotations(tmp_path)
    before = path.read_bytes()
    line = correction("test-0001", "blk_1")
    if "abstention" in bad:
        line["expected"]["abstention"] = True
    else:
        line.update(bad)
    corr = tmp_path / "c.jsonl"
    write_jsonl(corr, [line])
    with pytest.raises(ValueError, match=message):
        apply_corrections([corr], path, tmp_path / "journal.csv")
    assert path.read_bytes() == before
    assert not (tmp_path / "journal.csv").exists()


def test_apply_corrections_refuses_two_files_on_same_case(tmp_path):
    """Deux fichiers qui corrigent le même cas sont refusés : le conflit se tranche en équipe."""
    path, _ = annotations(tmp_path)
    a, b = tmp_path / "corrections_Alain.jsonl", tmp_path / "corrections_Linda.jsonl"
    write_jsonl(a, [correction("test-0001", "blk_1")])
    write_jsonl(b, [dict(correction("test-0001", "blk_1"), corrige_par="Linda")])
    with pytest.raises(ValueError, match="déjà corrigé"):
        apply_corrections([a, b], path, tmp_path / "journal.csv")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js absent")
def test_javascript_precheck_matches_python(tmp_path):
    """Le pré-contrôle recalculé dans la page donne les mêmes alertes que la version Python."""
    template = (EVAL_VOLET_B / "page_relecture.html").read_text(encoding="utf-8")
    js = template[template.index("// precheck:start"):template.index("// precheck:end")]
    recs = [record(["E9 : deux réceptions de 67108864 octets.", "E4 : un avertissement d'exception vers 10.0.0.1."]),
            record(["E9 : trois réceptions.", "E26 : enregistrement.", "E5 : réception de 999999 octets.", "réception sans code"]),
            record(["E9 : plusieurs réceptions.", "E5 : plusieurs réceptions."], hypotheses=["Le disque est plein."], abstention=True),
            record(["éE9 : code collé à une lettre accentuée."], resume="Bloc reçu par 10.0.0.1:50010."),
            record(["Aucun événement E26 n'apparaît.", "Pas d'avertissement.", "E9 : bloc absent du cache, deux fois.",
                    "Aucun événement E9 n'apparaît.", "Aucune erreur n'apparaît."])]
    script = tmp_path / "check.js"
    script.write_text(js + "\nconst recs = JSON.parse(require('fs').readFileSync(0, 'utf8'));\n"
                      "process.stdout.write(JSON.stringify(recs.map(r => precheck(r, r.expected))));\n", encoding="utf-8")
    out = subprocess.run(["node", str(script)], input=json.dumps(recs), capture_output=True, text=True,
                         encoding="utf-8", check=True).stdout
    assert json.loads(out) == [precheck(r) for r in recs]
