"""SCRUM-21 : génère les fichiers d'exemple du site (volet_a/web/public/examples/) à partir des logs bruts HDFS."""

import re
from pathlib import Path

from teamai.data.splits import load_split
from teamai.paths import RAW_HDFS, ROOT


OUTPUT = ROOT / "volet_a" / "web" / "public" / "examples"
LOG_FILE = RAW_HDFS / "HDFS.log"

BLOCK_PATTERN = re.compile(r"blk_-?\d+")


def main():
    """Choisit deux blocs normaux et un anormal, extrait leurs lignes brutes et écrit cinq fichiers d'exemple.

    Fichiers : bloc normal, bloc anormal, plusieurs blocs mélangés, bloc tronqué, lignes invalides.
    """
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # Exemples de démonstration tirés de la validation : le test officiel reste réservé
    # à l'évaluation finale (CONTRIBUTING §6, contrat C4).
    val = load_split("val")

    # Sélection déterministe de blocs de validation
    normal = val[val["label"] == 0].sort_values("BlockId")
    anomaly = val[val["label"] == 1].sort_values("BlockId")

    if normal.empty or anomaly.empty:
        raise RuntimeError("Blocs normaux ou anormaux absents.")

    normal_id = normal.iloc[0]["BlockId"]
    anomaly_id = anomaly.iloc[0]["BlockId"]
    second_normal_id = normal.iloc[1]["BlockId"]

    selected = {
        normal_id: [],
        anomaly_id: [],
        second_normal_id: [],
    }

    print("Extraction des lignes HDFS...")
    print("Lecture du fichier brut : environ 1,58 Go.")

    # Lecture en streaming : pas de chargement complet en mémoire
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            block_ids = set(BLOCK_PATTERN.findall(line))

            for block_id in block_ids:
                if block_id in selected:
                    selected[block_id].append(line)

    for block_id, lines in selected.items():
        if not lines:
            raise RuntimeError(
                f"Aucune ligne trouvée pour {block_id}"
            )

    def save(filename, lines):
        """Écrit `lines` dans OUTPUT/filename et affiche le nombre de lignes."""
        path = OUTPUT / filename
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"{filename}: {len(lines)} lignes")

    # 1. Bloc normal
    save("01_normal.log", selected[normal_id])

    # 2. Bloc anormal
    save("02_anomalie.log", selected[anomaly_id])

    # 3. Plusieurs blocs mélangés
    multi = (
        selected[normal_id]
        + selected[anomaly_id]
        + selected[second_normal_id]
    )
    save("03_plusieurs_blocs.log", multi)

    # 4. Bloc incomplet : extrait volontairement tronqué
    normal_lines = selected[normal_id]
    if len(normal_lines) < 2:
        raise RuntimeError("Bloc normal trop court pour le tronquer.")

    save(
        "04_bloc_incomplet.log",
        normal_lines[:max(1, len(normal_lines) // 2)],
    )

    # 5. Lignes invalides
    invalid_lines = [
        "Ceci n'est pas une ligne HDFS valide\n",
        "ERROR unknown event without block identifier\n",
        "081109 203518 143 INFO unknown.Component: "
        "UNKNOWN_TEMPLATE blk_999999999999\n",
    ]
    save("05_lignes_invalides.log", invalid_lines)

    print("\nBlocs sélectionnés :")
    print("Normal :", normal_id)
    print("Anomalie :", anomaly_id)
    print("Deuxième normal :", second_normal_id)

    print("\nSCRUM-21 : exemples générés.")


if __name__ == "__main__":
    main()
