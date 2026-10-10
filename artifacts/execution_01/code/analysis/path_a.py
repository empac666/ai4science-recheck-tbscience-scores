"""Path A: fresh Decimal JSON parse, direct task -> trial integer accumulation.

No counting code or intermediate rows are imported from path B or feasibility.
"""
import json
from decimal import Decimal
from .constants import DATASET, DOMAINS, LEADERBOARD, SYSTEMS


def count(path):
    document = json.loads(path.read_bytes(), parse_float=Decimal)
    board = document['leaderboard']
    if board['id'] != LEADERBOARD or board['name'] != 'v0-1-eval' or board['dataset_version_ids'] != [DATASET]:
        raise ValueError('A: leaderboard identity mismatch')
    tasks = {}
    domain_sizes = dict.fromkeys(DOMAINS, 0)
    for task in document['task_matrix']['tasks']:
        if task['id'] in tasks or task['domain'] not in domain_sizes:
            raise ValueError('A: duplicate task or unknown domain')
        tasks[task['id']] = task['domain']
        domain_sizes[task['domain']] += 1
    if len(tasks) != 70 or domain_sizes != DOMAINS:
        raise ValueError('A: task universe mismatch')
    output = {}
    for name, (rid, model, agent, _, _) in SYSTEMS.items():
        rows = [r for r in document['rows'] if r['id'] == rid]
        if len(rows) != 1:
            raise ValueError('A: row not unique')
        row = rows[0]
        if row['leaderboard_id'] != LEADERBOARD or (row['metadata']['model_display']['label'], row['metadata']['agent_display']['label'], row['metadata']['reasoning_effort']) != (model, agent, 'max'):
            raise ValueError('A: row identity/configuration mismatch')
        cells = document['task_matrix']['rows'][rid]
        if set(cells) != set(tasks):
            raise ValueError('A: cell universe mismatch')
        K = N = 0
        seen = set()
        by_task, by_job, task_jobs = {}, {}, []
        for tid in sorted(tasks):
            cell = cells[tid]
            if len(cell['trials']) != 3:
                raise ValueError('A: not three trials')
            k = n = 0
            cell_jobs = set()
            for trial in cell['trials']:
                if type(trial['solved']) is not bool or not isinstance(trial['id'], str) or not trial['id'] or trial['id'] in seen:
                    raise ValueError('A: nonboolean or duplicate/invalid trial')
                job = trial['job']
                if not isinstance(job, str) or not job or job in cell_jobs:
                    raise ValueError('A: invalid/repeated job in task')
                seen.add(trial['id'])
                cell_jobs.add(job)
                y = int(trial['solved'])
                K += y
                N += 1
                k += y
                n += 1
                record = by_job.setdefault(job, {'K': 0, 'N': 0, 'tasks': []})
                record['K'] += y
                record['N'] += 1
                record['tasks'].append(tid)
                task_jobs.append({'system': name, 'row_id': rid, 'task_id': tid, 'domain': tasks[tid], 'job_id': job, 'trial_id': trial['id'], 'K': y, 'N': 1})
            if type(cell['solved']) is not int or type(cell['total']) is not int or (cell['solved'], cell['total']) != (k, n):
                raise ValueError('A: cell summary mismatch')
            by_task[tid] = {'K': k, 'N': n, 'domain': tasks[tid]}
        if len(by_job) != 3 or any(j['N'] != 70 or set(j['tasks']) != set(tasks) for j in by_job.values()):
            raise ValueError('A: job universe mismatch')
        if type(row['n_trials']) is not int or row['n_trials'] != N or type(row['metrics']['passes']) is not int or type(row['metrics']['tasks']) is not int or (row['metrics']['passes'], row['metrics']['tasks']) != (K, N):
            raise ValueError('A: row summary mismatch')
        output[name] = {'K': K, 'N': N, 'tasks': by_task, 'jobs': by_job, 'task_jobs': task_jobs, 'row': row}
    return output
