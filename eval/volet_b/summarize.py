"""SCRUM-45 : tableau des 4 configurations dans eval/results/volet_b.md, à partir de runs complets et réels.

    python -m eval.volet_b.summarize eval/runs/<run base_1agent> eval/runs/<run base_3agents> ...
"""
import argparse
import json
import re
from pathlib import Path

from eval.volet_b.run_eval import CONFIGS, expected_inputs_hash
from teamai.paths import VOLET_B_SUMMARY, resolve_path

TITLE = '## Évaluation automatique des 4 configurations'
COLUMNS = ('Configuration', 'n', 'Conformité C5', 'Acceptées', 'Abstentions', 'Hypothèses/bloc avec incident',
           'Références inconnues', 'Réseau sans appui', 'Boucles', 'Appels SLM moyens', 'Latence moyenne (s)',
           'Latence médiane (s)', 'Pic VRAM (Mio)')


def metrics_path(path: Path) -> Path:
    """Accepte un dossier de run C7 ou directement son metrics.json."""
    path = resolve_path(path)
    return path / 'metrics.json' if path.is_dir() else path


def load_runs(paths) -> dict:
    """Lit les 4 runs et refuse un run factice, partiel, hors entrées figées ou en double."""
    reference = expected_inputs_hash()
    runs = {}
    for path in paths:
        values = json.loads(metrics_path(path).read_text(encoding='utf-8'))
        config = values.get('config')
        if config not in CONFIGS:
            raise ValueError(f'{path} : configuration inconnue {config}.')
        if config in runs:
            raise ValueError(f'{config} fourni deux fois.')
        if values.get('mock') is not False:
            raise ValueError(f'{config} : run factice (--mock) refusé.')
        if (values.get('limit') is not None or values.get('ids') is not None or values.get('complete') is not True
                or not values.get('n') or values['n'] != values.get('n_inputs')):
            raise ValueError(f'{config} : run incomplet (--limit ou --ids) refusé.')
        if values.get('official_input') is not True or values.get('input_sha256') != reference:
            raise ValueError(f'{config} : empreinte des entrées différente de test_inputs.sha256, refusé.')
        runs[config] = values
    missing = [config for config in CONFIGS if config not in runs]
    if missing:
        raise ValueError(f'Runs manquants : {", ".join(missing)}.')
    return runs


def decimal(value, digits: int) -> str:
    """Nombre à virgule décimale ; une mesure absente reste « non mesuré »."""
    return 'non mesuré' if value is None else f'{value:.{digits}f}'.replace('.', ',')


def rate(value) -> str:
    """Taux en pourcentage, à une décimale."""
    return 'non mesuré' if value is None else decimal(100 * value, 1) + ' %'


def row(config: str, values: dict) -> str:
    """Ligne du tableau pour une configuration."""
    vram = values['process_peak_vram_bytes']
    fields = [config, str(values['n']), rate(values['conformity_rate']), rate(values['accepted_rate']),
              rate(values['abstention_rate']), decimal(values['hypotheses_per_block_with_incident'], 2),
              rate(values['unknown_references_rate']), rate(values['unsupported_network_rate']),
              rate(values['loop_responses_rate']), decimal(values['slm_calls_mean'], 2),
              decimal(values['latency_mean_seconds'], 2), decimal(values['latency_median_seconds'], 2),
              decimal(None if vram is None else vram / 1024**2, 0)]
    return '| ' + ' | '.join(fields) + ' |'


def section(runs: dict) -> str:
    """Section Markdown complète, dans l'ordre fixe des configurations."""
    digest = next(iter(runs.values()))['input_sha256']
    return (f'{TITLE}\n\nEntrées figées `eval/volet_b/test_inputs.jsonl` (SHA-256 `{digest}`), mêmes traces, '
            'même corpus et mêmes paramètres de génération pour les 4 configurations. Mesures sur la réponse '
            'finale ; tous les cas au dénominateur, échecs compris. Acceptées : statut `accepte` pour 3 agents, '
            'contrat v16 valide pour 1 agent. Incident : indice `attention` calculé par le code, jamais le label.\n\n'
            '| ' + ' | '.join(COLUMNS) + ' |\n|---|' + '---:|' * (len(COLUMNS) - 1) + '\n'
            + '\n'.join(row(config, runs[config]) for config in CONFIGS) + '\n\n')


def update_summary(paths, output: Path = VOLET_B_SUMMARY) -> None:
    """Écrit ou remplace la section des 4 configurations sans toucher au reste du fichier."""
    new = section(load_runs(paths))
    text = output.read_text(encoding='utf-8') if output.exists() else '# Résultats du volet B\n'
    match = re.compile(rf'^{re.escape(TITLE)}\s*\n.*?(?=^## |\Z)', re.M | re.S).search(text)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text[:match.start()] + new + text[match.end():] if match else text.rstrip() + '\n\n' + new,
                      encoding='utf-8', newline='\n')


def main(argv=None) -> None:
    """Ligne de commande : les 4 dossiers de run (ou metrics.json), dans n'importe quel ordre."""
    parser = argparse.ArgumentParser(description='SCRUM-45 : résumé des 4 configurations du volet B.')
    parser.add_argument('runs', nargs=4, type=Path)
    parser.add_argument('--output', type=Path, default=VOLET_B_SUMMARY)
    args = parser.parse_args(argv)
    try:
        update_summary(args.runs, resolve_path(args.output))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f'Résumé : {args.output}')


if __name__ == '__main__':
    main()
