"""Extract only frozen source nodes; output small evidence strings, never bodies."""
import json
import re
import subprocess
from decimal import Decimal
from bs4 import BeautifulSoup
from .constants import DATASET, LEADERBOARD, MIRROR_URL, PROVENANCE_TEXT, RELEASE_COMMIT, SYSTEMS
from tools.audit_rules import one_decimal, split_display_accuracy


def unique(items, description):
    if len(items) != 1:
        raise ValueError(f'{description}: expected unique node, got {len(items)}')
    return items[0]


def rsc_text(soup):
    pieces = []
    for node in soup.find_all('script'):
        text = node.string or ''
        for match in re.finditer(r'self\.__next_f\.push\(', text):
            array, _ = json.JSONDecoder(parse_float=Decimal).raw_decode(text[match.end():])
            if len(array) > 1 and isinstance(array[1], str):
                pieces.append(array[1])
    return ''.join(pieces)


def objects_in_rsc(text):
    decoder = json.JSONDecoder(parse_float=Decimal)
    # Decode objects starting at every brace. Parent and nested objects remain
    # distinct, enabling uniqueness checks on an exact object ID and slug.
    for match in re.finditer(r'\{', text):
        try:
            obj, _ = decoder.raw_decode(text[match.start():])
        except ValueError:
            continue
        if isinstance(obj, dict):
            yield obj


def fact(literal=None, state=None):
    return {'state': state or ('缺失' if literal is None else '已见字面'), 'literal': literal}


def source_metadata(entry, path, hits, date, date_type, primary):
    return {'file': entry['file'], 'url': entry['url'], 'sha256': entry['sha256'], 'http_status': entry['status'],
            'input_kind': entry['kind'], 'extraction_path': path, 'hit_strings': hits,
            'date_field': date, 'date_type': date_type, 'fetched_at_utc': entry['fetched_at_utc'],
            'primary_support': bool(primary and entry['status'] == 200 and entry['kind'] == 'http_bytes' and hits and date)}


def missing_fields():
    return {k: fact() for k in ['model','agent','effort_literal','effort_operation','trials','metric_formula','dataset_version','run_identity']}


def classify(fields, extraction_status):
    required = ['model','agent','effort_operation','trials','metric_formula','dataset_version','run_identity']
    missing = [f for f in required if fields[f]['state'] == '缺失']
    if extraction_status != 'completed' or missing:
        return {'label': '来源未完整披露', 'first_priority': 1, 'missing_required_fields': missing,
                'extraction_failed': extraction_status != 'completed', 'interpretation': 'priorities 2–5 not applicable'}
    # All frozen external sources lack run identity. Do not invent an identity
    # or silently select another label if a source unexpectedly becomes complete.
    raise ValueError('Unexpected complete external identity; stop this comparison')


