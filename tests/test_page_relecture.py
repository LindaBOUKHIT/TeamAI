"""Pré-contrôle de la page de relecture SCRUM-35, sur des exemples synthétiques (aucune donnée de test)."""
from eval.volet_b.page_relecture import parse, precheck


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


def test_parse_reads_sections_and_meta():
    """Le découpage du Markdown retrouve identifiants, métadonnées et sections."""
    md = "# Titre\n\n## test-0001 — blk_1\n\n**Label officiel :** 0\n\n### Trace originale\n\n```text\n[E5] ligne\n```\n\n### Faits observés\n\n- E5 : réception.\n\n---\n"
    (case,) = parse(md)
    assert case["id"] == "test-0001" and case["block_id"] == "blk_1"
    assert case["meta"]["Label officiel"] == "0"
    assert case["sections"]["Faits observés"] == "- E5 : réception."
