"""Régressions SCRUM-28 : mode factice, sélection du bloc et conservation des preuves."""
import json
import os
from functools import lru_cache
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from volet_b.slm import generate as slm
from volet_b.slm.first_inference import main, new_run_directory, raw_lines


class InferenceReviewTests(unittest.TestCase):
    def test_default_and_explicit_none_share_one_model(self):
        builds = []
        @lru_cache(maxsize=1)
        def factory(adapter, offline):
            model = object()
            builds.append(model)
            return model
        with patch.object(slm, "_load_model", factory):
            first = slm.load_model()
            second = slm.load_model(None, local_files_only=False)
            self.assertIs(first, second)
            self.assertEqual(len(builds), 1)

    def test_mock_never_loads_weights_and_returns_abstention(self):
        with patch.dict(os.environ, {"TEAMAI_SLM_MOCK": "1"}), \
             patch.object(slm, "load_model", side_effect=AssertionError("Poids chargés")):
            for prompt in ("trace factice", [{"role": "user", "content": "trace factice"}]):
                out = slm.generate(prompt)
                answer = json.loads(out["text"])
                self.assertIs(answer["abstention"], True)
                self.assertEqual(answer["sources"], [])
                self.assertEqual(set(answer), {"resume_evenements", "faits_observes", "hypotheses",
                                               "infos_manquantes", "sources", "abstention"})
                self.assertEqual(out["new_tokens"], 0)
                self.assertEqual(out["seconds"], 0.0)

    def test_real_measurement_refuses_mock_environment_before_loading_data(self):
        with patch.dict(os.environ, {"TEAMAI_SLM_MOCK": "1"}), \
             patch("volet_b.slm.first_inference.pick_block", side_effect=AssertionError("Données lues")):
            with self.assertRaises(SystemExit) as error:
                main([])
            self.assertEqual(error.exception.code, 2)

    def test_extracts_exact_signed_block_and_keeps_order(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "fixture.txt"
            log.write_text("first blk_-12\nother blk_-123\nwrong xblk_-12\nlast (blk_-12)\n", encoding="utf-8")
            self.assertEqual(raw_lines("blk_-12", log), ["first blk_-12", "last (blk_-12)"])

    def test_unknown_block_is_reported_instead_of_generating_on_empty_input(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "fixture.txt"
            log.write_text("first blk_7\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Aucune ligne"):
                raw_lines("blk_8", log)

    def test_invalid_block_identifier_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Identifiant"):
            raw_lines(".*", Path("missing-file"))

    def test_repeated_runs_do_not_overwrite_previous_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = new_run_directory(root)
            (first / "output.txt").write_text("preuve conservée", encoding="utf-8")
            second = new_run_directory(root)
            self.assertNotEqual(first, second)
            self.assertEqual((first / "output.txt").read_text(encoding="utf-8"), "preuve conservée")
            self.assertTrue(second.is_dir())


if __name__ == "__main__":
    unittest.main()
