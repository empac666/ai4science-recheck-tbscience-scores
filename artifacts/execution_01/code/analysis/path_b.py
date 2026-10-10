"""Path B: independent fresh parse and job -> task accumulation.

Validation and summation are written independently of path A. Only locked IDs
are shared; no computed counts, counting function, or feasibility code is used.
"""
import json
from decimal import Decimal
from .constants import DATASET, DOMAINS, LEADERBOARD, SYSTEMS


def count(path):
    raw = json.loads(path.read_text(encoding='utf-8'), parse_float=Decimal)
    if raw['leaderboard']['id'] != LEADERBOARD or raw['leaderboard']['name'] != 'v0-1-eval' or raw['leaderboard']['dataset_version_ids'] != [DATASET]:
        raise ValueError('B: unexpected evaluation')
    ids = [t['id'] for t in raw['task_matrix']['tasks']]
    if len(ids) != 70 or len(set(ids)) != 70:
        raise ValueError('B: invalid task IDs')
    task_domains = {t['id']: t['domain'] for t in raw['task_matrix']['tasks']}
    if {d: list(task_domains.values()).count(d) for d in DOMAINS} != DOMAINS:
        raise ValueError('B: domain distribution mismatch')
    result = {}
    for system in SYSTEMS:
        rid, model, harness, _, _ = SYSTEMS[system]
        candidates = tuple(r for r in raw['rows'] if r['id'] == rid)
        if len(candidates) != 1:
            raise ValueError('B: missing/duplicate row')
        row = candidates[0]
        metadata = row['metadata']
        if row['leaderboard_id'] != LEADERBOARD or metadata['model_display']['label'] != model or metadata['agent_display']['label'] != harness or metadata['reasoning_effort'] != 'max':
            raise ValueError('B: wrong row metadata')
        matrix = raw['task_matrix']['rows'][rid]
        if set(matrix.keys()) != set(ids):
            raise ValueError('B: incomplete matrix')
        grouped = {}
        trial_ids = []
        for task_id, entry in matrix.items():
            if len(entry['trials']) != 3:
                raise ValueError('B: wrong cell length')
            for item in entry['trials']:
                if type(item['solved']) != bool or not isinstance(item['id'], str) or not item['id']:
                    raise ValueError('B: invalid trial')
                trial_ids.append(item['id'])
                job_id = item['job']
                if not isinstance(job_id, str) or not job_id:
                    raise ValueError('B: invalid job')
                bucket = grouped.setdefault(job_id, {})
                if task_id in bucket:
                    raise ValueError('B: duplicate task/job')
                bucket[task_id] = item['solved']
        if len(trial_ids) != len(set(trial_ids)) or len(grouped) != 3:
            raise ValueError('B: nonunique trials or wrong number of jobs')
        successes = observations = 0
        task_counts = {t: 0 for t in ids}
        jobs = {}
        for job_id in sorted(grouped):
            bucket = grouped[job_id]
            if set(bucket) != set(ids) or len(bucket) != 70:
                raise ValueError('B: job does not cover task universe')
            job_k = job_n = 0
            for task_id in sorted(bucket):
                if bucket[task_id] is True:
                    successes += 1
                    job_k += 1
                    task_counts[task_id] += 1
                observations += 1
                job_n += 1
            jobs[job_id] = {'K': job_k, 'N': job_n}
        for task_id, entry in matrix.items():
            if type(entry['solved']) != int or entry['solved'] != task_counts[task_id] or type(entry['total']) != int or entry['total'] != 3:
                raise ValueError('B: cell counts disagree')
        if type(row['n_trials']) != int or row['n_trials'] != observations:
            raise ValueError('B: n_trials disagreement')
        for key, observed in [('passes', successes), ('tasks', observations)]:
            if type(row['metrics'][key]) != int or row['metrics'][key] != observed:
                raise ValueError('B: metrics count disagreement')
        result[system] = {'K': successes, 'N': observations, 'tasks': task_counts, 'jobs': jobs}
    return result
