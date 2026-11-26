"""SCRUM-45 : dépouillement des deux grilles à l'aveugle, une fois remplies.

    python -m eval.volet_b.blind_scores

Lit les fiches et cle_aveugle.json de eval/volet_b/double_annotation/, calcule par configuration les
moyennes F, S, A, U et l'accord inter-annotateurs par critère (kappa de Cohen pondéré quadratique,
accord exact), puis écrit depouillement.json et desaccords.csv (cas à arbitrer, configuration masquée).
"""
import argparse
import csv
import json
import statistics
from pathlib import Path

from eval.volet_b import run_config
from eval.volet_b.blind_sheets import CRITERIA, KEY, SHEETS
from eval.volet_b.run_eval import CONFIGS
from teamai.paths import VOLET_B_BLIND, resolve_path

SCORES = (0, 1, 2)
RESULT = 'depouillement.json'
DISAGREEMENTS = 'desaccords.csv'


def read_sheet(path: Path) -> dict:
    """Notes d'une fiche par (cas, étiquette) ; toute note absente ou hors de 0, 1, 2 est refusée.

    Lecture en utf-8-sig : une fiche réenregistrée par Excel commence par un BOM, qui renommerait
    sinon la première colonne en « \\ufeffid ».
    """
    grades, problems = {}, []
    with path.open(encoding='utf-8-sig', newline='') as source:
        for row in csv.DictReader(source):
            item = (row['id'], row['etiquette'])
            if item in grades:
                problems.append(f'{item[0]} {item[1]} en double')
            values = {}
            for criterion in CRITERIA:
                value = (row.get(criterion) or '').strip()
                if value not in {str(score) for score in SCORES}:
                    problems.append(f'{item[0]} {item[1]} {criterion} : « {value} »')
                else:
                    values[criterion] = int(value)
            grades[item] = values
    if problems:
        raise ValueError(f'{path.name} : notes manquantes ou invalides : ' + ' ; '.join(problems))
    return grades


def weighted_kappa(first: list[int], second: list[int], categories=SCORES) -> float | None:
    """Kappa de Cohen à poids quadratiques ; None si le désaccord attendu est nul."""
    if len(first) != len(second) or not first:
        raise ValueError('Deux séries de même longueur non vides attendues.')
    n, k = len(first), len(categories)
    weight = {(i, j): (i - j) ** 2 / (k - 1) ** 2 for i in categories for j in categories}
    observed = sum(weight[a, b] for a, b in zip(first, second)) / n
    expected = sum(weight[i, j] * first.count(i) * second.count(j) for i in categories for j in categories) / n ** 2
    return None if expected == 0 else 1 - observed / expected


def exact_agreement(first: list[int], second: list[int]) -> float:
    """Part des notes identiques entre les deux annotateurs."""
    return sum(a == b for a, b in zip(first, second)) / len(first)


def score(directory: Path = VOLET_B_BLIND) -> dict:
    """Calcule moyennes, accord et désaccords, puis écrit les deux fichiers de dépouillement."""
    key = json.loads((directory / KEY).read_text(encoding='utf-8'))['cases']
    items = [(case, label) for case, labels in key.items() for label in labels]
    sheets = [read_sheet(directory / name) for name in SHEETS]
    for name, grades in zip(SHEETS, sheets):
        if set(grades) != set(items):
            raise ValueError(f'{name} : cas ou étiquettes différents de la clé.')
    configurations = {}
    for config in CONFIGS:
        mine = [item for item in items if key[item[0]][item[1]] == config]
        means = {criterion: dict(annotateur_1=statistics.mean(sheets[0][i][criterion] for i in mine),
                                 annotateur_2=statistics.mean(sheets[1][i][criterion] for i in mine),
                                 ensemble=statistics.mean(s[i][criterion] for s in sheets for i in mine))
                 for criterion in CRITERIA}
        total = statistics.mean(sum(s[i][c] for c in CRITERIA) for s in sheets for i in mine)
        configurations[config] = dict(n=len(mine), moyennes=means, total_sur_8=total)
    agreement, disagreements = {}, []
    for criterion in CRITERIA:
        first = [sheets[0][i][criterion] for i in items]
        second = [sheets[1][i][criterion] for i in items]
        agreement[criterion] = dict(n=len(items), kappa_quadratique=weighted_kappa(first, second),
                                    accord_exact=exact_agreement(first, second))
        disagreements += [dict(id=i[0], etiquette=i[1], critere=criterion, annotateur_1=a, annotateur_2=b,
                               ecart=abs(a - b), arbitrage='')
                          for i, a, b in zip(items, first, second) if a != b]
    result = dict(configurations=configurations, accord=agreement, desaccords=len(disagreements),
                  criteres='F exactitude des faits, S appui sur les sources, A abstention justifiée, U utilité',
                  protocole='Notes 0 à 2 ; moyennes sur les cas de chaque configuration ; kappa et accord exact '
                            'sur toutes les réponses notées, par critère ; avant arbitrage.')
    run_config.write_json(directory / RESULT, result)
    with (directory / DISAGREEMENTS).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=('id', 'etiquette', 'critere', 'annotateur_1', 'annotateur_2',
                                                    'ecart', 'arbitrage'), lineterminator='\n')
        writer.writeheader()
        writer.writerows(disagreements)
    return result


def main(argv=None) -> None:
    """Ligne de commande : dépouille le dossier des fiches remplies."""
    parser = argparse.ArgumentParser(description='SCRUM-45 : dépouillement de la double annotation à l\'aveugle.')
    parser.add_argument('--dir', type=Path, default=VOLET_B_BLIND)
    args = parser.parse_args(argv)
    try:
        result = score(resolve_path(args.dir))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for config, values in result['configurations'].items():
        print(f"{config} : total {values['total_sur_8']:.2f} / 8 sur {values['n']} réponses")
    for criterion, values in result['accord'].items():
        print(f"{criterion} : kappa {values['kappa_quadratique']}, accord exact {values['accord_exact']:.2f}")
    print(f"Désaccords à arbitrer : {result['desaccords']}")


if __name__ == '__main__':
    main()
