"""Check formal outputs against independently read aggregate CSVs and lock."""
import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from analysis.constants import LOCK
from analysis.environment import verify_code


def main():
    root=Path('.')
    r=json.loads((root/'results.json').read_text())
    assert r['status']=='completed'
    assert set(r['audit_predictions'])=={f'AP-{i:02d}' for i in range(1,20)}
    assert all(a['matches'] and a['status']=='completed' and a['observed'] is not None and a['deviation'] is None for a in r['audit_predictions'].values())
    assert all(a['verdict']=='一致' for a in r['official'].values())
    assert all(m['verdict']=='一致' and all(m['field_checks'].values()) for m in r['mirrors'].values())
    rows=list(csv.DictReader((root/'task_job_counts.csv').open(encoding='utf-8')))
    assert len(rows)==420
    keys={(x['row_id'],x['task_id'],x['trial_id']) for x in rows};assert len(keys)==420
    counted=defaultdict(lambda:[0,0]);tasks=defaultdict(lambda:[0,0]);jobs=defaultdict(lambda:[0,0])
    for x in rows:
        counted[x['system']][0]+=int(x['K']);counted[x['system']][1]+=int(x['N'])
        tasks[(x['system'],x['task_id'])][0]+=int(x['K']);tasks[(x['system'],x['task_id'])][1]+=int(x['N'])
        jobs[(x['system'],x['job_id'])][0]+=int(x['K']);jobs[(x['system'],x['job_id'])][1]+=int(x['N'])
    for system,(k,n) in counted.items():assert (k,n)==(r['official'][system]['K'],r['official'][system]['N'])
    for x in csv.DictReader((root/'task_counts.csv').open()):assert tasks[(x['system'],x['task_id'])]==[int(x['K']),int(x['N'])]
    for x in csv.DictReader((root/'job_counts.csv').open()):assert jobs[(x['system'],x['job_id'])]==[int(x['K']),int(x['N'])]
    claims=list(csv.DictReader((root/'claims_table.csv').open(encoding='utf-8')))
    assert len(claims)==8 and Counter(x['main_label'] for x in claims if x['in_seven_claims']=='True')==r['seven_claim_label_counts']
    assert r['primary_support_count']==sum(x['primary_support']=='True' for x in claims if x['in_seven_claims']=='True')
    assert r['bootstrap']['status']=='completed' and r['bootstrap']['replicates']==10000
    assert r['bootstrap']['primary_seed']==2026101001 and r['bootstrap']['stratified_seed']==2026101002
    for filename,marker,limit in [('x_post.md','Post 1 (',270),('x_post_cn.md','主帖（',140)]:
        text=(root/filename).read_text();blocks=text.split('\n\n');post=next(blocks[i+1] for i,b in enumerate(blocks) if b.startswith(marker))
        assert len(post)<=limit and 'figures/figure1.png' in text and LOCK in text
    first=(root/'REPORT.md').read_text().splitlines()[0]
    assert first.startswith('对已公开的70任务×3次试次标签的独立对账重加总得到：')
    assert all(x not in first for x in ['63.3','64.6','65.71','52.6','34.29'])
    for name in ['PREREG.md','feasibility.md','INPUTS_SHA256SUMS']:
        locked=subprocess.run(['git','show',f'{LOCK}:{name}'],capture_output=True,check=True).stdout
        assert (root/name).read_bytes()==locked
    assert (root/'figures/figure1.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    verify_code(root)
    print('Formal artifacts verified: AP-01–19, aggregate CSVs, strict mirrors, bootstrap settings, drafts, locked documents and code hashes')


if __name__=='__main__':main()
