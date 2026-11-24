"""Extraction déterministe des faits et preuves de la v16 depuis les lignes HDFS."""
from collections import Counter, defaultdict
from datetime import datetime
import re
from data.parse_hdfs import extract_message, match_event
from teamai.paths import SLM
from volet_b.slm.v16.policy import is_notable, network_evidence, make_cause_catalog, ATTENTION_CODES
import json

ATTENTION = ATTENTION_CODES
EXCERPT_BLOCK = 'blk_7800270577648029182'
GLOSSARY = json.loads((SLM / 'v16' / 'glossaire.json').read_text(encoding='utf-8'))


def prepare_block(bid, lines, templates, index=0, split=None):
    """Calcule les preuves depuis des couples (numéro de ligne source, texte), sans label.

    Les numéros d'origine sont indispensables aux références Txx figées.
    templates est le résultat de data.parse_hdfs.compile_templates.
    """
    events = []
    for line_no, raw in lines:
        if bid not in set(re.findall(r'blk_-?\d+', raw)):
            raise ValueError('ligne étrangère au bloc')
        msg = extract_message(raw)
        code, status = match_event(msg, templates) if msg else (None, 'invalid')
        if status != 'matched':
            raise ValueError(f'ligne {line_no} non reconnue : {status}')
        events.append({'line':line_no, 'timestamp':datetime.strptime(raw[:13],'%y%m%d %H%M%S').isoformat(' '),
                       'event':code, 'level':raw.split()[3], 'message':msg, 'raw':raw.rstrip()})
    if not events or events != sorted(events, key=lambda e:(e['timestamp'],e['line'])):
        raise ValueError('bloc vide ou lignes hors ordre chronologique')
    glossary = GLOSSARY
    counts = Counter(e['event'] for e in events)
    warn_count = sum(e['level']=='WARN' for e in events)
    seconds = int((datetime.fromisoformat(events[-1]['timestamp'])-datetime.fromisoformat(events[0]['timestamp'])).total_seconds())
    h,rest = divmod(seconds,3600); m,s = divmod(rest,60)
    facts = [f"[F01] {len(events)} lignes du bloc ; intervalle {events[0]['timestamp']} à {events[-1]['timestamp']} ; durée {h} h {m:02d} min {s:02d} s ({seconds} secondes).", f'[F02] Nombre total de lignes WARN : {warn_count}.']
    for code,n in sorted(counts.items(),key=lambda kv:int(kv[0][1:])):
        facts.append(f'[F{len(facts)+1:02d}] {code} : {n} occurrence(s) ; {glossary[code]}.')
    baseline_facts = facts[:]
    groups = defaultdict(list)
    for e in events: groups[e['timestamp']].append(e['event'])
    same_second_groups = []
    for stamp,codes in groups.items():
        if len(codes)<2: continue
        # Tri par code, jamais par position dans le journal : ce n'est pas une séquence.
        codes = sorted(codes,key=lambda c:int(c[1:]))
        ref = f'F{len(facts)+1:02d}'
        facts.append(f'[{ref}] {stamp} — même seconde : '+', '.join(codes)+' ; ordre non déterminable.')
        same_second_groups.append({'ref':ref,'timestamp':stamp,'codes':codes})
    positions = defaultdict(list)
    for i,e in enumerate(events): positions[e['event']].append(i)
    keep = sorted({i for p in positions.values() for i in (p[0],p[-1])})
    timeline = [f"[T{j:02d}] {events[i]['timestamp']} {events[i]['event']} (ligne {events[i]['line']})." for j,i in enumerate(keep,1)]
    notable = [e for e in events if e['event'] in ATTENTION or e['level'] in ('WARN','ERROR','FATAL')]
    original_notable = notable[:]
    if bid == EXCERPT_BLOCK:
        # Types présents + bornes temporelles, puis couverture régulière.
        by_code = defaultdict(list)
        for j,e in enumerate(notable): by_code[e['event']].append(j)
        kept = {j for indices in by_code.values() for j in (indices[0],indices[-1])}
        target = 6
        assert len(kept)<=target and len(notable)==15
        for j in (round(k*(len(notable)-1)/(target-1)) for k in range(target)):
            if len(kept)<target: kept.add(j)
        for j in range(len(notable)):
            if len(kept)<target: kept.add(j)
        notable = [notable[j] for j in sorted(kept)]
        facts.append(f'[F{len(facts)+1:02d}] Messages atypiques : {len(original_notable)} au total ; {len(notable)} extraits reproduits, incluant la première et la dernière occurrence de chaque code atypique. Les compteurs et la chronologie portent sur toutes les lignes du bloc.')
    evidence = [f"[L{j:02d}] {e['raw']}" for j,e in enumerate(notable,1)]
    block = {'block_id':bid,'split':split,'selection_index':index,
        'worker_id':index//20,'counts':dict(counts),'warn_count':warn_count,'duration_seconds':seconds,
        'attention':bool(notable),'facts':facts,'timeline':timeline,'evidence':evidence,
        'evidence_codes':{f'L{j:02d}':e['event'] for j,e in enumerate(notable,1)},
        
        'same_second_groups':same_second_groups,'baseline_v13_facts':baseline_facts,'raw_events':events}
    block['evidence_selection'] = {'total_notable':len(original_notable),'shown':len(notable),
        'selected_lines':[e['line'] for e in notable], 'omitted_lines':[e['line'] for e in original_notable if e not in notable],
        'user_authorized_length_exception':bid==EXCERPT_BLOCK}
    block['network_evidence'] = network_evidence(events)
    block['cause_catalog'] = make_cause_catalog(block)
    block['required_factual_codes'] = sorted(set(block['counts']) & {'E24','E27','E28'})
    return block
