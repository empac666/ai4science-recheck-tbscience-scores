"""Verify bytes and code before any main analysis; no network and no cache writes."""
import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from .constants import VERSIONS


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_paths(root):
    return sorted(p for folder in ['analysis','tests','tools'] for p in (root/folder).rglob('*.py'))


def code_hashes(root):
    return {str(p.relative_to(root)):digest(p) for p in code_paths(root)}


def verify_code(root):
    frozen=json.loads((root/'artifacts/code_freeze.json').read_text())
    if frozen['sha256'] != code_hashes(root):
        raise ValueError('Code differs from pre-execution hash freeze')
    for name in ['PREREG.md','feasibility.md','INPUTS_SHA256SUMS']:
        if digest(root/name) != frozen['locked_documents'][name]:
            raise ValueError('Locked document changed')
    return frozen


def verify_inputs(root,cache):
    manifest=json.loads((root/'INPUTS_SHA256SUMS').read_bytes())
    checks=[]
    for item in manifest['inputs']:
        file=cache/item['file']
        if not file.is_file():
            checks.append({'file':item['file'],'matches':False,'reason':'missing input'})
            continue
        size=file.stat().st_size;sha=digest(file)
        checks.append({'file':item['file'],'expected_bytes':item['bytes'],'observed_bytes':size,'expected_sha256':item['sha256'],
                       'observed_sha256':sha,'matches':size==item['bytes'] and sha==item['sha256'],'role':item['role']})
    return manifest, {'verified_at_utc':now(),'checks':checks,'all_match':all(c['matches'] for c in checks)}


def versions():
    actual={'python':platform.python_version()}
    for name in ['numpy','beautifulsoup4','matplotlib']:
        try:actual[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:actual[name]=None
    try:
        p=subprocess.run(['pdftotext','-v'],capture_output=True,text=True,check=True)
        actual['pdftotext']=re.search(r'pdftotext version ([0-9.]+)',p.stderr+p.stdout).group(1)
    except (OSError,subprocess.CalledProcessError,AttributeError):actual['pdftotext']=None
    return {'recorded_at_utc':now(),'implementation':platform.python_implementation(),
            'system':{'os':platform.system(),'release':platform.release(),'architecture':platform.machine()},
            'locked':VERSIONS,'actual':actual,'matches':{k:actual[k]==v for k,v in VERSIONS.items()}}
