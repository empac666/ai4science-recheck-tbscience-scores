# Terminal-Bench-Science 分数对账：可行性与输入说明

2026-10-10；版本 **R11fix-1**。已有数据的独立审计规程配套文件，分析规则以 [PREREG.md](PREREG.md) 为准。核心匿名数据已拿到，可在一天内完成记录对账。仅此前做过结构/主键和小计数检查；本轮修订未运行正式主分析、区间或模型。

## 1. 冻结与已知信息

官方API为浮动端点，冻结原始字节；核心 `science_board_v01.json` 493,155字节，抓取2026-10-10T00:24:00.008949+00:00，SHA-256 `86e6278ca64da88b69c1efd6059a33248bd300f27673098f60184286b470c4a7`。镜像 `benchlm_science.html` 253,414字节，SHA-256 `2704a4ca05d74d00c5c5b40ea9b54a9fdbf511823e56b16dfc7184bdb1a8361a`。输入URL、大小、哈希、逐文件抓取UTC及来源等级统一见 [INPUTS_SHA256SUMS](INPUTS_SHA256SUMS)，不链接未入库缓存。

官方leaderboard `v0-1-eval`、id `9a545a14-78d0-44b4-9003-afe062522a47`、dataset_version_id `2b817f26-dc4f-4477-8032-2218dcc553b5`；GitHub `v0.1.0`到commit `f81afac4f11048e77a15dfc8fb1dbfb897fea0ce`。固定tree的70个task.toml任务名与API无差集；不验证每次运行的任务文件字节。

| 已见字段／资格 | 基线事实（同一次可行性查看） |
|---|---|
| 系统 | 17行；只锁Astra `76867ebc-8f35-43c5-a8b0-0cee9db46c96`、Fable `1264a994-632f-4742-a143-a848a6ad4114` |
| 配置 | metadata中的GPT-6 Astra/Codex/max、Fable 5.1/Claude Code/max |
| 任务 | 70唯一id；life19、physical17、mathematical17、engineering9、earth8 |
| 标签与主键 | 各70 cell×3条JSON bool，共420；各210唯一trial，3个job×70，每task每job一条；无缺项/重复 |
| 已知计数／均值 | bool小计及metrics为143/210、84/210；accuracy为68.0952380952381、40（0–100）；展示68.1／40.0，stderr展示3.2／3.4 |
| 已见来源差异 | 模型卡10次/700，官方3次/210；AA mini-swe-agent；OpenAI maximum at any effort的两种操作未知 |
| 限制 | Vals换了当前数字；Astra只抽查1条配置；Fable详情404；任务字节未锁 |

这不是独立主分析；三份文档的143/84是同一次查看。冻结AP-01/02计数预测、AP-03确定的SE、AP-04平衡设计恒等式。正式执行须新写/冻结代码，两路径独立求和，不import可行性脚本；任一路径偏离计数预测，先保存再停止后续。

## 2. 冻结提取路径与一手支撑

逐说法须同时满足原始成功HTTP字节哈希、冻结路径、命中字符串、URL及日期字段/类型，抓取UTC另列；不得搜索替代节点补缺。原文日期未知不能用模型发布日期冒充页面发布时间。下表用已见短串冻结定位，执行仍从校验后的原始文件提取；节点/行不唯一或缺失即失败。

| 记录／文件 | 固定提取路径与必命中字符串 | 日期字段／类型 |
|---|---|---|
| S1／X 63 | 原帖未下载、字符串未读取；不以AA替代 | 原帖日期未知；只有既有10-09调研记录 |
| S1a／aa_science.html | 可见最内层div：完整模型名`GPT-6 Astra (Max)`及`with a score of 63.3%`的唯一摘要；同时解码`self.__next_f.push`字符串RSC，取JSON对象id=`2f339a97-9a0d-499a-9cb5-e0db665bfa25`、slug=`gpt-6-astra`的`terminalBenchScience`原串=`0.633333333333333`；方法div含`three repeats per task`、`mini-swe-agent`及70任务说明 | 同RSC对象`releaseDate=2026-09-03`（模型发布日期，非评测日）；抓取UTC单列 |
| S2／openai_web_rendered.json | JSON `tool_result`中L182表头GPT-6 Astra列，L183 Terminal-Bench Science 0.1行`64.6%`，L224方法`maximum at any effort` | `retrieved_at_utc=2026-10-10 00:25:38 UTC`，渲染读取时间；出版/运行时间未知 |
| S3、S6／vals_home.html | CSS `div.hidden.update-content[data-update-slug="2026-09-11-terminal-bench-science"]`：Astra `65.71%`、Fable `34.29%`；不取当前benchmarkData或BenchLM内嵌Vals表 | 祖先astro-island的`props`按Astro序列化解包，`updates`中同slug的`data.date=09/11/2026`（公告日期） |
| S4、S7／science_board_v01.json | `rows`中§1两个精确id；`metrics.display_accuracy`分别`**68.1%** +/- 3.2%`、`**40.0%** +/- 3.4%`；原值`metrics.accuracy`，SE `metrics.accuracy_stderr` | 两行`created_at/updated_at`为09-22/09-22、09-13/09-16（榜单行时间）；保留完整UTC原串 |
| S5／anthropic_systemcard.html | MIME application/pdf，文件头`%PDF-`；二进制传pdftotext `-layout`，印刷页171–172中§8.7 Terminal-Bench-Science唯一句`Claude Fable 5.1 scored 52.6% averaged over 10 trials per task (700 trials)` | HTTP `Last-Modified=Tue, 01 Sep 2026 17:40:21 GMT`（服务器修改字段，不证明出版日）；抓取UTC单列 |
| 镜像／benchlm_science.html | 唯一`script#__NEXT_DATA__` JSON，仅`props.pageProps.leaderboard`中sourceModelId=`openai-gpt-6-astra-codex`及`anthropic-fable-5-1-claude-code`；model=`GPT-6 Astra`／`Claude Fable 5.1`，harness/effort=Codex/max／Claude Code/max，score=`68.1`／`40`，externalUrl指向官方；`props.pageProps.trustCard.provenance.kind=mirror`，sourceUrl为官方域 | `props.pageProps.lastUpdated=October 7, 2026 snapshot`（快照日期） |

