"""Run the locked audit against a read-only external input cache.

Usage: python3 -m analysis.run --cache ../data_cache
Freeze all analysis, test and rule code with analysis.freeze before execution.
"""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP, localcontext
from pathlib import Path
from . import path_a, path_b
from .constants import LOCK, RELEASE_COMMIT
from .environment import now, verify_code, verify_inputs, versions
from .outputs import csv_write, drafts, figure, report, write_tables
from .predictions import ENUMERATION_SPEC, PREDICTIONS
from .sources import extract, mirrors, objects_in_rsc, rsc_text, unique
from .statistics import bootstrap, display_overlap, official, sensitivities
from tools.audit_rules import compatible_numerators, one_decimal, raw_percentage


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=lambda x: str(x) if isinstance(x,Decimal) else (_ for _ in ()).throw(TypeError(type(x).__name__)))+'\n',encoding='utf-8')


def ap(result,key,observed,matches,status='completed',deviation=None):
    result['audit_predictions'][key]={'prediction':PREDICTIONS[key],'observed':observed,'matches':bool(matches),
                                       'status':status if matches or status=='extraction_failed' else 'prediction_mismatch',
                                       'deviation':deviation if deviation else (None if matches else 'Extraction failed' if status=='extraction_failed' else 'Observed result differs from frozen audit prediction; item interpretation stopped')}


def stop(root,result,reason):
    result.update(status='stopped',stop_reason=reason,finished_at_utc=now())
    save(root/'results.json',result)
    (root/'REPORT.md').write_text('审计未完成 / Audit incomplete.\n\n'+reason+'\n',encoding='utf-8')
    with (root/'DEVIATIONS.md').open('a',encoding='utf-8') as f:f.write('\nExecution stop: '+reason+'\n')
    raise SystemExit(1)


