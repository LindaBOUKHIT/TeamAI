"""SCRUM-36 : jeu d'adaptation final issu des quatre lots corrigés."""
import pytest

from teamai.contracts import load_jsonl
from volet_b.slm import merge_lots


def test_train_val_a_jour_tries_et_hors_test():
    """Effectifs 200/40, tri par id, fichiers identiques à une nouvelle fusion, aucun bloc test."""
    splits = merge_lots.merge(merge_lots.load_lots(), merge_lots.banned_blocks())
    assert {split: len(rows) for split, rows in splits.items()} == {"train": 200, "val": 40}
    banned = merge_lots.banned_blocks()
    assert banned
    files = {split: load_jsonl(path) for split, path in merge_lots.OUTPUTS.items()}
    for split, rows in files.items():
        assert [ex["id"] for ex in rows] == sorted(ex["id"] for ex in rows)
        assert {ex["split"] for ex in rows} == {split}
        assert not {ex["block_id"] for ex in rows} & banned
        assert merge_lots.OUTPUTS[split].read_bytes() == merge_lots.serialize(splits[split])
    assert not {ex["block_id"] for ex in files["train"]} & {ex["block_id"] for ex in files["val"]}


def test_fusion_refuse_un_bloc_test():
    """Un bloc présent dans le split test d'un manifeste bloque la fusion."""
    example = merge_lots.load_lots()[0]
    with pytest.raises(ValueError, match="interdit"):
        merge_lots.merge([example], {example["block_id"]})
