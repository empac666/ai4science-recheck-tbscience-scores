import copy
import json
import tempfile
import unittest
from decimal import Decimal, localcontext
from pathlib import Path
from analysis import path_a, path_b
from analysis.constants import DATASET, DOMAINS, LEADERBOARD, MIRROR_URL, PROVENANCE_TEXT, SYSTEMS
from analysis.sources import aa_summary_score, classify, fact, mirrors, missing_fields, pdf_section_87
from analysis.statistics import bootstrap, display_overlap, official, sensitivities
from tools.audit_rules import compatible_numerators, one_decimal, split_display_accuracy


def fixture():
    tasks=[]
    for domain,size in DOMAINS.items():
        for i in range(size):tasks.append({'id':f'{domain}-{i:02d}','domain':domain})
    doc={'leaderboard':{'id':LEADERBOARD,'name':'v0-1-eval','dataset_version_ids':[DATASET]},'rows':[],
         'task_matrix':{'tasks':tasks,'rows':{}}}
    for system,(rid,model,agent,_,_) in SYSTEMS.items():
        cells={}
        for i,task in enumerate(tasks):
            trials=[{'id':f'{system}-{i}-{j}','job':f'job-{j}','solved':(i+j)%4==0} for j in range(3)]
            cells[task['id']]={'solved':sum(t['solved'] for t in trials),'total':3,'trials':trials}
        k=sum(c['solved'] for c in cells.values())
        with localcontext() as ctx:
            ctx.prec=50
            p=Decimal(k)/210
            se=100*(p*(1-p)/210).sqrt()
            metrics={'passes':k,'tasks':210,'accuracy':float(p*100),'accuracy_stderr':float(se),
                     'display_accuracy':f'**{one_decimal(str(p*100))}%** +/- {one_decimal(str(se))}%','domain_metrics':{}}
            for domain in DOMAINS:
                group=[cells[t['id']] for t in tasks if t['domain']==domain]
                dk,dn=sum(t['solved'] for t in group),len(group)*3
                metrics['domain_metrics'][domain]={'passes':dk,'tasks':dn,'accuracy':float(Decimal(dk)/dn*100)}
        doc['rows'].append({'id':rid,'leaderboard_id':LEADERBOARD,'metadata':{'model_display':{'label':model},'agent_display':{'label':agent},'reasoning_effort':'max'},
                            'metrics':metrics,'n_trials':210})
        doc['task_matrix']['rows'][rid]=cells
    return doc


class CountingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'synthetic.json';self.doc=fixture()
    def tearDown(self):self.tmp.cleanup()
    def write(self):self.path.write_text(json.dumps(self.doc),encoding='utf-8')
    def test_independent_counts_and_pairing(self):
        self.write();a=path_a.count(self.path);b=path_b.count(self.path)
        for system in SYSTEMS:
            self.assertEqual(a[system]['K'],b[system]['K']);self.assertEqual(a[system]['N'],210)
            self.assertEqual({t:d['K'] for t,d in a[system]['tasks'].items()},b[system]['tasks'])
        checks=official(a,b)
        self.assertTrue(all(r['verdict']=='一致' and r['stderr']['matches'] and r['weighting_identity']['matches'] for r in checks.values()))
        self.assertTrue(all(d['official_counts_match'] for r in sensitivities(a).values() for d in r['domains'].values()))
        first=bootstrap(a,True);second=bootstrap(a,True)
        self.assertEqual(first,second)
        self.assertEqual(first['primary']['Astra_minus_Fable_pp'],[0.,0.])
        self.assertEqual(first['stratified_sensitivity']['Astra_minus_Fable_pp'],[0.,0.])
        self.assertIsNone(bootstrap(a,False)['primary'])
    def assert_rejected(self,mutation):
        self.doc=fixture();mutation(self.doc);self.write()
        for module in [path_a,path_b]:
            with self.subTest(path=module.__name__):
                with self.assertRaises((ValueError,KeyError)):module.count(self.path)
    def test_rejects_nonboolean(self):
        rid=SYSTEMS['Astra'][0]
        self.assert_rejected(lambda d: next(iter(d['task_matrix']['rows'][rid].values()))['trials'][0].update(solved=1))
    def test_rejects_duplicate_trial(self):
        rid=SYSTEMS['Astra'][0]
        def mutation(d):
            cells=list(d['task_matrix']['rows'][rid].values());cells[1]['trials'][0]['id']=cells[0]['trials'][0]['id']
        self.assert_rejected(mutation)
    def test_rejects_duplicate_task_job(self):
        rid=SYSTEMS['Astra'][0]
        def mutation(d):
            trials=next(iter(d['task_matrix']['rows'][rid].values()))['trials'];trials[1]['job']=trials[0]['job']
        self.assert_rejected(mutation)
    def test_rejects_missing_task(self):
        rid=SYSTEMS['Astra'][0]
        self.assert_rejected(lambda d:d['task_matrix']['rows'][rid].pop(next(iter(d['task_matrix']['rows'][rid]))))
    def test_rejects_bad_cell_summary(self):
        rid=SYSTEMS['Astra'][0]
        self.assert_rejected(lambda d:next(iter(d['task_matrix']['rows'][rid].values())).update(solved=99))
    def test_rejects_duplicate_task_id(self):
        self.assert_rejected(lambda d:d['task_matrix']['tasks'].append(copy.deepcopy(d['task_matrix']['tasks'][0])))
    def test_rejects_wrong_evaluation(self):
        self.assert_rejected(lambda d:d['leaderboard'].update(id='other'))
    def test_rejects_metrics_boolean(self):
        self.assert_rejected(lambda d:d['rows'][0]['metrics'].update(passes=True))


