"""SCRUM-59 : chaque module, classe et fonction Python du dépôt a une docstring."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".venv", "venv", ".git", "node_modules", "raw", "runs", "__pycache__"}


def python_files() -> list[Path]:
    """Fichiers .py du dépôt, hors environnements virtuels, données brutes et sorties d'expériences."""
    return sorted(p for p in ROOT.rglob("*.py") if not EXCLUDED & set(p.relative_to(ROOT).parts))


def missing_docstrings(path: Path) -> list[str]:
    """Éléments sans docstring dans un fichier, au format « chemin:ligne nom »."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT).as_posix()
    missing = [] if ast.get_docstring(tree) else [f"{rel}:1 module"]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not ast.get_docstring(node):
            missing.append(f"{rel}:{node.lineno} {node.name}")
    return missing


class DocstringTests(unittest.TestCase):
    """Garde-fou : la CI échoue dès qu'une fonction est ajoutée sans docstring."""

    def test_every_definition_has_a_docstring(self):
        """Liste tous les manques d'un coup pour qu'ils soient corrigés en une fois."""
        missing = [item for path in python_files() for item in missing_docstrings(path)]
        self.assertEqual(missing, [], "Docstrings manquantes :\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
