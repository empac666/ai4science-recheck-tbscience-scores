# Terminal-Bench-Science 分数对账：已有数据的独立审计规程

2026-10-10；版本 **R11lock**（Verification & Audit Protocol）。采用OSF Existing Data / Secondary Data Analysis的可见信息披露结构，不声称盲态或早于数据查看。尚未公开锁定、未运行正式主分析、区间或模型。首次 push 到公开 GitHub 的 main 分支提交作为公开锁定时间戳；本轮只准备本地提交。

## 1. 问题与冻结记录

主问题：独立重加总已公开的试次成功标签，官方两系统展示值及BenchLM镜像是否算术相符？审计对象是记录，不是模型、grader或科学发现。榜单有17系统，本题只锁两个id；七说法取自已见10-09材料，不是全网抽样。

| 记录 | 系统／数字字符串（%） | 冻结出处／证据等级 | 同一原文写明的N |
|---|---|---|---|
| S1 | Astra `63` | X原帖未读；仅既有说法 | 未知，不重构 |
| S1a | Astra `63.3`；内嵌 `0.633333333333333` | AA HTML原始字节，独立补充 | 70任务×3，210 |
| S2 | Astra `64.6` | OpenAI渲染可读；原始页HTTP403 | 未写明，不重构 |
| S3 | Astra `65.71` | Vals09-11隐藏公告原始字节 | 未写试次数；仅方案列70／210 |
| S4 | Astra `68.1` | 官方JSON；BenchLM另作镜像 | 210 |
| S5 | Fable5.1 `52.6` | Anthropic PDF §8.7原始字节 | 700 |
| S6 | Fable5.1 `34.29` | 同Vals历史公告原始字节 | 未写试次数；仅方案列70／210 |
| S7 | Fable5.1 `40.0` | 官方JSON；BenchLM另作镜像 | 210 |

