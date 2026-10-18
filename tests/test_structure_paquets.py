"""SCRUM-60 : le code Python forme des paquets et ses chemins viennent de teamai.paths."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".venv", "venv", ".git", "node_modules", "raw", "runs", "__pycache__", "tests"}
FORBIDDEN = re.compile(r"sys\.path|Path\(__file__\)|Path\(\"(data|eval|volet_a|volet_b)/")


def code_files() -> list[Path]:
    """Fichiers .py du code du dépôt (tests, environnements et données exclus)."""
    return sorted(p for p in ROOT.rglob("*.py")
                  if not EXCLUDED & set(p.relative_to(ROOT).parts) and p.parent != ROOT)


class PackageStructureTests(unittest.TestCase):
    """Garde-fou : plus de chemins recréés à la main ni de bricolage de sys.path."""

    def test_every_code_folder_is_a_package(self):
        """Chaque dossier contenant du code a un __init__.py, jusqu'à la racine."""
        missing = set()
        for path in code_files():
            for folder in path.relative_to(ROOT).parents:
                if folder != Path(".") and not (ROOT / folder / "__init__.py").exists():
                    missing.add(folder.as_posix())
        self.assertEqual(sorted(missing), [], "Ajouter un __init__.py (docstring seule) dans ces dossiers.")

    def test_paths_come_from_teamai_paths(self):
        """Seul teamai/paths.py calcule des chemins à partir de son propre emplacement."""
        offenders = []
        for path in code_files():
            if path == ROOT / "teamai" / "paths.py":
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if FORBIDDEN.search(line):
                    offenders.append(f"{path.relative_to(ROOT).as_posix()}:{number} {line.strip()}")
        self.assertEqual(offenders, [], "Importer le chemin depuis teamai.paths (ou l'y ajouter).")


if __name__ == "__main__":
    unittest.main()
