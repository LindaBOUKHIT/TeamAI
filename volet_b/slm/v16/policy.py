"""Règles locales v16 : preuves du bloc uniquement, aucun accès externe."""
import json
import re
import unicodedata

ATTENTION_CODES = {'E1','E4','E7','E8','E10','E12','E13','E14','E17','E20','E24','E27','E28','E29'}
EXCEPTION_CODES = {'E4','E7','E8','E10','E12','E14','E17'}
FACTUAL_REQUIRED_CODES = {'E24','E27','E28'}
# Exemples explicitement demandés par l'utilisateur. Leur présence réelle est
# comptée séparément ; aucun de ces motifs n'a été trouvé dans les 85 blocs connus.
NETWORK_EVIDENCE_PATTERNS = {
    'Socket': r'\bsocket\w*',
    'Connection': r'\bconnection\w*',
    'timeout': r'\btimeout\b|\btimed\s+out\b',
    'Broken pipe': r'\bbroken\s+pipe\b',
    'Connection reset': r'\bconnection\s+reset\b',
}
NETWORK_HYPOTHESIS_PATTERN = r'\breseau\w*|\bnetwork\w*|\bconnex\w*|\bconnect\w*|\btimeout\w*|\btimed\s+out\b|\bsocket\w*|\bbroken\s+pipe\b|\bdelai\s+(?:de\s+)?(?:connexion|reseau)'


def folded(text):
    """Normalise un texte en minuscules sans accents pour les contrôles lexicaux."""
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')


def is_notable(event):
    """Indique si un événement porte un code atypique ou un niveau WARN, ERROR ou FATAL."""
    return event['event'] in ATTENTION_CODES or event['level'] in ('WARN','ERROR','FATAL')


def is_warn_or_exception(event):
    """Indique si le niveau, le code ou le message signale un avertissement ou une exception."""
    return event['level'] in ('WARN','ERROR','FATAL') or event['event'] in EXCEPTION_CODES or bool(re.search(r'\bexception\b',event['message'],re.I))


def network_evidence(events):
    """Extrait les motifs réseau des seuls messages WARN ou d’exception, avec leur ligne."""
    matches=[]
    for event in events:
        if not is_warn_or_exception(event):
            continue
        for name,pattern in NETWORK_EVIDENCE_PATTERNS.items():
            match=re.search(pattern,event['message'],re.I)
            if match:
                matches.append({'line':event['line'],'event':event['event'],'marker':name,'matched_text':match[0]})
    return matches


def make_cause_catalog(block):
    """Causes immédiates explicitement lisibles ; jamais de diagnostic racine inventé.

    Les candidats sont conditionnés par les messages de CE bloc. Une phrase
    générique E4, une adresse IP ou un nom de composant ne sont pas une cause.
    Les libellés deviennent une liste fermée ; les références sont calculées.
    """
    by_line={e['line']:e for e in block['raw_events']}
    shown={line:ref for line,ref in zip(block['evidence_selection']['selected_lines'],block['evidence_codes'])}
    codes=sorted({e['event'] for e in block['raw_events'] if is_notable(e)},key=lambda c:int(c[1:]))
    catalog=[]
    for code in codes:
        candidates=[]
        for line,ref in shown.items():
            e=by_line[line]
            if e['event']!=code:
                continue
            label=quote=hypothesis=None
            if code=='E7' and 'Could not read from stream' in e['message']:
                label='impossibilité de lire le flux pendant l’écriture'
                quote='Could not read from stream'
                hypothesis=f'L’exception d’écriture pourrait être liée à l’impossibilité de lire le flux [{ref}].'
            elif code=='E20' and 'BlockInfo not found in volumeMap' in e['message']:
                label='entrée BlockInfo absente de volumeMap lors de la suppression'
                quote='BlockInfo not found in volumeMap'
                hypothesis=f'L’erreur de suppression pourrait être liée à l’absence d’entrée BlockInfo dans volumeMap [{ref}].'
            # Aucune cause racine déduite des autres codes : les messages
            # génériques/redondants/sans fichier ne la départagent pas.
            if label and not any(c['cause']==label for c in candidates):
                candidates.append({'cause':label,'quote':quote,'reference':ref,'line':line,'hypothesis':hypothesis})
        catalog.append({'code':code,'candidates':candidates,'unknown_cause':not candidates})
    return catalog


def allowed_hypotheses(block):
    """Renvoie les seules formulations conditionnelles autorisées pour les preuves du bloc."""
    return [c['hypothesis'] for row in block['cause_catalog'] for c in row['candidates']]


def cause_catalog_text(block):
    """Rend le catalogue fermé du bloc sous forme de texte à joindre au prompt."""
    if not block['cause_catalog']:
        return 'Aucun indice d’incident reconnu : hypotheses=[] et infos_manquantes=[].'
    lines=[]
    for row in block['cause_catalog']:
        if not row['candidates']:
            lines.append(row['code']+' : [] ; cause indéterminée, aucune hypothèse autorisée.')
        else:
            for c in row['candidates']:
                lines.append(f"{row['code']} : « {c['quote']} » [{c['reference']}] autorise seulement : {c['hypothesis']}")
    return '\n'.join(lines)