七说法固定S1–S7；S1a不替代S1、不增加分母。URL、字节、哈希、抓取UTC见 [INPUTS_SHA256SUMS](INPUTS_SHA256SUMS)；提取路径、日期字段及短串见 [feasibility.md §2](feasibility.md#2-冻结提取路径与一手支撑)，选择理由见 [pick.md](pick.md)。

OpenAI“maximum at any effort”保留两种未知配置：整套基准选总分最高的固定effort；逐任务取跨effort最大值后平均（oracle envelope）。原文不能区分，均不得当成已确认设置或差值因果解释。

## 2. 已知基线／事前冻结的待检验项

**A．已知基线（Observed Baseline）。** 同一次可行性检查已见小计143/210、84/210，官方均值68.0952380952381、40，展示68.1／40.0及stderr展示3.2／3.4；原始 `metrics.accuracy_stderr` 数字串分别为 `3.2164475807033743`、`3.380617018914066`；三份文档不是三次复现。已见两行id、Codex/max与Claude Code/max；每任务恰好3条、3个job各70条；五域life/physical/mathematical/engineering/earth为19/17/17/9/8。官方3次与模型卡10次/700不同；AA为mini-swe-agent；OpenAI跨effort取最大但方式未知。Vals当前行换了另一套数字，Fable详情404；Astra只抽查1条配置，不能外推其余试次。任务名对齐固定提交，未验证任务字节锁。上述信息已约束次级标签，不包装为事前未知发现。

**B．冻结待检验项（Prospective Audit Targets）。** 待独立执行：双路径布尔累计、字段与Decimal显示一致性、限定浮点/舍入对照、镜像核对、封闭有理数枚举、来源单标签、任务簇区间和次级汇总。已知整数及确定的SE是审计预测，重算相符只确认审计轨迹。

| 编号预测 | 预期输出／对象 |
|---|---|
| AP-01 | A、B各得Astra K=143，N=210；一位展示68.1 |
| AP-02 | A、B各得Fable K=84，N=210；一位展示40.0 |
| AP-03 | 已知K决定的朴素SE按§5量化：Astra `3.2`、Fable `3.4`；计算SE、原始stderr各量化一位后的数字串与清理后的展示后段三方相等，预期两系统均相符 |
| AP-04 | 平衡设计下70任务等权与210试次等权百分数相等（代数复核） |
| AP-05 | `M_A=一致`：镜像Astra与官方score各量化一位均为 `68.1`，且§4冻结元数据逐字段精确相等 |
| AP-06 | `M_F=一致`：镜像Fable原始score `40` 与官方 `40.0` 各量化一位均为 `40.0`，且§4冻结元数据逐字段精确相等 |

外部五对主标签预测为AP-07至AP-11，有理数集合预测为AP-12至AP-19，编号及预期逐项见§4。

`results.json`每个编号独立记录 `prediction`、`observed`（独立重算／抽取／枚举）、`matches`、`status`、`deviation`；提取失败时 `observed=null`、`matches=false`、`status=extraction_failed`，不填入预测。任一计数路径偏离AP-01/02时保存偏离值、诊断并停止后续；AP-03及AP-05至AP-19偏离时记录并停止该项解释，不改变其他独立项目的判定。不得改预测、阈值或分母。

## 3. 输入、资格与独立实现

核心仅 `science_board_v01.json`、`benchlm_science.html`；其余只支撑来源/版本字段。先校验所有输入字节/哈希，不以派生文件替代原始输入。`tb_news.html`不参与任何终点。历史名 `anthropic_systemcard.html` 按二进制PDF流解析，禁止按HTML读取。

官方 `v0-1-eval`：leaderboard id `9a545a14-78d0-44b4-9003-afe062522a47`，dataset_version_id `2b817f26-dc4f-4477-8032-2218dcc553b5`；发布 `v0.1.0` commit `f81afac4f11048e77a15dfc8fb1dbfb897fea0ce`。冻结下载字节，不要求联网取现榜。

| 固定行 | id | 精确metadata标签／agent／effort |
|---|---|---|
| Astra | `76867ebc-8f35-43c5-a8b0-0cee9db46c96` | GPT-6 Astra／Codex／max |
| Fable | `1264a994-632f-4742-a143-a848a6ad4114` | Fable 5.1／Claude Code／max |

全集为 `task_matrix.tasks` 的70唯一id；`task_matrix.rows[row_id]`精确覆盖全集。每cell3条trial，`solved`必须JSON bool；trial id系统内唯一；每task每job一条，各3个job各70条。主键 `(row_id,task_id,trial_id)`，域连接 `tasks[].domain`。缺键、重复、非bool即停止受影响计算，不修补、筛选或删失败项。`metrics.tasks=210`是试次数。

本轮交付 [tools/audit_rules.py](tools/audit_rules.py) 的纯规则函数（展示串清理、Decimal量化、封闭枚举）；本轮不执行真实输入的枚举或主分析。正式执行前另写完整独立执行代码并冻结包括规则函数在内的所有代码哈希；不得import可行性脚本或用其输出作独立计数。A直接task→trial累计；B独立解析并job→task累计；不得共用求和函数。

版本锁：CPython **3.13.5**、NumPy **2.5.3**、BeautifulSoup4 **4.15.0**、Poppler/pdftotext **25.03.0**；可选图Matplotlib **3.11.2**。记录系统及实际版本，不匹配先记偏离，不静默替换。CPython或NumPy任一版本不一致，停止主区间及分层敏感性，不生成带种子区间；BeautifulSoup或Matplotlib不一致记偏离；pdftotext不一致时S5提取按失败处理，不以其他解析器替代。

## 4. 指标、算术与来源判据

令 `y_sij=int(solved)`，`K_s=Σ_iΣ_j y_sij`，`q_si=Σ_j y_sij/3`。

| 指标 | 公式／用途 |
|---|---|
| 主百分数／标准pass@1（k=1） | `P_s=100 K_s/210=100 mean_i(q_si)`；AA“pass@1，3次”是试次均值 |
| 次级pass@3 | `100 Σ_i 1{Σ_j y_sij≥1}/70`；至少一次成功，不替代榜单均值 |
| 五域等权 | 五域成功率均值，改变任务权重，仅次级 |

Decimal精度50，中间运算上下文固定 `ROUND_HALF_EVEN`，最终主显示量化固定 `ROUND_HALF_UP`；JSON用 `parse_float=Decimal`保留数字符；主值从 `Decimal(K)/Decimal(210)*100`计算，以 `Decimal('0.1')`、`ROUND_HALF_UP`量化。禁止将二进制浮点accuracy舍入作主值。`metrics.accuracy`锁0–100尺度，允许绝对差≤`1e-10`个百分点。`display_accuracy`仅以字面 ASCII 三字符 `+/-` 切分，必须恰好出现一次；找不到该分隔符、出现多次或清理后非合法非负十进制数字串，记提取失败并停止这项核对。前后两段均先 `strip()`，再删除所有 `*`、`%` 和空白字符，不补符号或末尾零，不把 Unicode `±` 替代为分隔符。已见前段数字串预期分别为 `68.1`、`40.0`，后段预期分别为 `3.2`、`3.4`；前段与主Decimal一位量化的定点数字串精确相等，保留末尾零；后段用于§5三方相等核对。附属浮点对照仅 `float(K)/210*100`和accuracy转float：用 `Decimal.from_float`固定实际二进制值，按下述三算法各量化一位，记录与主Decimal对应算法输出是否相符及偏差，不改变主判定。

**主算术判定：** 官方内部须A/B的K/N相同、cell.solved/total及metrics.passes/tasks、n_trials相符，均值满足阈值且显示匹配；否则“不一致”。镜像只取冻结两行，双方score均以 `Decimal(原始数字串)`、精度50、`Decimal('0.1')`、`ROUND_HALF_UP`量化一位后比较；原始数字串是否有小数点/末尾零只进事实列，不参与主判定。下表冻结的元数据全部精确相等且量化分数相等才“一致”；可抽取而不满足则“不一致”，不可抽取则“镜像无法抽取”。两系统分判；镜像失败不改变官方内部判定。

镜像提取路径仍限唯一 `script#__NEXT_DATA__` 的 `props.pageProps.leaderboard` 两行及 `props.pageProps.trustCard.provenance`。各字段按完整字符串比较，不作大小写、空白、URL尾斜线或域名归一化：

| 字段 | Astra预期字面量 | Fable预期字面量 |
|---|---|---|
| sourceModelId | `openai-gpt-6-astra-codex` | `anthropic-fable-5-1-claude-code` |
| model | `GPT-6 Astra` | `Claude Fable 5.1` |
| harness | `Codex` | `Claude Code` |
| reasoningEffort | `max` | `max` |
| externalUrl | `https://www.terminal-bench-science.ai/` | `https://www.terminal-bench-science.ai/` |
| provenance.sourceUrl | `https://www.terminal-bench-science.ai/` | `https://www.terminal-bench-science.ai/` |
| provenance.kind | `mirror` | `mirror` |
| provenance.text | `Every row is mirrored from Terminal-Bench-Science 0.1 as it publishes it; BenchLM did not re-run these results.` | 同左完整字符串 |

`provenance.total` 还须为JSON整数 `17`（非bool）；对象字段集合精确为 `{kind,total,text,sourceUrl}`，键顺序无关，不接受额外/缺失字段。AP-05/06在 `results.json` 各记录预测、原始抽取字段、双方量化分数、字段逐项命中及是否相符，禁止仅把预测当作镜像输出。

**一手支撑：** 每条须同时有原始成功HTTP字节哈希、冻结提取路径、命中字符串、URL及日期字段/类型（抓取UTC另列）；缺一“未达一手”。S1未读、S2仅渲染均不计原始字节分子，故“有一手支撑数/7”上限**5/7**，实际数待执行。S1a证据单列，不补S1；日期不冒充运行时间。S5的HTTP `Last-Modified` 在类型上满足“日期字段/类型”的提取规范，仅表示服务器修改时间，不证明出版日或运行日。

**冻结对比对：** S4/S7展示各对官方精确均值；BenchLM两行各对官方；S1a/S2/S3各对官方Astra；S5/S6各对官方Fable。S1仅列未读状态，不配63↔63.3运行对。跨模型只描述官方两系统差值；未列对不入主表。

官方内部/镜像对只用上段算术标签；外部五对每对一个主标签，严格依次取首个命中，不拼复合标签：

| 优先级 | 条件 | 主标签 |
|---:|---|---|
| 1 | 提取/数值/来源，或模型、agent、effort操作、试次数、指标公式、数据集版本、运行身份任一必要字段缺失 | 来源未完整披露 |
| 2 | 必要字段完整，配置字段仅限模型、agent、effort操作、试次数、指标公式、数据集版本，其中任一与官方不同 | 配置差异已证实，因果未定 |
| 3 | 上述身份/配置相同，更高精度同一原值按两种展示精度得到两数 | 舍入解释了差值 |
| 4 | 身份/配置相同但原值缺失，展示原像相交 | 可由舍入兼容 |
| 5 | 必要字段完整、配置相同，但更高精度同原值舍入或展示原像均不能解释差值 | 同配置下算术不符 |

**运行身份操作定义：** 外部数字的同一原文须同时明确出现§3对应官方 `row_id` 的完整字符串，并将该数字声明为该官方 `v0-1-eval` 榜单运行（leaderboard id须为§3冻结值），才记“与官方相同”；模型名、agent、effort或相同分数均不构成运行身份。仅出现id但没有榜单运行关联仍为缺失。数据集版本命中须同一原文明确给出§3 `dataset_version_id` 完整值，或明确给出发布 `v0.1.0` 及其完整commit并关联到该评测；后者仅命中公开版本，内部id仍单列缺失。泛称0.1不等于已确认版本或任务字节身份。

配置事实与内部追踪元数据分列。单条trial的Codex版本、重试/回退、verifier、timeout、environment_mode均只作样例事实，不触发系统级主标签；不能用当前Vals方法页回填历史公告。优先级2在必要字段完整的对比可达，当前五对因运行身份缺失均停在1，优先级2–5对这五对不适用；明确配置差异仍在事实列披露。

事实表每一字段使用 `state` 和可选 `literal`，`state`只允许 `{已见字面,缺失,与官方相同,与官方不同}`；已见字面或比较状态只能附下面已冻结的字面量，缺失用null，禁止推测性取值。模型字面差异不自行映射为新型号；effort操作不能由Max标签推断。完整提取路径见feasibility §2。

| 编号／冻结对比 | 数字／模型字面 | agent字面／比较 | effort字面／操作 | 试次数 | 指标公式 | 数据集版本／运行身份 | 预期主标签 |
|---|---|---|---|---|---|---|---|
| AP-07 S1a↔官方Astra | `63.3`／`GPT-6 Astra (Max)` | `mini-swe-agent`／与官方不同 | `Max`／操作缺失 | `three repeats per task`，210／与官方相同 | `pass@1 averaged over three repeats per task`／与官方相同 | `Terminal-Bench-Science 0.1.0`、版本身份缺失／运行身份缺失 | 来源未完整披露 |
| AP-08 S2↔官方Astra | `64.6`／`GPT-6 Astra`（渲染） | 缺失 | `maximum at any effort`／操作缺失 | 缺失 | 缺失 | 缺失／缺失 | 来源未完整披露 |
| AP-09 S3↔官方Astra | `65.71`／`GPT-6 Astra` | `one harness fixed`、agent身份缺失 | 缺失 | 缺失 | `pass@1`、试次聚合公式缺失 | 缺失／缺失 | 来源未完整披露 |
| AP-10 S5↔官方Fable | `52.6`／`Claude Fable 5.1` | `Claude Code --bare`／已见字面 | `maximum effort`／固定maximum操作，与官方相同 | `10 trials per task (700 trials)`／与官方不同 | `averaged over 10 trials per task`／与官方相同 | 缺失／缺失 | 来源未完整披露 |
| AP-11 S6↔官方Fable | `34.29`／`Claude Fable 5.1` | `one harness fixed`、agent身份缺失 | 缺失 | 缺失 | `pass@1`、试次聚合公式缺失 | 缺失／缺失 | 来源未完整披露 |

S3/S6仅就冻结历史公告提取；保留该节点已见“固定一个harness”和pass@1字面，但未给agent名称、试次数或完整聚合公式，当前方法的具名harness/公式不移入这张事实表。S2原始来源失败另列，不因渲染值升级来源。每对 `results.json` 保存预测标签、独立抽取事实、首个命中优先级、实际主标签、是否相符；偏离即停止该对解释，禁止改标签或把编号预测直接充当提取结果。

effort字段含§1两种未知操作，禁止回填为固定max。缺失优先可使已知配置差异的来源停在披露等级，差异仍在事实字段保留，不升级主标签或解释差量。只有同批官方原始试次的聚合可作口径代数复核，另列；外部均无成对试次，禁止“口径差异解释”标签。

显示解释算法全集仅 `{ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN}`，列全部命中算法及结果，禁止另加算法。非负显示x、d位，h=`10^-d`：HALF_UP原像 `[x-h/2,x+h/2)`；HALF_EVEN末位偶数双含端点、奇数双不含；DOWN原像 `[x,x+h)`；截到[0,100]。两显示须用同算法。63和63.3的HALF_UP原像 `[62.5,63.5)`、`[63.25,63.35)`相交，存在性不解释未读原帖。

**封闭有理数检验：** 独立算术字段，不是来源主标签。只用该数字同一原文写明N；Vals仅“假定N”方案列，禁止当前页回填。S1/S2不重构，不借210或700。其余逐固定N枚举全部整数 `0≤K≤N`，仅HALF_UP与原显示位数d：`C_N(x)={K:100K/N∈[x-h/2,x+h/2)}`，Decimal边界比较；报告完整“与该分母兼容的分子集合”，包括空集。

| 编号 | 记录／显示位数d | 允许N／分母资格 | 预测兼容分子集合 |
|---|---|---|---|
| AP-12 | S1a `63.3`／1 | 同原文210 | `{133}` |
| AP-13 | S3 `65.71`／2 | 假定70 | `{46}` |
| AP-14 | S3 `65.71`／2 | 假定210 | `{138}` |
| AP-15 | S6 `34.29`／2 | 假定70 | `{24}` |
| AP-16 | S6 `34.29`／2 | 假定210 | `{72}` |
| AP-17 | S5 `52.6`／1 | 同原文700 | `{368}` |
| AP-18 | S4 `68.1`／1 | 同原文210 | `{143}` |
| AP-19 | S7 `40.0`／1 | 同原文210 | `{84}` |

交付规则函数对每个固定N运行 `for K in range(N + 1)`，精度50下生成Decimal边界；以 `lower*N ≤ Decimal(100)*K < upper*N` 比较，等价于上述百分数区间，避免边界上的除法近似。预测表只用于事后比对，严禁以表中集合、预置K或“百分数×N四舍五入”代替循环枚举输出。每个编号在 `results.json` 记录预测集合、枚举完整集合（含空集）、x/d/N及分母资格、是否相符；与预测不符保存偏离并停止该项解释。

S1a内嵌 `0.633333333333333` 唯一允许算术陈述：它与 `Decimal(133)/Decimal(210)` 在15位小数 `ROUND_HALF_UP` 下相同，但不等于精确分数133/210（精确关系以整数交叉乘积检验）。该陈述不进入来源主标签、不把未读S1记为已解释。

46/70=138/210、24/70=72/210不能鉴定统计单位。兼容集合仅是算术可能性，**不得称已恢复试次、不得生成试次列表，禁止百分数×N填官方主计数分子**。

## 5. 区间与次级汇总

固定汇总任务/域/job通过数、五域等权、各job70试次率和三job均值、pass@3；AP-04是恒等式。主区间明确**非分层任务簇**：把70任务视为跨域无权重任务分布的经验样本，不把固定域配比作为约束，也不证明全科学总体代表性。

task id字典序；`Generator(PCG64(2026101001))`，10,000次，每次 `integers(0,70,size=70)`有放回抽70任务，保留各3条trial，两系统共用索引；P和两官方系统差值取2.5%/97.5%分位数，固定 `numpy.percentile(...,method="linear")`。分层敏感性另起 `PCG64(2026101002)`，按earth/engineering/life/mathematical/physical顺序、各域task id排序，分别有放回抽原域8/9/19/17/17任务，两系统共用索引，仍按70任务合并。不得挑区间替代主区间。

朴素SE仅210条独立伯努利口径：`p=Decimal(K)/210`，`SE=100*sqrt(p*(1-p)/210)`。AP-03相等规则：计算SE与从§2A原始数字串解析的 `metrics.accuracy_stderr` 各按 `Decimal('0.1')`、`ROUND_HALF_UP`量化一位并转定点数字串；两者与§4按字面 `+/-` 切分并清理的后段数字串三方完全相同（预期 `3.2`／`3.4`），才“相符”；不把未量化长串直接比3.2/3.4。不相符报告值，不改主计数。有限冻结集合计数无抽样误差，区间只描述重采样。

**区间/SE不得判外部数字显著不同、谁正确或谁更强；作者±3.2/±3.4不是95%CI，不由其重叠或不重叠推显著性。** 未完成10,000次的区间省略并写状态。

## 6. 停止、传播与交付

硬上限8小时；150分钟区间未完成则省略，210分钟停止扩大来源搜寻，预算见 [feasibility.md §4](feasibility.md#4-执行预算与降级)。核心哈希/资格失败停止受影响计算；AP-01/02偏离停止后续；AP-03、AP-05至AP-19偏离停止该项解释；版本停止规则见§3。保留诊断及 `DEVIATIONS.md`，不得换latest、阈值、分母、模型、任务或删失败项。额外网页不可读只影响次级。

报告首句逐字冻结，仅替换占位符：

> 对已公开的70任务×3次试次标签的独立对账重加总得到：Astra {K_A}/210={P_A_raw}%（一位展示{P_A_1}%），Fable 5.1 {K_F}/210={P_F_raw}%（一位展示{P_F_1}%）；对官方68.1%／40.0%的内部判定分别为{V_A}／{V_F}，BenchLM镜像判定分别为{M_A}／{M_F}；本审计未重跑模型，判定只针对榜单展示值的算术相符，不涉及grader、任务字节、科学结论或谁更强。

K来自两路径；`{P_A_raw}`、`{P_F_raw}`只代入精度50、`ROUND_HALF_EVEN`上下文下依序 `Decimal(K)/Decimal(210)*Decimal(100)` 得到的定点字符串 `format(value, 'f')`，仅在有小数点时删除小数部分末尾零并删除空小数点（代码为 `.rstrip('0').rstrip('.')`），不删整数末尾零；不再一位量化、不使用循环节括号、不加入分数或百分号；分数只由模板外围 `{K}/210=` 保留。该50位Decimal字符串是计算近似，精确值由整数比给出，不称无限精确十进制；Fable raw为 `40`，一位展示为 `40.0`。`results.json`另保存整数比和同一Decimal字符串；一位按§4。V仅 `{一致,不一致}`；M仅 `{一致,不一致,镜像无法抽取}`。路径未完成/停止时不用此句，报告“审计未完成”及原因。63、63.3、64.6、65.71、52.6、34.29不得进入首句。

未来交付 `REPORT.md`、`results.json`、任务/job表、七说法及S1a证据/关系表、自制对账图、独立代码/版本/哈希、`DEVIATIONS.md`。图只含七说法加两官方重算值，S1标未读，S1a只进来源表；不做新排名或跨来源显著性。当前Vals62.86/40.00、AA Fable43.33只留背景；Vals40.00另记“数值相同、运行身份未建立”，不当镜像；“nearly twice”仅Vals引文，不换算或移到官方值。

公开只放方案、自制汇总、必要短串与元数据；第三方原始网页/PDF/JSON、轨迹、环境配置仅本地缓存。文档链接相对；本轮不push、不建远程、不跑主分析。
