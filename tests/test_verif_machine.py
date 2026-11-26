"""SCRUM-61 : relevé machine et comparaison base / échelle 0 / échelle 1, sans modèle réel."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from volet_b.slm import verif_machine


def fake_run(texts):
    """Remplace subprocess.run : les lancements enfants écrivent un résultat fictif, nvidia-smi est absent."""
    def run(cmd, **kwargs):
        """Lancement enfant simulé."""
        if cmd[0] == "nvidia-smi":
            raise OSError("absent")
        out = Path(cmd[cmd.index("--out") + 1])
        name = out.stem
        out.write_text(json.dumps({"chargement_s": 1.0, "generation_s": 2.0, "tokens": 10, "tokens_par_s": 5.0,
                                   "vram_avant_mib": None, "vram_apres_mib": None, "vram_modele_mib": None,
                                   "texte": texts[name]}), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return run


class VerifMachineTest(unittest.TestCase):
    """Contrôles du script de relevé SCRUM-61."""

    def test_summary_requires_three_runs(self):
        """Le résumé n'est complet qu'avec les trois lancements."""
        self.assertEqual(verif_machine.summarize({"base": {"texte": "a"}}), {"complet": False})
        s = verif_machine.summarize({"base": {"texte": "a"}, "echelle_0": {"texte": "a"}, "echelle_1": {"texte": "b"}})
        self.assertEqual(s, {"complet": True, "base_egale_echelle_0": True, "echelle_0_differe_echelle_1": True})

    def test_seed_prompt_is_train(self):
        """Le prompt vient d'un bloc train."""
        example_id, prompt = verif_machine.seed_prompt()
        self.assertEqual(example_id, "seed-0001")
        self.assertTrue(prompt)

    def test_wrong_sha256_stops_before_any_run(self):
        """Une empreinte fausse arrête tout avant le moindre lancement."""
        with tempfile.TemporaryDirectory() as tmp:
            adapter = Path(tmp) / "adapter.gguf"
            adapter.write_bytes(b"x")
            with mock.patch.object(verif_machine.subprocess, "run") as run, self.assertRaises(SystemExit):
                verif_machine.main(["--adapter", str(adapter), "--sha256", "0" * 64])
            run.assert_not_called()

    def test_full_run_writes_report(self):
        """Un relevé complet écrit resultats.json et resultats.md."""
        with tempfile.TemporaryDirectory() as tmp:
            adapter = Path(tmp) / "adapter.gguf"
            adapter.write_bytes(b"x")
            texts = {"base": "a", "echelle_0": "a", "echelle_1": "b"}
            with mock.patch.object(verif_machine, "OUT", Path(tmp) / "machine"), \
                    mock.patch.object(verif_machine.subprocess, "run", side_effect=fake_run(texts)):
                verif_machine.main(["--adapter", str(adapter), "--sha256", verif_machine.sha256(adapter)])
            folder = next((Path(tmp) / "machine").iterdir())
            report = json.loads((folder / "resultats.json").read_text(encoding="utf-8"))
            self.assertTrue(report["resume"]["base_egale_echelle_0"])
            self.assertTrue(report["resume"]["echelle_0_differe_echelle_1"])
            self.assertEqual(report["environnement"]["gpu"], [])
            self.assertIn("| echelle_1 | 1.0 | 2.0 | 10 | 5.0 |", (folder / "resultats.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
