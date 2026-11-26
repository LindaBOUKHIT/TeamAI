"""SCRUM-45 : fiches de double annotation à l'aveugle des 4 configurations, sur les cas de double_annotation.csv.

    python -m eval.volet_b.blind_sheets eval/runs/<run 1> eval/runs/<run 2> eval/runs/<run 3> eval/runs/<run 4>

Écrit dans eval/volet_b/double_annotation/ une fiche identique par annotateur et la clé cle_aveugle.json,
à garder fermée jusqu'à la fin des deux grilles. Le dépouillement se fait avec eval.volet_b.blind_scores.
"""
import argparse
import csv
import json
import random
from pathlib import Path

from data.parse_hdfs import compile_templates
from eval.volet_b import run_config
from eval.volet_b.run_eval import CONFIGS, inputs_hash, load_cases, prepare_case
from teamai.paths import VOLET_B_BLIND, VOLET_B_DOUBLE_ANNOTATION, VOLET_B_TEST_INPUTS, resolve_path
from volet_b.slm.v16.runtime import INSTRUCTION, build_prompt

LABELS = ('A', 'B', 'C', 'D')
CRITERIA = ('F', 'S', 'A', 'U')
SEED = 'SCRUM-45'
COLUMNS = ('id', 'etiquette', 'trace', 'preuves', 'reponse', *CRITERIA, 'commentaire')
SHEETS = ('aveugle_annotateur_1.csv', 'aveugle_annotateur_2.csv')
KEY = 'cle_aveugle.json'
EMPTY = dict(faits_observes='aucun', hypotheses='aucune', infos_manquantes='aucune', sources='aucune')
TITLES = dict(faits_observes='Faits observés', hypotheses='Hypothèses', infos_manquantes='Informations manquantes',
              sources='Sources documentaires')


def selected_ids(path: Path = VOLET_B_DOUBLE_ANNOTATION) -> list[str]:
    """Identifiants choisis pour la double annotation, dans l'ordre du fichier."""
    with path.open(encoding='utf-8', newline='') as source:
        ids = [row['id'] for row in csv.DictReader(source)]
    if not ids or len(set(ids)) != len(ids) or not all(ids):
        raise ValueError(f'{path} : identifiants non vides et distincts attendus.')
    return ids


def draw_order(case_id: str) -> dict:
    """Associe A, B, C, D aux configurations, avec une graine fixe propre au cas."""
    return dict(zip(LABELS, random.Random(f'{SEED}:{case_id}').sample(list(CONFIGS), len(CONFIGS))))


def load_run(path: Path, reference: str) -> tuple[str, dict]:
    """Lit un run réel sur les entrées figées et indexe ses prédictions par cas."""
    path = resolve_path(path)
    config = json.loads((path / 'config.json').read_text(encoding='utf-8'))
    if config.get('config') not in CONFIGS:
        raise ValueError(f'{path} : configuration inconnue {config.get("config")}.')
    if config.get('mock') is not False:
        raise ValueError(f'{config["config"]} : run factice (--mock) refusé.')
    if config.get('input_sha256') != reference:
        raise ValueError(f'{config["config"]} : empreinte des entrées différente de test_inputs.sha256, refusé.')
    records = {}
    for line in (path / 'predictions.jsonl').read_text(encoding='utf-8').splitlines():
        if line.strip():
            record = json.loads(line)
            if record['id'] in records:
                raise ValueError(f'{config["config"]} : cas {record["id"]} en double.')
            records[record['id']] = record
    return config['config'], records


def render_trace(lines: list[str]) -> str:
    """Trace brute numérotée comme les références (ligne N) des preuves, à partir de 1."""
    return '\n'.join(f'{number}: {line}' for number, line in enumerate(lines, 1))


