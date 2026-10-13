"""Locked Decimal checks, sensitivity summaries and paired task resampling."""
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_DOWN, localcontext
from fractions import Fraction
from .constants import DOMAINS
from tools.audit_rules import raw_percentage, one_decimal, split_display_accuracy

ALGORITHMS = (ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN)


def official(a, b):
    out = {}
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 50, ROUND_HALF_EVEN
        for name, record in a.items():
            K, N, row = record['K'], record['N'], record['row']
            percent = Decimal(K) / Decimal(N) * 100
            front, back = split_display_accuracy(row['metrics']['display_accuracy'])
            checks = {'paths_equal': (K, N) == (b[name]['K'], b[name]['N']),
                      'per_task_paths_equal': all(t['K'] == b[name]['tasks'][tid] for tid, t in record['tasks'].items()),
                      'per_job_paths_equal': all((j['K'], j['N']) == (b[name]['jobs'][jid]['K'], b[name]['jobs'][jid]['N']) for jid, j in record['jobs'].items()),
                      'accuracy_within_tolerance': abs(Decimal(row['metrics']['accuracy']) - percent) <= Decimal('1e-10'),
                      'display_matches': front == one_decimal(str(percent))}
            p = Decimal(K) / N
            se = 100 * (p * (1-p) / N).sqrt()
            original_se = str(row['metrics']['accuracy_stderr'])
            se_check = {'computed': str(se), 'original': original_se, 'computed_one_decimal': one_decimal(str(se)),
                        'original_one_decimal': one_decimal(original_se), 'display': back,
                        'matches': one_decimal(str(se)) == one_decimal(original_se) == back}
            float_checks = {}
            for label, f in [('count_float', float(K)/210*100), ('accuracy_float', float(row['metrics']['accuracy']))]:
                value = Decimal.from_float(f)
                float_checks[label] = {'binary_decimal': str(value), 'difference_pp': str(value-percent), 'algorithms': {}}
                for alg in ALGORITHMS:
                    f_display = format(value.quantize(Decimal('.1'), rounding=alg), 'f')
                    d_display = format(percent.quantize(Decimal('.1'), rounding=alg), 'f')
                    float_checks[label]['algorithms'][alg] = {'float': f_display, 'decimal': d_display, 'matches': f_display == d_display}
            task_mean = sum((Fraction(t['K'],3) for t in record['tasks'].values()), Fraction()) / 70 * 100
            trial_mean = Fraction(100*K, N)
            out[name] = {'K': K, 'N': N, 'integer_ratio': f'{K}/{N}', 'percentage_decimal50': raw_percentage(K,N),
                         'percentage_one_decimal': one_decimal(str(percent)), 'verdict': '一致' if all(checks.values()) else '不一致',
                         'checks': checks, 'reported_accuracy': str(row['metrics']['accuracy']), 'display_accuracy': row['metrics']['display_accuracy'],
                         'stderr': se_check, 'float_checks': float_checks,
                         'weighting_identity': {'task_mean_exact': str(task_mean), 'trial_mean_exact': str(trial_mean), 'matches': task_mean == trial_mean}}
    return out


def sensitivities(records):
    out = {}
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 50, ROUND_HALF_EVEN
        for name, record in records.items():
            domains = {}
            for domain in DOMAINS:
                group = [t for t in record['tasks'].values() if t['domain'] == domain]
                k, n = sum(t['K'] for t in group), sum(t['N'] for t in group)
                reported = record['row']['metrics']['domain_metrics'][domain]
                pct = Decimal(k)/n*100
                domains[domain] = {'K': k, 'N': n, 'tasks': len(group), 'percentage': str(pct),
                                   'official_counts_match': (reported['passes'],reported['tasks']) == (k,n),
                                   'official_accuracy_matches': abs(Decimal(reported['accuracy'])-pct) <= Decimal('1e-10')}
            eq = sum((Fraction(100*d['K'],d['N']) for d in domains.values()),Fraction())/5
            jobs = {j: {'K': r['K'], 'N': r['N'], 'percentage': str(Decimal(r['K'])/r['N']*100)} for j,r in sorted(record['jobs'].items())}
            job_mean = sum((Fraction(100*j['K'],j['N']) for j in jobs.values()),Fraction())/3
            solved_any = sum(t['K'] >= 1 for t in record['tasks'].values())
            out[name] = {'domains': domains, 'five_domain_equal_weight_exact': str(eq), 'five_domain_equal_weight_percentage': str(Decimal(eq.numerator)/eq.denominator),
                         'jobs': jobs, 'three_job_mean_exact': str(job_mean),
                         'pass_at_3': {'K_tasks': solved_any, 'N_tasks':70, 'percentage': str(Decimal(solved_any)/70*100)}}
    return out


