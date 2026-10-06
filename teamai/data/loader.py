"""Chargement des fichiers prétraités de Loghub HDFS_v1, au format défini dans docs/contrats.md.

    from teamai.data.loader import load_traces, load_vocab
    traces = load_traces()            # BlockId, label (0/1), anomaly_type, events (list[str])
    vocab = load_vocab()              # {"E1": 1, …, "E29": 29}, 0 réservé au padding
"""
import pandas as pd

from teamai.paths import PREPROCESSED, SAMPLE

PAD_ID = 0
MAX_LEN = 50  # couvre > 99,9 % des traces (p99 = 33 événements)


def load_traces(sample: bool = False, nrows: int | None = None) -> pd.DataFrame:
    """Une ligne par bloc : séquence d'EventId ordonnée et label binaire (1 = anomalie)."""
    path = (SAMPLE if sample else PREPROCESSED) / "Event_traces.csv"
    df = pd.read_csv(path, usecols=["BlockId", "Label", "Type", "Features"], nrows=nrows)
    df["events"] = df["Features"].str.strip("[]").str.split(",")
    df["label"] = (df["Label"] == "Fail").astype(int)
    df = df.rename(columns={"Type": "anomaly_type"})
    return df[["BlockId", "label", "anomaly_type", "events"]]


def load_templates() -> pd.DataFrame:
    """Les 29 templates Loghub : EventId (E1…E29) et EventTemplate ([*] = partie variable)."""
    return pd.read_csv(PREPROCESSED / "HDFS.log_templates.csv")


def load_vocab() -> dict[str, int]:
    """EventId → indice entier, 0 réservé au padding (contrat partagé Python / JavaScript)."""
    ids = load_templates()["EventId"]
    return {e: int(e[1:]) for e in ids}


def encode(events: list[str], vocab: dict[str, int], max_len: int = MAX_LEN) -> list[int]:
    """Séquence d'EventId → indices tronqués/complétés à max_len (troncature en fin de séquence)."""
    ids = [vocab[e] for e in events[:max_len]]
    return ids + [PAD_ID] * (max_len - len(ids))


if __name__ == "__main__":
    t = load_traces()
    lengths = t["events"].str.len()
    print(f"{len(t)} blocs · {t['label'].sum()} anomalies ({t['label'].mean():.2%})")
    print(f"longueur : médiane {lengths.median():.0f}, p99 {lengths.quantile(.99):.0f}, max {lengths.max()}")
    print(f"séquences uniques : {t['events'].map(tuple).nunique()}")
    print(f"vocabulaire : {len(load_vocab())} événements")