def render_answer(record: dict) -> str:
    """Réponse finale lisible, sans statut, erreur ni mesure qui trahirait la configuration."""
    final = record['final']
    if not final['text'] or not final['text'].strip():
        return 'Aucune réponse produite.'
    answer = final['answer']
    if not isinstance(answer, dict):
        return 'Réponse non analysable (texte brut) :\n' + final['text']
    passages = {p['id']: p['text'] for p in record['passages']}
    parts = ['Résumé : ' + str(answer.get('resume_evenements'))]
    for key, title in TITLES.items():
        values = answer.get(key)
        if not isinstance(values, list):
            parts.append(f'{title} : {values!r}')
        elif not values:
            parts.append(f'{title} : {EMPTY[key]}')
        elif key == 'sources':
            parts.append(f'{title} :' + ''.join(f'\n- [{v}] {passages.get(v, "passage non fourni au modèle")}'
                                                 for v in values))
        else:
            parts.append(f'{title} :' + ''.join(f'\n- {v}' for v in values))
    abstention = answer.get('abstention')
    parts.append('Abstention : ' + ('oui' if abstention is True else 'non' if abstention is False else repr(abstention)))
    return '\n\n'.join(parts)


def build(run_paths, output_dir: Path = VOLET_B_BLIND, selection: Path = VOLET_B_DOUBLE_ANNOTATION,
          inputs: Path = VOLET_B_TEST_INPUTS) -> list[Path]:
    """Écrit les deux fiches et la clé ; refuse d'écraser une fiche ou une clé existante."""
    reference, official = inputs_hash(inputs)
    if not official:
        raise ValueError('Les fiches se construisent sur les entrées figées test_inputs.jsonl.')
    loaded = [(resolve_path(path), *load_run(path, reference)) for path in run_paths]
    runs = {config: records for _, config, records in loaded}
    if sorted(runs) != sorted(CONFIGS) or len(loaded) != len(CONFIGS):
        raise ValueError(f'Un run par configuration attendu : {", ".join(CONFIGS)}.')
    cases = {case['id']: case for case in load_cases(inputs)[0]}
    targets = [output_dir / name for name in (*SHEETS, KEY)]
    existing = [str(path) for path in targets if path.exists()]
    if existing:
        raise FileExistsError(f'Fichiers déjà présents, non écrasés : {", ".join(existing)}')
    templates = compile_templates(run_config.TEMPLATES)
    rows, key = [], {}
    for index, case_id in enumerate(selected_ids(selection)):
        missing = [config for config, records in runs.items() if case_id not in records]
        if case_id not in cases or missing:
            raise ValueError(f'{case_id} absent des entrées ou des runs {", ".join(missing)}.')
        block, problem = prepare_case(cases[case_id], index, templates)
        if block is None:
            raise ValueError(f'{case_id} : {problem}')
        evidence = build_prompt(block).removeprefix(INSTRUCTION).strip()
        key[case_id] = draw_order(case_id)
        for label, config in key[case_id].items():
            rows.append(dict(id=case_id, etiquette=label, trace=render_trace(cases[case_id]['trace_lines']),
                             preuves=evidence, reponse=render_answer(runs[config][case_id]),
                             **{criterion: '' for criterion in CRITERIA}, commentaire=''))
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in SHEETS:
        with (output_dir / name).open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    run_config.write_json(output_dir / KEY, dict(
        seed=f'random.Random("{SEED}:<id>").sample({list(CONFIGS)}, 4), étiquettes {"".join(LABELS)} dans cet ordre',
        input_sha256=reference, runs={config: str(path) for path, config, _ in loaded},
        criteria='F exactitude des faits, S appui sur les sources, A abstention justifiée, U utilité ; 0 à 2',
        cases=key))
    return targets


def main(argv=None) -> None:
    """Ligne de commande : les 4 dossiers de run réels, dans n'importe quel ordre."""
    parser = argparse.ArgumentParser(description='SCRUM-45 : fiches de double annotation à l\'aveugle.')
    parser.add_argument('runs', nargs=4, type=Path)
    parser.add_argument('--output-dir', type=Path, default=VOLET_B_BLIND)
    args = parser.parse_args(argv)
    try:
        written = build(args.runs, resolve_path(args.output_dir))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print('Fichiers : ' + ', '.join(str(path) for path in written))


if __name__ == '__main__':
    main()
