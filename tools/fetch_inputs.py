"""Verify frozen input bytes; --fetch explicitly refetches HTTP inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--fetch', action='store_true', help='Refetch HTTP bodies; verify before saving')
    action.add_argument('--verify-only', action='store_true', help='Verify local files (the default)')
    parser.add_argument('--file', action='append', dest='files', help='Select a filename; repeat as needed')
    parser.add_argument('--output', default='data_cache', help='Cache directory relative to repository root')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    requested_output = Path(args.output)
    if requested_output.is_absolute():
        parser.error('--output must be relative')
    manifest = json.loads((root / 'INPUTS_SHA256SUMS').read_text(encoding='utf-8'))
    records = manifest['inputs']
    names = {record['file'] for record in records}
    if args.files:
        unknown = set(args.files) - names
        if unknown:
            parser.error('Unknown frozen filename: ' + ', '.join(sorted(unknown)))
        records = [record for record in records if record['file'] in args.files]
    output = root / requested_output
    failures = 0
    for record in records:
        name = record['file']
        if Path(name).name != name or name in ('.', '..'):
            parser.error('Manifest filenames must be plain basenames')
        target = output / name
        try:
            fetch_http = args.fetch and record['kind'] == 'http_bytes'
            if fetch_http:
                url = record['url']
                if not url.startswith('https://'):
                    raise ValueError('Only HTTPS input URLs are supported')
                request = Request(url, headers={'User-Agent': 'R11fix-input-verifier/1.0'})
                try:
                    response = urlopen(request, timeout=45)
                except HTTPError as error:
                    response = error  # Frozen 403/404 bodies are access evidence.
                with response:
                    status = response.code
                    data = response.read()
                if status != record['status']:
                    raise ValueError('HTTP status differs from frozen response')
            else:
                if args.fetch and record['kind'] == 'rendered_record':
                    print(f'LOCAL ONLY {name}: HTTP cannot recreate the saved rendered record')
                data = target.read_bytes()
            if len(data) != record['bytes']:
                raise ValueError('Byte count differs from frozen input')
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError('SHA-256 differs from frozen input')
            if fetch_http:
                output.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(name + '.verified.tmp')
                temporary.write_bytes(data)
                temporary.replace(target)
            print(f'OK {name}')
        except (OSError, ValueError, URLError):
            failures += 1
            # Do not emit local paths, response bodies, or arbitrary exception text.
            print(f'FAIL {name}: missing bytes, fetch failure, or frozen metadata mismatch', file=sys.stderr)
    print(f'Checked {len(records)} frozen inputs; failures={failures}')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
