"""Freeze execution code after synthetic tests and before main-data execution."""
import json
from pathlib import Path
from .constants import LOCK
from .environment import code_hashes, digest, now


def main():
    root=Path('.')
    destination=root/'artifacts/code_freeze.json'
    if destination.exists():raise SystemExit('Freeze already exists; preserve it and document any new execution epoch')
    destination.parent.mkdir(exist_ok=True)
    archives=sorted(str(p) for p in (root/'artifacts').glob('execution_[0-9][0-9]'))
    data={'frozen_at_utc':now(),'protocol_lock_commit':LOCK,'scope':'all analysis, tests, and tools Python code; synthetic tests preceded this freeze',
          'execution_epoch':len(archives)+1,'prior_epoch_archives':archives,
          'sha256':code_hashes(root),'locked_documents':{p:digest(root/p) for p in ['PREREG.md','feasibility.md','INPUTS_SHA256SUMS']}}
    destination.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (root/'artifacts/CODE_SHA256SUMS').write_text(''.join(f'{h}  {p}\n' for p,h in data['sha256'].items()),encoding='utf-8')
    print('Code hashes frozen before formal execution')


if __name__=='__main__':main()