def extract(cache, manifest, official, pdf_version_matches):
    entries = {e['file']: e for e in manifest['inputs']}
    claims = {}
    identity_scopes = {}
    s1 = manifest['unfetched_claims'][0]
    claims['S1'] = {'record':'S1','system':'Astra','display':'63','status':'not_read', 'facts':missing_fields(),
                    'source': {'file':None,'url':s1['url'],'sha256':None,'http_status':None,'input_kind':'not_read','extraction_path':None,
                               'hit_strings':[],'date_field':None,'date_type':'unknown','fetched_at_utc':None,'primary_support':False},
                    'main_label':'来源未完整披露','comparison':None}
    for name, sid in [('Astra','S4'),('Fable','S7')]:
        rid = SYSTEMS[name][0]
        # A fresh parse is used for source extraction, separate from both counters.
        doc = json.loads((cache/'science_board_v01.json').read_bytes(), parse_float=Decimal)
        row = unique([r for r in doc['rows'] if r['id']==rid],sid)
        display,_ = split_display_accuracy(row['metrics']['display_accuracy'])
        fields = missing_fields()
        fields.update(model=fact(row['metadata']['model_display']['label'],'与官方相同'),agent=fact(row['metadata']['agent_display']['label'],'与官方相同'),
                      effort_literal=fact(row['metadata']['reasoning_effort']),effort_operation=fact('max','与官方相同'),
                      trials=fact(row['metrics']['tasks'],'与官方相同'),metric_formula=fact('pass@1','与官方相同'),
                      dataset_version=fact(doc['leaderboard']['dataset_version_ids'][0],'与官方相同'),run_identity=fact(rid,'与官方相同'))
        claims[sid]={'record':sid,'system':name,'display':display,'status':'completed','facts':fields,'main_label':official[name]['verdict'],
                     'comparison':f'official {name} exact mean','N_same_document':row['metrics']['tasks'],
                     'source':source_metadata(entries['science_board_v01.json'],f'rows[id={rid}].metrics.display_accuracy',
                                              [row['metrics']['display_accuracy']],{'created_at':row['created_at'],'updated_at':row['updated_at']},'leaderboard row timestamps',True)}
    # AA: unique innermost summary + exact RSC model object, no derived cache.
    try:
        soup = BeautifulSoup((cache/'aa_science.html').read_bytes(),'html.parser')
        def innermost(predicate):
            return [n for n in soup.find_all('div') if predicate(n.get_text(' ',strip=True)) and not any(predicate(c.get_text(' ',strip=True)) for c in n.find_all('div'))]
        summary = unique(innermost(lambda t:'GPT-6 Astra (Max)' in t and 'with a score of 63.3%' in t),'AA summary').get_text(' ',strip=True)
        method = unique(innermost(lambda t:'three repeats per task' in t and 'mini-swe-agent' in t),'AA method').get_text(' ',strip=True)
        task_description = unique(innermost(lambda t: t.startswith('A 70-task benchmark')),'AA 70 tasks').get_text(' ',strip=True)
        rsc = rsc_text(soup)
        model = unique([o for o in objects_in_rsc(rsc) if o.get('id')=='2f339a97-9a0d-499a-9cb5-e0db665bfa25' and o.get('slug')=='gpt-6-astra'],'AA model')
        raw = str(model['terminalBenchScience'])
        display = unique(re.findall(r'with a score of ([0-9]+\.[0-9]+)%',summary),'AA score')
        if raw != '0.633333333333333' or model['releaseDate'] != '2026-09-03':
            raise ValueError('AA frozen raw value/date mismatch')
        fields = missing_fields()
        fields.update(model=fact(model['name']),agent=fact('mini-swe-agent','与官方不同'),effort_literal=fact(model['suffix']),
                      trials=fact('three repeats per task','与官方相同'),metric_formula=fact('pass@1 averaged over three repeats per task','与官方相同'))
        claims['S1a']={'record':'S1a','system':'Astra','display':display,'status':'completed','facts':fields,
                       'N_same_document':70*3,'embedded_ratio':raw,'public_version_literal':'Terminal-Bench-Science 0.1.0',
                       'operation_ambiguity':None,'comparison':'S1a vs official Astra',
                       'source':source_metadata(entries['aa_science.html'],'innermost summary/method div; self.__next_f.push RSC exact id/slug',
                                                ['GPT-6 Astra (Max)','with a score of '+display+'%','mini-swe-agent','three repeats per task','70-task',raw],model['releaseDate'],'model release date; not evaluation date',True)}
        identity_scopes['S1a'] = soup.get_text(' ',strip=True) + rsc
        assert not any(SYSTEMS['Astra'][0] in x or LEADERBOARD in x or DATASET in x for x in [summary,method,task_description,rsc])
    except (ValueError,KeyError,AssertionError) as err:
        claims['S1a']=failed('S1a','Astra','63.3',entries['aa_science.html'],str(err))
    # Rendered record only: positional table column, not the HTTP 403 body.
    try:
        rendered=json.loads((cache/'openai_web_rendered.json').read_bytes())
        text=rendered['tool_result']
        header=unique(re.findall(r'^L182: (.*)$',text,re.M),'S2 header')
        table=unique(re.findall(r'^L183: (.*)$',text,re.M),'S2 table')
        method=unique(re.findall(r'^L224: (.*)$',text,re.M),'S2 method')
        if header.split('|')[1].strip() not in ['GPT-6 Astra','GPT‑6 Astra'] or table.split('|')[0].strip() != 'Terminal-Bench Science 0.1' or 'maximum at any effort' not in method:
            raise ValueError('S2 frozen table/method mismatch')
        display=table.split('|')[1].strip().removesuffix('%')
        if not text.startswith('GPT-6 Astra:') or display != '64.6':raise ValueError('S2 value/model mismatch')
        fields=missing_fields();fields.update(model=fact('GPT-6 Astra'),effort_literal=fact('maximum at any effort'))
        claims['S2']={'record':'S2','system':'Astra','display':display,'status':'completed','facts':fields,'comparison':'S2 vs official Astra',
                      'operation_ambiguity':['best fixed effort over the benchmark','per-task cross-effort oracle envelope'],
                      'source':source_metadata(entries['openai_web_rendered.json'],'tool_result L182/L183/L224',
                                               ['GPT-6 Astra','64.6%','maximum at any effort'],rendered['retrieved_at_utc'],'rendered retrieval time; publication/run time unknown',False),
                      'original_http_status':entries['openai_astra.html']['status']}
        identity_scopes['S2'] = text
    except (ValueError,KeyError,IndexError) as err:
        claims['S2']=failed('S2','Astra','64.6',entries['openai_web_rendered.json'],str(err))
    # Historical announcement only. Current Vals methods are never consulted.
    try:
        soup=BeautifulSoup((cache/'vals_home.html').read_bytes(),'html.parser')
        slug='2026-09-11-terminal-bench-science'
        node=unique(soup.select(f'div.hidden.update-content[data-update-slug="{slug}"]'),'Vals announcement')
        text=node.get_text(' ',strip=True)
        def unpack(v):
            if isinstance(v,list) and len(v)==2 and type(v[0]) is int:
                if v[0]==0: return unpack(v[1])
                if v[0]==1: return [unpack(x) for x in v[1]]
            if isinstance(v,dict):return {k:unpack(x) for k,x in v.items()}
            return v
        props=unpack(json.loads(node.find_parent('astro-island')['props']))
        update=unique([u for u in props['updates'] if u['slug']==slug],'Vals date')
        date=update['data']['date']
        if date != '09/11/2026' or 'one harness fixed' not in text or 'pass@1' not in text:
            raise ValueError('Vals date/method mismatch')
        for sid,system,label in [('S3','Astra','GPT-6 Astra'),('S6','Fable','Claude Fable 5.1')]:
            display=unique(re.findall(re.escape(label)+r'(?: leads)? (?:at )?([0-9]+\.[0-9]+)%',text),sid+' value')
            fields=missing_fields();fields.update(model=fact(label))
            claims[sid]={'record':sid,'system':system,'display':display,'status':'completed','facts':fields,'comparison':sid+' vs official '+system,
                         'partial_method_literals':['one harness fixed','pass@1'],'N_same_document':None,
                         'source':source_metadata(entries['vals_home.html'],f'div.hidden.update-content[data-update-slug={slug}]; ancestor astro-island props updates.data.date',
                                                  [label,display+'%','one harness fixed','pass@1'],date,'announcement date',True)}
            identity_scopes[sid] = text
    except (ValueError,KeyError,TypeError,AttributeError) as err:
        for sid,system,display in [('S3','Astra','65.71'),('S6','Fable','34.29')]:claims[sid]=failed(sid,system,display,entries['vals_home.html'],str(err))
    # PDF: correct locked tool or explicit extraction failure, no substitute.
    try:
        if not pdf_version_matches:raise ValueError('pdftotext version mismatch; protocol extraction stopped')
        entry=entries['anthropic_systemcard.html']
        with (cache/entry['file']).open('rb') as f:
            if f.read(5)!=b'%PDF-' or entry['content_type']!='application/pdf':raise ValueError('Invalid frozen PDF input')
        proc=subprocess.run(['pdftotext','-layout',str(cache/entry['file']),'-'],capture_output=True,text=True,check=True)
        text=' '.join(proc.stdout.split())
        start=unique([m.start() for m in re.finditer(r'8\.7 Terminal-Bench-Science 0\.1',text)],'PDF section')
        section=text[start:]
        next_section=re.search(r' 8\.8 ',section)
        if next_section:section=section[:next_section.start()]
        sentence='Claude Fable 5.1 scored 52.6% averaged over 10 trials per task (700 trials)'
        if section.count(sentence)!=1 or 'Claude Code in --bare mode' not in section or 'maximum thinking effort' not in section:
            raise ValueError('PDF frozen sentence/method not unique or missing')
        display=unique(re.findall(r'Claude Fable 5\.1 scored ([0-9]+\.[0-9]+)%',section),'PDF score')
        N=int(unique(re.findall(r'10 trials per task \(([0-9]+) trials\)',section),'PDF N'))
        fields=missing_fields();fields.update(model=fact('Claude Fable 5.1'),agent=fact('Claude Code --bare'),
                effort_literal=fact('maximum effort'),effort_operation=fact('maximum effort','与官方相同'),
                trials=fact('10 trials per task (700 trials)','与官方不同'),metric_formula=fact('averaged over 10 trials per task','与官方相同'))
        claims['S5']={'record':'S5','system':'Fable','display':display,'status':'completed','facts':fields,'N_same_document':N,'comparison':'S5 vs official Fable',
                      'method_hit_strings':['Claude Code in --bare mode','maximum thinking effort'],
                      'source':source_metadata(entry,'PDF bytes -> pdftotext -layout -> section 8.7 unique sentence',
                                               [sentence,'Claude Code in --bare mode','maximum thinking effort'],entry['last_modified'],'HTTP Last-Modified; not proof of publication/run date',True)}
        identity_scopes['S5'] = section
    except (ValueError,KeyError,subprocess.CalledProcessError) as err:
        claims['S5']=failed('S5','Fable','52.6',entries['anthropic_systemcard.html'],str(err))
    for sid in ['S1a','S2','S3','S5','S6']:
        if claims[sid]['status'] == 'completed':
            text = identity_scopes[sid]
            claims[sid]['identity_evidence'] = {
                'official_row_id_present': SYSTEMS[claims[sid]['system']][0] in text,
                'official_leaderboard_id_present': LEADERBOARD in text,
                'dataset_version_id_present': DATASET in text,
                'release_commit_present': RELEASE_COMMIT in text,
                'release_v0_1_0_present': 'v0.1.0' in text,
                'scope': 'same frozen source; Vals restricted to historical announcement; PDF section 8.7',
            }
            # An absent exact ID directly establishes missing run identity.
            # If unexpected IDs appear, save and stop rather than infer association.
            if any(claims[sid]['identity_evidence'][k] for k in ['official_row_id_present','official_leaderboard_id_present','dataset_version_id_present','release_commit_present']):
                raise ValueError('Unexpected external identity literal; comparison requires diagnosis')
        classification=classify(claims[sid]['facts'],claims[sid]['status'])
        claims[sid]['classification']=classification
        claims[sid]['main_label']=classification['label']
    return claims