class DecimalAndSourceTests(unittest.TestCase):
    def test_summary_score_bound_to_target_model(self):
        summary='GPT-6 Astra (Max) scores the highest on Terminal-Bench-Science 0.1 with a score of 63.3%, followed by Another Model with a score of 61.9% and Third Model with a score of 59.0%'
        self.assertEqual(aa_summary_score(summary),'63.3')
        with self.assertRaises(ValueError):aa_summary_score('Another Model with a score of 63.3%')
    def test_pdf_body_heading_excludes_contents(self):
        text='Contents\n8.7 Terminal-Bench-Science 0.1       171\n\n8.7 Terminal-Bench-Science 0.1\n\nbody text\n8.8 Another section\nnot part of target\n'
        self.assertEqual(pdf_section_87(text),'body text')
        with self.assertRaises(ValueError):pdf_section_87(text+'\n8.7 Terminal-Bench-Science 0.1\nother body')
    def test_literal_delimiter_and_trailing_zero(self):
        self.assertEqual(split_display_accuracy(' **40.0%** +/- 3.4% '),('40.0','3.4'))
        for text in ['40.0 ± 3.4','40 +/- 3 +/- 4','-1 +/- 2','40 +/- nan','40 +/-','1e2 +/- 2']:
            with self.assertRaises(ValueError):split_display_accuracy(text)
        self.assertEqual(one_decimal('40'),'40.0');self.assertEqual(one_decimal('2.25'),'2.3')
    def test_enumeration_endpoint_and_empty_set(self):
        self.assertEqual(compatible_numerators('13',8),[1]) # 12.5 inclusive lower endpoint
        self.assertEqual(compatible_numerators('12',8),[]) # 12.5 exclusive upper endpoint
        self.assertEqual(compatible_numerators('0.1',3),[])
        self.assertEqual(compatible_numerators('0.0',3),[0])
        self.assertEqual(compatible_numerators('100.0',3),[3])
        with self.assertRaises(ValueError):compatible_numerators('40',True)
    def test_inverse_images_same_algorithm(self):
        overlaps=display_overlap('63','63.3')
        self.assertEqual(set(overlaps),{'ROUND_HALF_UP','ROUND_HALF_EVEN','ROUND_DOWN'})
        self.assertTrue(all(r['intersects'] for r in overlaps.values()))
        self.assertFalse(any(r['intersects'] for r in display_overlap('40.0','52.6').values()))
        self.assertEqual(display_overlap('0.0','0.0')['ROUND_HALF_UP']['x_interval'][0],'0')
    def test_missing_identity_wins_over_known_difference(self):
        fields=missing_fields();fields['trials']=fact('10 trials per task (700 trials)','与官方不同')
        self.assertEqual(classify(fields,'completed')['first_priority'],1)
        self.assertEqual(classify(fields,'extraction_failed')['label'],'来源未完整披露')
    def test_mirror_strict_metadata_and_quantization(self):
        with tempfile.TemporaryDirectory() as folder:
            cache=Path(folder)
            provenance={'kind':'mirror','total':17,'text':PROVENANCE_TEXT,'sourceUrl':MIRROR_URL}
            rows=[{'sourceModelId':x[3],'model':x[4],'harness':x[2],'reasoningEffort':'max','externalUrl':MIRROR_URL,'score':40} for x in SYSTEMS.values()]
            doc={'props':{'pageProps':{'leaderboard':rows,'trustCard':{'provenance':provenance},'lastUpdated':'test'}}}
            def write(): (cache/'benchlm_science.html').write_text('<script id="__NEXT_DATA__" type="application/json">'+json.dumps(doc)+'</script>')
            official={s:{'reported_accuracy':'40.0'} for s in SYSTEMS}
            write();result=mirrors(cache,official)
            self.assertTrue(all(r['verdict']=='一致' for r in result.values()))
            self.assertEqual(result['Fable']['score_raw_string'],'40')
            provenance['extra']='unexpected';write()
            self.assertTrue(all(r['verdict']=='不一致' for r in mirrors(cache,official).values()))
            del provenance['extra'];rows[0]['externalUrl']=MIRROR_URL.rstrip('/');write()
            self.assertEqual(mirrors(cache,official)['Astra']['verdict'],'不一致')
            (cache/'benchlm_science.html').write_text('<html/>')
            self.assertTrue(all(r['verdict']=='镜像无法抽取' for r in mirrors(cache,official).values()))


if __name__=='__main__':unittest.main()
