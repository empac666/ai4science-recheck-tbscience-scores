# Terminal-Bench-Science 分数对账 / Score reconciliation

已完成对冻结公开逐试次记录的独立重加总：**Astra 143/210 → 68.1%，Fable 5.1 84/210 → 40.0%**。官方内部值与 BenchLM 两行镜像均一致；七说法主标签为“一致”2 条、“来源未完整披露”5 条，一手支撑 5/7。未重跑模型，不指控任何一方。

The released trial labels reproduce both official displays, and the frozen BenchLM mirror agrees. Of seven frozen claims, two official displays match and five lack complete source/run details. This is an arithmetic audit of existing public records, with no model reruns and no accusations.

结果入口：[REPORT.md](REPORT.md)（冻结首句、中英双语报告）、[results.json](results.json)（AP-01–AP-19 预测/重算/相符记录）、[figure1.png](figures/figure1.png)（七冻结说法＋两个官方重算值，按来源顺序，不排新榜）。

| Output / 交付物 | Contents / 内容 |
|---|---|
| [task_counts.csv](task_counts.csv) | 140 条逐系统/任务整数计数 |
| [task_job_counts.csv](task_job_counts.csv) | 420 条逐系统/任务/job 计数及公开试次主键 |
| [job_counts.csv](job_counts.csv) | 6 条 job 汇总及试次率 |
| [domain_counts.csv](domain_counts.csv) | 10 条域汇总与官方域字段核对 |
| [claims_table.csv](claims_table.csv) | 七说法及独立 S1a 的来源、日期类型、字段状态和单一主标签 |
| [analysis](analysis/) / [tests](tests/) | 独立双路径、Decimal、来源提取、任务簇 bootstrap、合成与产物核验 |
| [artifacts](artifacts/) | 全输入哈希清单、版本、预执行代码哈希、锁定提交证据及执行轨迹 |
| [DEVIATIONS.md](DEVIATIONS.md) | 实现错误、停止记录、重新冻结代码及重执行披露 |
| [x_post.md](x_post.md) / [x_post_cn.md](x_post_cn.md) | 未发布的英文与中文传播草稿；配图 figures/figure1.png |

公开协议锁定提交：[acd553f7c989c1141424f8de33515727b4a61086](https://github.com/empac666/ai4science-recheck-tbscience-scores/commit/acd553f7c989c1141424f8de33515727b4a61086)。[PREREG.md](PREREG.md)、[feasibility.md](feasibility.md) 与 [INPUTS_SHA256SUMS](INPUTS_SHA256SUMS) 保持锁定字节；锁定提交公开可读已核验，首次公开 push 的事件时间未独立恢复，不以 commit 日期替代，见 [public_lock.json](artifacts/public_lock.json)。

All 14 frozen input sizes and SHA-256 hashes match. CPython 3.13.5, NumPy 2.5.3, BeautifulSoup4 4.15.0, pdftotext 25.03.0 and Matplotlib 3.11.2 match the lock. Both 10,000-replicate paired task-cluster bootstrap designs were completed: non-stratified primary, stratified sensitivity. Intervals describe resampling and do not establish external-score significance or model superiority.

主计数来自两条重新解析原始 JSON 的独立路径，未共用求和函数、未导入可行性脚本。所有 AP 最终相符。已知基线曾在可行性阶段查看，本执行不声称盲态或未知发现。初始 AA/PDF 提取代码错误及辅助树核对误纳入 CI/归档样例均已修正，先保存诊断与原始代码、重新冻结哈希，再执行；[execution_history.json](artifacts/execution_history.json)、[execution_01](artifacts/execution_01/)、[execution_02](artifacts/execution_02/) 保留前两轮记录。

The initial extraction and auxiliary tree-check errors were implementation corrections after observed results; original code and results remain archived. No input, frozen source node, prediction, threshold, denominator or seed was changed. See the deviation log rather than treating the corrected execution as blind.

复现 / Reproduce（在仓库根目录，冻结输入位于上级只读缓存，不重抓现榜）：

```bash
python3 -m unittest tests.test_audit -v
python3 -m analysis.run --cache ../data_cache
python3 -m tests.check_artifacts
```

现有 [code_freeze.json](artifacts/code_freeze.json) 会在运行前后校验全部分析/测试/工具代码；不得覆盖历史冻结记录。依赖锁见 [requirements.txt](analysis/requirements.txt)，执行说明见 [analysis/README.md](analysis/README.md)。

仍未知：未读 S1 原帖、S2 原始页（冻结 HTTP 403）、外部逐试次与运行身份、完整任务字节身份、grader 有效性、Fable 单条详情（冻结 HTTP 404）。模型卡与官方的重复次数、AA agent 差异为事实，不解释差值因果；OpenAI 的 effort 选择操作仍未知。S1a 不替代 S1、不增加七说法分母；有理数兼容集合不代表恢复试次。

第三方原始 HTML/PDF/JSON、轨迹与环境配置不入库；所有输入只读，发布文件只含自制汇总与必要短串/元数据。本分支仅本地提交，不 push；传播草稿未发布。

历史方案与讨论：[pick.md](pick.md)、[response.md](response.md)、[response2.md](response2.md)、[agy_review.md](agy_review.md)、[grok_review.md](grok_review.md)、[agy_review2.md](agy_review2.md)、[grok_review2.md](grok_review2.md)。这些是锁定前材料，执行结论以 REPORT.md 和 results.json 为准。