def supporting_checks(cache):
    from bs4 import BeautifulSoup
    tree=json.loads((cache/'tb_tree_v01.json').read_bytes())
    tag=json.loads((cache/'tb_tag.json').read_bytes())
    paths=[x['path'] for x in tree['tree'] if x['path'].endswith('/task.toml')]
    names={p.split('/')[-2] for p in paths}
    doc=json.loads((cache/'science_board_v01.json').read_bytes())
    tasks={t['id'] for t in doc['task_matrix']['tasks']}
    version={'tag_commit':tag['object']['sha'],'tree_commit':tree['sha'],'release_commit_matches':tag['object']['sha']==tree['sha']==RELEASE_COMMIT,
             'unique_task_toml_count':len(names),'task_names_match':names==tasks,'task_byte_identity_verified':False}
    sample_text=rsc_text(BeautifulSoup((cache/'science_trial_sample.html').read_bytes(),'html.parser'))
    candidates=[o for o in objects_in_rsc(sample_text) if o.get('id')=='0156fedf-e8cc-5e04-bf3f-7b9e1aa435ff' and 'config' in o]
    sample=unique(candidates,'Astra trial sample')
    config=sample['lock']
    example={'trial_id':sample['id'],'codex_version':config['agent']['kwargs']['version'],
             'verifier_disable':config['verifier']['disable'],'environment_mode':config['verifier']['environment_mode'],
             'timeout_multiplier':config['timeout_multiplier'],'scope':'one Astra trial only; no system-wide inference; no labels depend on these fields',
             'Fable_detail_http_status':404}
    return {'release_and_task_names':version,'single_trial_example':example,
            'current_Vals_background':{'Fable_40_00':'数值相同、运行身份未建立','used_as_mirror':False,'used_to_fill_history':False,
                                       'basis':'already disclosed feasibility background; not an endpoint'},
            'tb_news_used_in_endpoints':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,default=Path('../data_cache'))
    args=parser.parse_args()
    root=Path('.')
    for folder in ['artifacts','figures']:(root/folder).mkdir(exist_ok=True)
    result={'protocol_lock_commit':LOCK,'started_at_utc':now(),'status':'running','audit_predictions':{}}
    result['code_freeze']=verify_code(root)
    manifest,input_checks=verify_inputs(root,args.cache)
    save(root/'artifacts/input_verification.json',input_checks)
    csv_write(root/'artifacts/input_verification.csv',input_checks['checks'])
    if not input_checks['all_match']:stop(root,result,'Input byte/hash verification failed; affected computations stopped')
    software=versions();save(root/'artifacts/software_versions.json',software)
    result['software_versions']=software
    deviations=[]
    history_file=root/'artifacts/execution_history.json'
    if history_file.exists():
        history=json.loads(history_file.read_text())
        result['execution_history']=history
        deviations.extend([
            '实现修正与重执行：首轮 S1a 与 S5 提取失败，AP-07/AP-10/AP-12/AP-17 的 observed=null、matches=false；受影响项解释停止，其他独立结果保留。',
            'AA 原正则匹配了同一最内层摘要中后续模型的分数；修正为把分数绑定到 GPT-6 Astra (Max)。PDF 原定位同时命中目录和正文；修正为 pdftotext -layout 的独立 §8.7 正文标题，再核对同一句。冻结文件、节点路径、预测、阈值与分母均未改变。',
            '首轮代码、哈希、results.json、来源表及执行元数据完整保存于 artifacts/execution_01/；详见 artifacts/execution_history.json。最终执行代码已另行冻结后重执行；这是看过首轮结果后的实现修正，不声称盲态。',
            '首轮自动生成报告曾错误宣称全部 AP 完成，现已由明确反映实际状态的最终 REPORT.md 取代；首轮诊断记录不删除。',
            'Implementation corrections after an observed first execution are documented. No scientific protocol, input, extraction-node specification, prediction, threshold, denominator or seed changed. Original failures and original code are retained; the corrected code was frozen before re-execution.',
        ])
    for key,matches in software['matches'].items():
        if not matches:deviations.append(f"Version mismatch: {key}: expected {software['locked'][key]}, actual {software['actual'][key]}; protocol downgrade applied")
    (root/'DEVIATIONS.md').write_text('# Execution deviations / 执行偏离\n\n'+ ('\n'.join(deviations) if deviations else '无执行偏离：全部冻结输入与五项软件版本相符；协议、阈值、分母和冻结提取路径保持原样。\n\nNo execution deviations. All input hashes and locked software versions match. Known baseline exposure is disclosed in the locked protocol and is not a new deviation.')+'\n',encoding='utf-8')
    counts={}
    errors={}
    # Each path reads independently even if the other path fails.
    for name,module in [('A',path_a),('B',path_b)]:
        try:counts[name]=module.count(args.cache/'science_board_v01.json')
        except (ValueError,KeyError,TypeError) as err:errors[name]=str(err)
    if errors:
        result['count_diagnostics']={'errors':errors,'completed_path_totals':{p:{s:{'K':d['K'],'N':d['N']} for s,d in c.items()} for p,c in counts.items()}}
        stop(root,result,'Eligibility validation failed; successful path retained in diagnostics')
    a,b=counts['A'],counts['B']
    result['count_paths']={p:{s:{'K':d['K'],'N':d['N']} for s,d in c.items()} for p,c in counts.items()}
    for name,key in [('Astra','AP-01'),('Fable','AP-02')]:
        observed={p:{'K':counts[p][name]['K'],'N':counts[p][name]['N']} for p in ['A','B']}
        observed['display']=one_decimal(raw_percentage(a[name]['K'],a[name]['N']))
        ap(result,key,observed,observed==PREDICTIONS[key])
    if not all(result['audit_predictions'][key]['matches'] for key in ['AP-01','AP-02']):stop(root,result,'AP-01/02 count deviation: all subsequent analyses stopped')
    off=official(a,b);result['official']=off
    observed={s:off[s]['stderr']['display'] for s in ['Astra','Fable']}
    observed['three_way_equal']=all(off[s]['stderr']['matches'] for s in off)
    ap(result,'AP-03',{'summary':observed,'checks':{s:off[s]['stderr'] for s in off}},observed==PREDICTIONS['AP-03'])
    identities={s:off[s]['weighting_identity'] for s in off}
    ap(result,'AP-04',identities,{s:d['matches'] for s,d in identities.items()}==PREDICTIONS['AP-04'])
    mirror=mirrors(args.cache,off);result['mirrors']=mirror
    for name,key in [('Astra','AP-05'),('Fable','AP-06')]:
        ok=mirror[name]['status']=='completed'
        ap(result,key,mirror[name] if ok else None,ok and mirror[name]['verdict']==PREDICTIONS[key],status='completed' if ok else 'extraction_failed')
    claims=extract(args.cache,manifest,off,software['matches']['pdftotext']);result['claims']=claims
    for sid,key in [('S1a','AP-07'),('S2','AP-08'),('S3','AP-09'),('S5','AP-10'),('S6','AP-11')]:
        c=claims[sid];ok=c['status']=='completed'
        observed={'facts':c['facts'],'identity_evidence':c.get('identity_evidence'),'classification':c['classification'],'source':c['source']} if ok else None
        ap(result,key,observed,ok and c['main_label']==PREDICTIONS[key],status='completed' if ok else 'extraction_failed')
    enumeration=[]
    for key,sid,N,qualification in ENUMERATION_SPEC:
        c=claims[sid];ok=c['status']=='completed'
        x=c['display'];d=len(x.partition('.')[2])
        values=compatible_numerators(x,N) if ok else None
        item={'record':sid,'x':x,'d':d,'N':N,'denominator_qualification':qualification,'numerators':values,
              'status':'completed' if ok else 'extraction_failed','same_document_N':c.get('N_same_document')}
        enumeration.append(item)
        ap(result,key,item if ok else None,ok and values==PREDICTIONS[key],status='completed' if ok else 'extraction_failed')
    result['rational_compatibility']=enumeration
    result['not_reconstructed']={'S1':'N unknown; original unread','S2':'N unknown; rendered source only'}
    result['rounding_inverse_images']={'S1_vs_S1a_existence_only':display_overlap('63','63.3'),
            **{sid+'_vs_official':display_overlap(claims[sid]['display'],off[claims[sid]['system']]['percentage_one_decimal']) for sid in ['S1a','S2','S3','S5','S6'] if claims[sid]['status']=='completed'},
            'scope':'allowed display algorithms only; does not explain unidentified external runs or unread S1'}
    if claims['S1a']['status']=='completed' and result['audit_predictions']['AP-12']['matches']:
        with localcontext() as ctx:
            ctx.prec,ctx.rounding=50,ROUND_HALF_EVEN
            embedded=Decimal(claims['S1a']['embedded_ratio'])
            numerator=result['rational_compatibility'][0]['numerators'][0]
            true_ratio=Decimal(numerator)/210
            num,den=embedded.as_integer_ratio()
            result['AA_embedded_ratio_check']={'raw':str(embedded),'compatible_numerator':numerator,
                    'same_half_up_15_places':embedded.quantize(Decimal('1e-15'),rounding=ROUND_HALF_UP)==true_ratio.quantize(Decimal('1e-15'),rounding=ROUND_HALF_UP),
                    'exactly_equal_by_integer_cross_product':num*210==numerator*den,
                    'left_cross_product':num*210,'right_cross_product':numerator*den,
                    'not_used_to_explain_S1':True}
    result['sensitivity']=sensitivities(a)
    result['bootstrap']=bootstrap(a,software['matches']['python'] and software['matches']['numpy'])
    result['official_difference_pp']=raw_percentage(a['Astra']['K']-a['Fable']['K'],210)
    result['supporting_checks']=supporting_checks(args.cache)
    seven=[claims[f'S{i}'] for i in range(1,8)]
    result['seven_claim_label_counts']=dict(Counter(c['main_label'] for c in seven))
    result['primary_support_count']=sum(c['source']['primary_support'] for c in seven)
    result['primary_support_denominator']=7
    result['no_model_reruns']=True
    result['uncompleted_items']=['S1 original unread','S2 original HTTP403','external trial records and run identities unavailable',
                                'complete task-byte identity and grading not verified','Fable trial detail HTTP404','first-public-push event timestamp not independently recovered']
    result['status']='completed' if all(x['matches'] for x in result['audit_predictions'].values()) else 'completed_with_stopped_items'
    result['finished_at_utc']=now()
    write_tables(root,a,claims,result['sensitivity'])
    figure(root,result);report(root,result);drafts(root,result)
    save(root/'results.json',result)
    # Detect changes during execution; retain pre-execution freeze separately.
    verify_code(root)
    save(root/'artifacts/execution.json',{'started_at_utc':result['started_at_utc'],'finished_at_utc':result['finished_at_utc'],
              'code_freeze_time_utc':result['code_freeze']['frozen_at_utc'],'status':result['status'],'all_AP_matches':all(x['matches'] for x in result['audit_predictions'].values()),
              'no_network_in_analysis':True,'cache_writes':False,'code_verified_before_and_after':True})
    print(json.dumps({'status':result['status'],'counts':result['count_paths'],'official':{s:off[s]['verdict'] for s in off},
                      'mirrors':{s:mirror[s]['verdict'] for s in mirror},'labels':result['seven_claim_label_counts'],'primary_support':result['primary_support_count']},ensure_ascii=False))


if __name__=='__main__':main()
