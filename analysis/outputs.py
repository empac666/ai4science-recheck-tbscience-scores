"""Original aggregate artifacts, nine-point figure, bilingual report and drafts."""
import csv
import json
from collections import Counter
from decimal import Decimal
from .constants import LOCK, REPOSITORY


def csv_write(path, rows, fields=None):
    fields=fields or list(rows[0])
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(rows)


def write_tables(root, records, claims, sensitivity):
    task_rows=[];job_rows=[];task_job_rows=[];domain_rows=[]
    for system,record in records.items():
        for tid,t in sorted(record['tasks'].items()):task_rows.append({'system':system,'row_id':record['row']['id'],'task_id':tid,**t})
        for jid,j in sorted(record['jobs'].items()):job_rows.append({'system':system,'job_id':jid,'K':j['K'],'N':j['N'],'percentage':sensitivity[system]['jobs'][jid]['percentage']})
        task_job_rows.extend(sorted(record['task_jobs'],key=lambda r:(r['task_id'],r['job_id'])))
        for domain,d in sensitivity[system]['domains'].items():domain_rows.append({'system':system,'domain':domain,**d})
    for filename,rows in [('task_counts.csv',task_rows),('job_counts.csv',job_rows),('task_job_counts.csv',task_job_rows),('domain_counts.csv',domain_rows)]:csv_write(root/filename,rows)
    rows=[]
    for sid in ['S1','S2','S3','S4','S5','S6','S7','S1a']:
        c=claims[sid];s=c['source']
        row={'record':sid,'in_seven_claims':sid!='S1a','system':c['system'],'display_percent':c['display'],
             'main_label':c['main_label'],'extraction_status':c['status'],'comparison':c.get('comparison'),
             'primary_support':s['primary_support'],'url':s['url'],'source_file':s['file'],'sha256':s['sha256'],'http_status':s['http_status'],
             'extraction_path':s['extraction_path'],'hit_strings':json.dumps(s['hit_strings'],ensure_ascii=False),
             'date_field':json.dumps(s['date_field'],ensure_ascii=False),'date_type':s['date_type'],'fetched_at_utc':s['fetched_at_utc'],
             'same_document_N':c.get('N_same_document'),'public_version_literal':c.get('public_version_literal'),
             'partial_method_literals':json.dumps(c.get('partial_method_literals'),ensure_ascii=False),
             'first_priority':c.get('classification',{}).get('first_priority'),'missing_fields':json.dumps(c.get('classification',{}).get('missing_required_fields'),ensure_ascii=False)}
        for key,field in c['facts'].items():row[key+'_state']=field['state'];row[key+'_literal']=field['literal']
        rows.append(row)
    csv_write(root/'claims_table.csv',rows)


def figure(root,results):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels=[
        'S1 Astra 63 | X claim, original unread; N unknown',
        'S2 Astra 64.6 | OpenAI rendered; effort selection / N unknown',
        'S3 Astra 65.71 | Vals historical announcement; N unknown',
        'S4 Astra 68.1 | Official display; 70 tasks x 3 trials',
        'S5 Fable 52.6 | Anthropic PDF; 70 tasks x 10 trials',
        'S6 Fable 34.29 | Vals historical announcement; N unknown',
        'S7 Fable 40.0 | Official display; 70 tasks x 3 trials',
        'Recount Astra | Official public labels; 143 / 210',
        'Recount Fable | Official public labels; 84 / 210',
    ]
    values=[float(results['claims'][sid]['display']) for sid in ['S1','S2','S3','S4','S5','S6','S7']]
    values.extend(float(results['official'][s]['percentage_decimal50']) for s in ['Astra','Fable'])
    fig,ax=plt.subplots(figsize=(13,7.2))
    colors=['#727b87']*7+['#15735a']*2
    ax.scatter(values,range(9),c=colors,s=[65]*7+[110]*2,zorder=3)
    for i,value in enumerate(values):
        display=results['claims'][['S1','S2','S3','S4','S5','S6','S7'][i]]['display'] if i<7 else results['official'][['Astra','Fable'][i-7]]['percentage_one_decimal']
        ax.annotate(display+'%',(value,i),xytext=(8,0),textcoords='offset points',va='center',fontsize=10)
    ax.set_yticks(range(9),labels,fontsize=10);ax.invert_yaxis();ax.set_xlim(0,100)
    ax.set_xlabel('Reported percentage / recount of public trial labels (%)')
    ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    ax.spines[['top','right','left']].set_visible(False)
    ax.set_title('Terminal-Bench-Science: seven frozen claims and two official recounts',loc='left',fontsize=14,pad=16)
    fig.text(.02,.025,'Frozen source order; no new ranking. Different setups / unknown run identities. No model reruns.\nSources, dates and metric details: claims_table.csv + INPUTS_SHA256SUMS.',fontsize=10)
    fig.tight_layout(rect=(0,.09,1,1));fig.savefig(root/'figures/figure1.png',dpi=170,metadata={'Title':'Frozen Terminal-Bench-Science score reconciliation','Creator':'Original audit figure'});plt.close(fig)