七说法分母S1–S7固定；S1未读，S2“渲染可读”不进原始字节分子，**上限5/7，实际数由提取核验决定**。S1a独立报告，不补63、不增加七数分母。镜像不是独立评测，不重复增加分子。

S5发布页 `anthropic_release.html`只作同值旁证：HTML指标表Terminal-Bench-Science 0.1行、Claude Fable 5.1列52.6%；不替代PDF的700和设置证据。PDF不得交给HTML解析器，派生TXT不是原始输入。

## 3. 配置、背景与版本锁

| 证据 | 用途／边界 |
|---|---|
| science_trial_sample.html | 一条Astra trial id=`0156fedf-e8cc-5e04-bf3f-7b9e1aa435ff`的RSC配置：Codex0.155.1、verifier disable=false、environment_mode=separate、timeout_multiplier=1；仅代表这一条，不外推其余试次 |
| science_fable_trial_sample.html | HTTP404，只记录获取失败，不证明不存在配置 |
| Anthropic PDF §8.7 | Claude Code --bare、maximum effort、70×10；无700条标签，不恢复试次；兼容分子仅封闭枚举 |
| vals_science.html | 当前主表39行/域表5行，Astra62.86、Fable40.00、mini-swe-agent等只作带抓取时间背景，不回填09-11 |
| AA | 3次pass@1均值；背景Fable43.33不进入七数/主图 |
| OpenAI | 整套固定effort最高分／逐任务包络线均未知；N未写，不重构64.6 |
| tb_tree_v01.json、tb_tag.json | 任务名称/域和版本佐证，不验证运行身份或字节一致 |
| tb_news.html | 冻结哈希的背景，**不参与任何终点** |

锁CPython3.13.5、NumPy2.5.3、BeautifulSoup4 4.15.0、Poppler/pdftotext25.03.0，可选Matplotlib3.11.2。主百分数/SE用精度50 Decimal，主显示HALF_UP；显示解释仅HALF_UP/HALF_EVEN/DOWN，有理数只HALF_UP；版本变化先记偏离。

主区间非分层70任务簇，10,000次PCG64(2026101001)、linear分位数；分层按原域数仅敏感性，另seed2026101002；两系统共用任务索引。区间只描述官方420标签重采样，不判外部数字显著性/谁正确，不以作者±重叠判显著性。SE相等规则见PREREG §5：原始stderr各量化后核显示，不直接用未量化长串比较。

## 4. 执行预算与降级

无需账号、GPU、模型重跑或付费API，普通CPU可读420标签。通常3–4小时、硬上限8小时是静态预算，未做计时实验。

| 累计时间 | 工作／出口 |
|---|---|
| 0–30分钟 | 哈希、冻结独立代码、资格检查；核心离线 |
| 30–90分钟 | 双路径、预测/实测表、官方内部/镜像判定；计数偏离保存后停止 |
| 90–150分钟 | 主非分层区间、分层敏感性及汇总；150分钟省略未完成区间 |
| 150–210分钟 | 来源表、兼容集合、单主标签；210分钟停止扩大来源搜寻 |
| 210–240分钟 | 图、冻结首句及报告核验 |
| 8小时 | 硬停止，保存核心、诊断和次级未完成状态 |

核心哈希/主键失败停止受影响计算，不换现榜、分母或筛失败。镜像无法抽取单列，不改变官方内部判定。次级配置缺失保留未知；缺失优先可覆盖已知配置差异，仍保留差异事实。公开只含方案、自制结果与必要元数据，不上传原始HTML/PDF/JSON、轨迹或环境配置。本轮只修订/本地提交，不执行以上主分析。