def reference_tokens(text):
    """Références F/T/L/E, groupées, nues ou plages ; normalisation des zéros."""
    found=set()
    def canonical(prefix,number):
        """Normalise une référence et conserve deux chiffres pour les préfixes F, T et L."""
        return prefix+(str(number) if prefix=='E' else f'{number:02d}')
    for m in re.finditer(r'\b([FTLE])(\d+)\s*[-–]\s*([FTLE])?(\d+)\b',text):
        start,end=int(m[2]),int(m[4]);end_prefix=m[3] or m[1]
        if end_prefix!=m[1] or start<1 or end<start or end-start>100:
            found.add('INVALID_REFERENCE_RANGE')
        else:
            found.update(canonical(m[1],n) for n in range(start,end+1))
    for m in re.finditer(r'\b([FTLE])(\d+)\b',text):
        found.add(canonical(m[1],int(m[2])))
    return found


def answer_strings(value,path=''):
    """Parcourt les chaînes d’une réponse JSON en conservant leur chemin de champ."""
    if isinstance(value,str):
        yield path,value
    elif isinstance(value,list):
        for i,v in enumerate(value,1):
            yield from answer_strings(v,f'{path}[{i}]')
    elif isinstance(value,dict):
        for key,v in value.items():
            yield from answer_strings(v,f'{path}.{key}' if path else key)


def unknown_reference_errors(answer,block):
    """Liste les références de chaque champ qui sont absentes des preuves du bloc."""
    allowed=reference_tokens('\n'.join(block['facts']+block['timeline']+block['evidence']))|set(block['counts'])
    errors=[]
    for path,text in answer_strings(answer):
        missing=reference_tokens(text)-allowed
        if missing:
            errors.append(path+' : références inexistantes '+','.join(sorted(missing)))
    return errors


def hypothesis_anchor_errors(answer,block):
    """Liste les hypothèses sans ancrage Lxx ou Exx existant dans le bloc."""
    values=answer.get('hypotheses',[])
    if not isinstance(values,list):
        return []
    allowed=set(block['evidence_codes'])|set(block['counts'])
    return [f'hypotheses[{i}] : ancrage Lxx ou Exx existant requis'
            for i,h in enumerate(values,1) if isinstance(h,str) and not reference_tokens(h)&allowed]


def network_alert_details(answer,block):
    """Alerte lexicale demandée, pas un jugement de causalité.

    Un motif présent dans une ligne autorise ce contrôle minimal, sans prouver
    la cause réseau. Une négation peut encore déclencher l'alerte : à relire.
    """
    if block['network_evidence']:
        return []
    values=answer.get('hypotheses',[])
    if not isinstance(values,list):
        return []
    return [{'hypothesis_index':i,'text':h,'alert':'cause_reseau_sans_appui'}
            for i,h in enumerate(values,1) if isinstance(h,str) and re.search(NETWORK_HYPOTHESIS_PATTERN,folded(h))]


def network_alerts_from_text(text,block):
    """Extrait les alertes réseau d’une réponse JSON ; rend une liste vide si elle est illisible."""
    try: a=json.loads(text)
    except (ValueError,TypeError): return []
    return network_alert_details(a,block) if isinstance(a,dict) else []


def factual_mention_errors(answer,block):
    """Une copie exacte de la définition du code satisfait la mention factuelle."""
    facts=answer.get('faits_observes',[])
    if not isinstance(facts,list):
        return []
    present=set()
    for fact in facts:
        if fact in block['facts']:
            m=re.match(r'\[F\d+\] (E\d+) :',fact)
            if m: present.add(m[1])
    return ['mention factuelle obligatoire absente : '+c for c in sorted(FACTUAL_REQUIRED_CODES&set(block['counts'])-present)]


def retry_errors(text,block):
    """Liste les erreurs de références, d’ancrage et de réseau déclenchant la correction v16."""
    try: a=json.loads(text)
    except (ValueError,TypeError): return []
    if not isinstance(a,dict): return []
    errors=unknown_reference_errors(a,block)+hypothesis_anchor_errors(a,block)
    errors += [f"hypotheses[{v['hypothesis_index']}] : cause réseau sans appui ; aucune ligne WARN ou d’exception du bloc ne contient d’indice réseau" for v in network_alert_details(a,block)]
    return list(dict.fromkeys(errors))


def repair_prompt(base,errors):
    # La première réponse reste dans le journal. Les champs complets sont
    # régénérés une seule fois avec les erreurs exactes, sans historique coûteux.
    """Ajoute les erreurs précises au prompt pour régénérer une seule réponse complète."""
    return base+'\n\nCORRECTION UNIQUE :\n'+'\n'.join('- '+e for e in errors)+'\nRends les six champs JSON complets. Corrige ces erreurs avec les seules preuves et causes autorisées ; hypotheses=[] reste permis. La seconde réponse sera conservée telle quelle.'