def report(root,r):
    a,f=r['official']['Astra'],r['official']['Fable'];m=r['mirrors']
    sentence=f"对已公开的70任务×3次试次标签的独立对账重加总得到：Astra {a['K']}/210={a['percentage_decimal50']}%（一位展示{a['percentage_one_decimal']}%），Fable 5.1 {f['K']}/210={f['percentage_decimal50']}%（一位展示{f['percentage_one_decimal']}%）；对官方68.1%／40.0%的内部判定分别为{a['verdict']}／{f['verdict']}，BenchLM镜像判定分别为{m['Astra']['verdict']}／{m['Fable']['verdict']}；本审计未重跑模型，判定只针对榜单展示值的算术相符，不涉及grader、任务字节、科学结论或谁更强。"
    lines=[sentence,'',
           'This recount of released trial labels confirms the official displays: Astra 143/210 → 68.1%; Fable 5.1 84/210 → 40.0%. Both BenchLM rows match the frozen official values and every required provenance field. No models were rerun; no party is accused of wrongdoing.','',
           '这是对公开逐试次记录的重加总，不指控任何一方。已知基线曾在可行性查看中出现；AP 的相符只确认独立审计轨迹，不是未知发现。50 位 Decimal 字符串是计算近似，精确量由整数比给出。','',
           f"公开锁定：[提交 {LOCK}]({REPOSITORY}/commit/{LOCK})。协议与可行性文件未改；公开可访问性已核验，首次 push 的事件时间未独立恢复，不能用作者日期冒充。See [public_lock.json](artifacts/public_lock.json).",'',
           'A 直接按 task→trial 计数；B 从原始 JSON 重新解析并按 job→task 计数。两者不共享求和函数、不导入可行性脚本，逐任务、逐 job、总分子和分母全部相符。资格检查包括 70 唯一任务、五域 8/9/19/17/17、每 cell 三个 bool、系统内 trial 唯一、每 task 每 job 一条、三个 job 各 70 条及 cell/metrics/n_trials 字段。','',
           'Both independent implementations agree at task, job and total levels. All 14 frozen input byte counts and hashes match; only those cached inputs are used. Code hashes were frozen before formal execution. All five locked software versions match.','',
           '| Audit target / 审计项 | Result / 结果 |','|---|---|']
    for name in ['Astra','Fable']:
        s=r['official'][name]['stderr']
        lines.append(f"| {name} naive stderr | computed {s['computed']}; raw {s['original']}; both → {s['display']}, display matches |")
    lines.extend(['',
                  '作者的 ±3.2/±3.4 是朴素标准误展示，不是 95% CI。AP-04 使用有理数验证平衡设计下任务等权与试次等权恒等。有限冻结集合计数没有抽样误差；下列区间仅描述任务簇重采样。These intervals do not establish population representativeness, external-score significance, causal superiority, or grading validity.','',
                  '| Task-cluster bootstrap, percentage points / 任务簇区间 | Primary, non-stratified / 非分层主区间 | Stratified sensitivity / 分层敏感性 |',
                  '|---|---|---|'])
    boot=r['bootstrap']
    if boot['status']=='completed':
        for key in ['Astra','Fable','Astra_minus_Fable_pp']:
            p,s=boot['primary'][key],boot['stratified_sensitivity'][key]
            lines.append(f'| {key} | [{p[0]:.6f}, {p[1]:.6f}] | [{s[0]:.6f}, {s[1]:.6f}] |')
        lines.extend(['','各 10,000 次，PCG64 种子 2026101001／2026101002，linear 2.5%／97.5% 分位数；task id 字典序，两系统共用抽样索引。非分层主区间按跨域经验任务分布抽 70 个簇；分层按冻结域顺序及原域数抽样。Replicate hashes and exact numerical outputs are in [results.json](results.json).'])
    else:lines.extend(['',f"未完成 / Not completed: bootstrap {boot['status']}; intervals omitted."])
    lines.extend(['','| Sensitivity / 敏感性 | Astra | Fable |','|---|---|---|'])
    for domain in ['earth','engineering','life','mathematical','physical']:
        ds=[r['sensitivity'][s]['domains'][domain] for s in ['Astra','Fable']]
        lines.append(f"| {domain} | {ds[0]['K']}/{ds[0]['N']} | {ds[1]['K']}/{ds[1]['N']} |")
    for label,key in [('Five-domain equal weight / 五域等权','five_domain_equal_weight_percentage')]:
        lines.append(f"| {label} | {float(r['sensitivity']['Astra'][key]):.6f}% | {float(r['sensitivity']['Fable'][key]):.6f}% |")
    ps=[r['sensitivity'][s]['pass_at_3'] for s in ['Astra','Fable']]
    lines.append(f"| pass@3: at least one success / 至少一次成功 | {ps[0]['K_tasks']}/70 = {float(ps[0]['percentage']):.6f}% | {ps[1]['K_tasks']}/70 = {float(ps[1]['percentage']):.6f}% |")
    lines.extend(['',
                  '五域等权改变任务权重，pass@3 改变指标；均不替代官方 pass@1。三个 job 的试次率及均值见 [job_counts.csv](job_counts.csv)，逐任务及逐任务/job 整数表见 [task_counts.csv](task_counts.csv) 与 [task_job_counts.csv](task_job_counts.csv)。Domain weighting and pass@3 are sensitivity summaries, not alternative leaderboard scores.','',
                  '| Frozen claim / 冻结说法 | Source / 来源 | Display | One main label / 单一主标签 |','|---|---|---|---|'])
    source_names={'S1':'X original unread','S2':'OpenAI rendered only','S3':'Vals 09-11 announcement','S4':'Official JSON','S5':'Anthropic PDF §8.7','S6':'Vals 09-11 announcement','S7':'Official JSON'}
    for sid in ['S1','S2','S3','S4','S5','S6','S7']:
        c=r['claims'][sid];lines.append(f"| {sid} {c['system']} | {source_names[sid]} | {c['display']}% | {c['main_label']} |")
    lines.extend(['',f"七说法主标签计数：{json.dumps(r['seven_claim_label_counts'],ensure_ascii=False)}；一手支撑 {r['primary_support_count']}/7。S1a 单列，不增加七说法分母。The five external comparisons (including supplementary S1a) all stop at priority 1 because necessary source/configuration/run-identity fields are missing. Known agent or trial-count differences remain factual columns, with no causal attribution.",'',
                  'AA 使用 mini-swe-agent；模型卡 10 次/任务（700）与官方 3 次/任务（210）不同。OpenAI “maximum at any effort”可能是整套固定 effort 最高分，也可能是逐任务跨 effort 包络线，原文不能区分。历史 Vals 公告只保留固定一个 harness、pass@1 的字面；没有具名 agent 或完整试次聚合公式。No current Vals method is used to fill historical gaps.','',
                  'S1 原帖未读；S2 HTTP 403，仅渲染记录，不算原始字节一手支撑。S5 的 Last-Modified 是服务器修改字段，不证明出版或运行时间。All extracted fields, date types, evidence hashes and per-field states are in [claims_table.csv](claims_table.csv).','',
                  '| Rational compatibility / 有理数兼容 | Authorized denominator / 分母资格 | Full numerator set / 完整分子集合 |','|---|---|---|'])
    for e in r['rational_compatibility']:
        lines.append(f"| {e['record']} {e['x']}%, d={e['d']} | N={e['N']}, {e['denominator_qualification']} | {e['numerators']} |")
    lines.extend(['',
                  '全部由 for K in range(N+1) 和 Decimal 边界比较枚举；兼容分子不代表恢复试次。S1/S2 的 N 未写，不重构。46/70=138/210 与 24/70=72/210 不能鉴定统计单位。AA 内嵌小数与 133/210 在 15 位 HALF_UP 下相同，但整数交叉乘积确认它不是精确分数；这不解释未读的 S1。','',
                  '浮点对照仅限计数 float 与 accuracy float，以 Decimal.from_float 记录实际二进制值；显示解释算法仅 HALF_UP/HALF_EVEN/DOWN。63 与 63.3 的同算法原像存在交集，仅为算术存在性，不解释未读原帖；完整端点、全部命中算法及冻结允许对比见 results.json。','',
                  ('最终 AP-01–AP-19 全部完成并与冻结预测相符。' if all(x['matches'] for x in r['audit_predictions'].values()) else '仍未完成或停止的 AP 项：'+', '.join(k for k,v in r['audit_predictions'].items() if not v['matches'])+'；详见 results.json 的状态及诊断。') + ' 主计数、两套 bootstrap、stderr、域/job/pass@3 汇总见上述记录。仍未完成或不可验证：S1 原文读取、S2 原始页获取、外部逐试次与运行身份、完整任务字节身份、grader 验证、Fable 单条详情（冻结 HTTP 404）。These unknowns are scope limits, not completed checks. Current Vals background has numerically equal Fable 40.00 but no established run identity; it is not treated as a mirror.','',
                  '首轮 S1a 与 S5 提取代码发生实现错误，相应 AP observed=null、matches=false，解释停止；修正分别绑定摘要中的目标模型分数、排除 PDF 目录条目，再冻结代码重执行。首轮结果、全部代码及哈希保留于 [execution_01](artifacts/execution_01/)。这是看过首轮结果后的修正，不声称盲态。The first execution and corrected execution are both retained; no frozen source node, prediction, denominator, threshold or seed changed.','',
                  '末轮辅助核对已限定正式 tasks/ 目录：冻结版本的 70 个任务名与 API 相符；早先误纳入 CI/归档样例的诊断与第二轮代码保留于 [execution_02](artifacts/execution_02/)。任务文件字节及每次运行身份仍未验证。The benchmark task-name check excludes repository test fixtures; it does not establish task-byte identity.','',
                  '本次没有改变协议、阈值、分母或来源；[DEVIATIONS.md](DEVIATIONS.md) 记录执行偏离情况。[artifacts](artifacts/) 含逐输入校验、版本、预执行代码哈希、代码轨迹及公开锁定证据；第三方原始正文不入库。','',
                  '![Seven frozen claims and two official recounts](figures/figure1.png)','',
                  '图为自制对账图，按冻结来源顺序，不排新榜。英文与中文传播草稿分别见 [x_post.md](x_post.md)、[x_post_cn.md](x_post_cn.md)，均未发布。'])
    (root/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def drafts(root,r):
    english='Terminal-Bench-Science’s Astra 68.1% and Fable 5.1 40.0% check out: we counted 143/210 and 84/210 in public trial records. BenchLM matches too. No models were rerun; we accuse no one. Other claims lack complete run details.'
    chinese='Terminal-Bench-Science 的 Astra 68.1%、Fable 5.1 40.0% 对账一致：公开记录重加总为143/210、84/210，BenchLM也一致。未重跑模型，不指控任何一方；其他说法缺少完整运行信息。'
    assert len(english)<=270 and len(chinese)<=140
    link=f'{REPOSITORY}\nLocked protocol commit: {LOCK}'
    reply='Of seven frozen public claims, two official displays match the released labels; five lack complete run details. Different agent setups and repeat counts remain facts, without a causal explanation for the gaps.'
    (root/'x_post.md').write_text(f'Draft only — not published. Three posts total. Attach figures/figure1.png to the main post.\n\nPost 1 ({len(english)} characters):\n\n{english}\n\nReply 1:\n\n{reply}\n\nReply 2:\n\n{link}\n',encoding='utf-8')
    (root/'x_post_cn.md').write_text(f'仅传播草稿，未发布；主帖配图用 figures/figure1.png。\n\n主帖（{len(chinese)}字）：\n\n{chinese}\n\n一条回复：\n\n{REPOSITORY}\n锁定协议提交：{LOCK}\n',encoding='utf-8')
