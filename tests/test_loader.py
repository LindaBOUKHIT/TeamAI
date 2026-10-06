"""Chargeur partagé teamai.data.loader — format C1 / C2 de docs/contrats.md."""
import pytest

from teamai.data.loader import MAX_LEN, PAD_ID, encode


def test_traces_respectent_le_format_C1(fixture_data):
    traces = fixture_data.load_traces()
    assert list(traces.columns) == ["BlockId", "label", "anomaly_type", "events"]
    assert len(traces) == 12
    assert set(traces["label"]) == {0, 1}
    assert traces["label"].sum() == 4
    assert traces["BlockId"].str.startswith("blk_").all()


def test_sequences_sont_des_listes_d_eventid(fixture_data):
    traces = fixture_data.load_traces()
    for events in traces["events"]:
        assert isinstance(events, list) and events
        assert all(e.startswith("E") and e[1:].isdigit() for e in events)


def test_type_d_anomalie_seulement_pour_les_anomalies(fixture_data):
    traces = fixture_data.load_traces()
    assert traces.loc[traces["label"] == 0, "anomaly_type"].isna().all()
    assert traces.loc[traces["label"] == 1, "anomaly_type"].notna().all()


def test_vocabulaire_C2_29_evenements_sans_le_padding(fixture_data):
    vocab = fixture_data.load_vocab()
    assert len(vocab) == 29
    assert vocab["E1"] == 1 and vocab["E29"] == 29
    assert PAD_ID not in vocab.values()


def test_encode_complete_jusqu_a_max_len(fixture_data):
    vocab = fixture_data.load_vocab()
    ids = encode(["E5", "E22", "E11"], vocab)
    assert len(ids) == MAX_LEN
    assert ids[:3] == [5, 22, 11]
    assert set(ids[3:]) == {PAD_ID}


def test_encode_tronque_les_longues_sequences(fixture_data):
    vocab = fixture_data.load_vocab()
    longest = max(fixture_data.load_traces()["events"], key=len)
    assert len(longest) > MAX_LEN  # la fixture contient une trace de 269 événements
    assert encode(longest, vocab) == [vocab[e] for e in longest[:MAX_LEN]]


def test_encode_refuse_un_evenement_inconnu(fixture_data):
    with pytest.raises(KeyError):
        encode(["E99"], fixture_data.load_vocab())


@pytest.mark.full_data
def test_corpus_complet_chiffres_de_reference():
    """Les chiffres cités dans docs/contrats.md et le rapport."""
    from teamai.data.loader import load_traces

    traces = load_traces()
    assert len(traces) == 575_061
    assert traces["label"].sum() == 16_838
    assert traces["events"].map(tuple).nunique() == 18_373
