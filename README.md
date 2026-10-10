# Terminal-Bench-Science 分数对账 / Score reconciliation

版本 / Version: **R11lock**，2026-10-10。

这是已有数据的独立审计规程：对官方公开的70任务×3次试次标签重加总，核对Astra与Fable 5.1的68.1%／40.0%以及BenchLM镜像；再按冻结规则审计七个传播说法及独立的AA63.3记录。选择它是因为传播口径分歧明确，官方420条布尔标签和任务连接已可获得，能交付整数分子/分母和算术判定，无需重跑模型。

This is a verification and audit protocol for existing data. It will independently re-tabulate released trial labels for two Terminal-Bench-Science systems, reconcile official and mirror displays, and audit a frozen set of public score claims. Available trial labels and clear arithmetic endpoints make the question feasible without running models again.

锁定方式：**首次 push 到公开 GitHub 的 main 分支提交即公开锁定时间戳**。本地commit及作者日期不等于公开登记时间；首次公开推送事件需留存可核查记录。当前仅本地准备，未push、未建远程、无公开锁定时间戳。独立执行代码之后须在分析前冻结哈希；后续偏离保留原协议并另记。

Locking: the first protocol commit pushed to the main branch of a public GitHub repository serves as the public lock timestamp. A local commit date alone is not public registration; retain evidence of that first public push. This repository is currently local, with no remote or public lock. Freeze the independent analysis code before execution and document subsequent deviations.

已知结果披露：同一次可行性查看已见143/210、84/210及官方精确均值/展示/配置与平衡设计；这些不是事前未知发现。主计数、确定的SE、镜像判定、外部五对主标签及有理数集合均写成编号审计预测（AP-01至AP-19）。正式独立分析、bootstrap、来源主标签尚未执行；**未重跑模型**。本审计只核对公开标签算术，不验证grader、任务字节、科学发现或模型因果优越。

Known results: the prior feasibility check exposed 143/210 and 84/210, official means and displays, configurations, and the balanced design. Counts, SE checks, mirror verdicts, five external labels, and rational compatibility sets are numbered audit predictions (AP-01 through AP-19). The independent analysis and intervals have not been run. No models have been rerun; arithmetic agreement does not validate grading, task bytes, scientific conclusions, or causal model superiority.

文件 / Documents:

- [PREREG.md](PREREG.md)：冻结审计协议 / frozen protocol。
- [feasibility.md](feasibility.md)：输入与提取路径、可行性、预算 / input paths and feasibility。
- [pick.md](pick.md)：选择理由与传播记录 / selection rationale and claims。
- [response.md](response.md)：第一轮逐条回应历史 / first-round response history。
- [response2.md](response2.md)：第二轮逐条回应与规则取舍 / second-round response and rule decisions。
- [agy_review.md](agy_review.md)、[grok_review.md](grok_review.md)：第一轮独立审稿意见 / first-round independent reviews。
- [agy_review2.md](agy_review2.md)、[grok_review2.md](grok_review2.md)：第二轮评审原文 / second-round independent reviews。
- [DOC_SHA256SUMS](DOC_SHA256SUMS)：公开文档、输入元数据及工具代码SHA-256，排除清单自身 / hashes for public documents, metadata and helper code。
- [INPUTS_SHA256SUMS](INPUTS_SHA256SUMS)：JSON格式输入清单，文件名/URL/字节/SHA-256/历史抓取UTC/证据等级；仅元数据 / metadata only。
- [tools/fetch_inputs.py](tools/fetch_inputs.py)：按清单重抓并验哈希，或离线验已有缓存 / refetch or verify cached bytes。
- [tools/audit_rules.py](tools/audit_rules.py)：字面分隔符与Decimal规则；对全部0≤K≤N循环生成兼容集合，不含预测分子 / pure display and Decimal enumeration rules, with no embedded predicted numerators。

原始网页、PDF、JSON、轨迹和环境配置不入库；`.gitignore`排除缓存。URL可能漂移，重抓字节不匹配即失败，不能替换冻结快照。渲染记录无法由HTTP重新生成；未读出处无哈希。脚本默认离线核验；联网需显式`--fetch`：

```bash
python3 tools/fetch_inputs.py --help
python3 tools/fetch_inputs.py --verify-only
python3 tools/fetch_inputs.py --fetch --file science_board_v01.json
```

Raw third-party pages, PDFs, JSON, traces, and environment configurations are excluded. Refetched bytes must match the frozen hashes; mutable endpoints may no longer do so. Rendered records require the original saved artifact and cannot be recreated as raw HTTP bytes. The helper verifies locally by default and accesses the network only with `--fetch`.

计划交付 / Planned outputs: `REPORT.md`、`results.json`（预测/实测/相符）、任务/job汇总表、七说法及S1a来源/关系表、自制对账图、独立代码及版本/哈希、`DEVIATIONS.md`。这些是未来交付物，本轮仅修订规程、交付纯规则函数并作合成案例验证与本地提交；未对真实数据运行主分析或兼容集合枚举。完整独立执行代码及所有代码哈希须在正式执行前冻结。

规则摘要 / Rule constraints: 展示串仅按字面 `+/-` 切分并清理两段；SE采用三方一位数字串相等；镜像双方分数量化一位、元数据完整字面相等。外部五对均预测“来源未完整披露”，配置差异单列事实；CPython或NumPy不一致停止主区间与分层敏感性，pdftotext不一致使S5提取失败。完整算法以PREREG为准。

仍未知 / Remaining unknowns: 外部逐试次/运行身份、未读原帖、OpenAI原始页与effort操作、任务字节锁。Missing external trials, run identities, unread posts, original OpenAI bytes and effort selection details, and task-byte identity remain explicit unknowns.