def failed(sid,system,display,entry,reason):
    return {'record':sid,'system':system,'display':display,'status':'extraction_failed','error':reason,
            'facts':missing_fields(),'source':source_metadata(entry,None,[],None,'not extracted',False)}


def mirrors(cache, official):
    try:
        soup=BeautifulSoup((cache/'benchlm_science.html').read_bytes(),'html.parser')
        script=unique(soup.select('script#__NEXT_DATA__'),'mirror script')
        page=json.loads(script.string,parse_float=Decimal)['props']['pageProps']
        provenance=page['trustCard']['provenance']
    except (ValueError,KeyError,TypeError) as err:
        return {s:{'verdict':'镜像无法抽取','status':'extraction_failed','error':str(err)} for s in SYSTEMS}
    result={}
    for system,(_,_,agent,source_id,model) in SYSTEMS.items():
        try:
            row=unique([r for r in page['leaderboard'] if r['sourceModelId']==source_id],system+' mirror')
            expected={'sourceModelId':source_id,'model':model,'harness':agent,'reasoningEffort':'max','externalUrl':MIRROR_URL}
            observed={k:row[k] for k in expected}
            checks={k:observed[k]==v for k,v in expected.items()}
            expected_prov={'kind':'mirror','total':17,'text':PROVENANCE_TEXT,'sourceUrl':MIRROR_URL}
            checks.update({'provenance.'+k:provenance[k]==v for k,v in expected_prov.items()})
            checks['provenance.key_set']=set(provenance)==set(expected_prov)
            checks['provenance.total_integer']=type(provenance['total']) is int
            if type(row['score']) is bool or not isinstance(row['score'],(int,Decimal)):
                raise ValueError('invalid score type')
            score=str(row['score']);mirror_q=one_decimal(score);official_q=one_decimal(official[system]['reported_accuracy'])
            checks['score_quantized']=mirror_q==official_q
            result[system]={'verdict':'一致' if all(checks.values()) else '不一致','status':'completed',
                            'raw_fields':observed,'provenance':provenance,'score_raw_string':score,
                            'official_quantized':official_q,'mirror_quantized':mirror_q,'field_checks':checks,
                            'snapshot_date':page['lastUpdated']}
        except (ValueError,KeyError,TypeError) as err:
            result[system]={'verdict':'镜像无法抽取','status':'extraction_failed','error':str(err)}
    return result
