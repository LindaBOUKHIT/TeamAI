"""Gel du test réservé (SCRUM-35) : exemples fabriqués, aucune donnée du test officiel."""
from eval.volet_b.figer_test import problems


def fabricated(n=80):
    """80 cas C5 complets (40 normaux, 40 anomalies) et leur ligne de validation humaine."""
    rows, validation = [], {}
    for i in range(1, n + 1):
        rid = f"test-{i:04d}"
        rows.append({"id": rid, "block_id": f"blk_{i}", "split": "test", "trace_lines": ["ligne"], "events": ["E5"],
                     "label": int(i > n // 2),
                     "expected": {"resume_evenements": "Résumé.", "faits_observes": ["E5 : fait."], "hypotheses": [],
                                  "infos_manquantes": [], "sources": [], "abstention": False},
                     "annotator": "Linda", "reviewed_by": "Alain"})
        validation[rid] = {"block_id": f"blk_{i}", "annotator": "Linda", "annotation_verifiee": "oui",
                           "reviewed_by": "Alain", "relecture_validee": "oui"}
    return rows, validation


def test_jeu_complet_sans_obstacle():
    """Un jeu complet, vérifié et relu par deux personnes distinctes, peut être figé."""
    assert problems(*fabricated()) == []


def test_relecture_manquante_bloque_le_gel():
    """Un cas sans relecteur empêche l'écriture de test.jsonl."""
    rows, validation = fabricated()
    rows[0]["reviewed_by"] = ""
    validation["test-0001"].update(reviewed_by="", relecture_validee="")
    assert problems(rows, validation) == ["test-0001 : reviewed_by : texte non vide attendu",
                                          "test-0001 : vérification ou relecture non validée"]


def test_relecteur_identique_a_l_annotateur_bloque_le_gel():
    """Un relecteur identique à l'annotateur empêche aussi le gel (C5)."""
    rows, validation = fabricated()
    rows[1]["reviewed_by"] = "Linda"
    validation["test-0002"]["reviewed_by"] = "Linda"
    assert problems(rows, validation) == ["test-0002 : reviewed_by : le relecteur doit être différent de l'annotateur"]


def test_sans_relecture_croisee_marque_sans_inventer_de_nom():
    """Un cas vérifié mais non relu reçoit NON_RELU ; un cas non vérifié reste bloquant."""
    from eval.volet_b.figer_test import NON_RELU, accept_without_review
    rows = [{"id": "a", "reviewed_by": ""}, {"id": "b", "reviewed_by": ""}]
    validation = {"a": {"annotation_verifiee": "oui", "reviewed_by": "", "relecture_validee": ""},
                  "b": {"annotation_verifiee": "", "reviewed_by": "", "relecture_validee": ""}}
    assert accept_without_review(rows, validation) == ["a"]
    assert rows[0]["reviewed_by"] == NON_RELU and rows[1]["reviewed_by"] == ""