def bootstrap(records, version_matches):
    spec = {'replicates': 10000, 'rng': 'Generator(PCG64)', 'percentile_method': 'linear',
            'primary_seed': 2026101001, 'stratified_seed': 2026101002,
            'primary_design': 'non-stratified task clusters, 70 draws, paired systems',
            'stratified_design': 'earth/engineering/life/mathematical/physical, original domain sizes, paired systems'}
    if not version_matches:
        return {**spec, 'status': 'stopped_version_mismatch', 'primary': None, 'stratified_sensitivity': None}
    import numpy as np
    names = ['Astra','Fable']
    tids = sorted(records['Astra']['tasks'])
    successes = np.array([[records[s]['tasks'][t]['K'] for s in names] for t in tids],dtype=np.int64)
    def summarize(samples):
        difference = samples[:,0]-samples[:,1]
        return {**{s: np.percentile(samples[:,i],[2.5,97.5],method='linear').tolist() for i,s in enumerate(names)},
                'Astra_minus_Fable_pp': np.percentile(difference,[2.5,97.5],method='linear').tolist()}
    rng = np.random.Generator(np.random.PCG64(2026101001))
    main = np.empty((10000,2))
    for iteration in range(10000):
        indices = rng.integers(0,70,size=70)
        main[iteration] = successes[indices].sum(axis=0)/210*100
    rng = np.random.Generator(np.random.PCG64(2026101002))
    groups = [[i for i,t in enumerate(tids) if records['Astra']['tasks'][t]['domain'] == d] for d in DOMAINS]
    stratified = np.empty((10000,2))
    for iteration in range(10000):
        indices = []
        for group in groups:
            draw = rng.integers(0,len(group),size=len(group))
            indices.extend(group[int(i)] for i in draw)
        stratified[iteration] = successes[indices].sum(axis=0)/210*100
    import hashlib
    return {**spec, 'status': 'completed', 'primary': summarize(main), 'stratified_sensitivity': summarize(stratified),
            'replicate_sha256': {'primary': hashlib.sha256(main.astype('<f8').tobytes()).hexdigest(),
                                 'stratified': hashlib.sha256(stratified.astype('<f8').tobytes()).hexdigest()},
            'replicate_digest_format': '10000 by 2 little-endian float64 percentages, Astra then Fable, C order'}


def display_overlap(x_text, y_text):
    """All allowed same-algorithm inverse-image intersections, clipped to [0,100]."""
    def interval(text, algorithm):
        x = Decimal(text)
        h = Decimal(1).scaleb(-len(text.partition('.')[2]))
        if algorithm == ROUND_DOWN:
            lower, upper, left, right = x, x+h, True, False
        else:
            lower, upper = x-h/2, x+h/2
            even = int(x/h) % 2 == 0
            left, right = (True,False) if algorithm == ROUND_HALF_UP else (even,even)
        if lower < 0: lower,left = Decimal(0),True
        if upper > 100: upper,right = Decimal(100),True
        return lower,upper,left,right
    result = {}
    with localcontext() as ctx:
        ctx.prec,ctx.rounding = 50,ROUND_HALF_EVEN
        for alg in ALGORITHMS:
            a,b = interval(x_text,alg),interval(y_text,alg)
            low, high = max(a[0],b[0]),min(a[1],b[1])
            left = (a[0] != low or a[2]) and (b[0] != low or b[2])
            right = (a[1] != high or a[3]) and (b[1] != high or b[3])
            result[alg] = {'x_interval': [str(a[0]),str(a[1]),a[2],a[3]], 'y_interval': [str(b[0]),str(b[1]),b[2],b[3]],
                           'intersects': low < high or (low == high and left and right)}
    return result
