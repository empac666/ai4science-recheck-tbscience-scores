# R11lock 第二轮修订回应

2026-10-10；版本 **R11lock**。回应 [agy_review2.md](agy_review2.md) 与 [grok_review2.md](grok_review2.md)。三项must-fix全部落实；下面逐条说明采纳与取舍。本文记录规则修订，不是正式分析结果。

| 意见 | 处理与理由 | 定稿位置 |
|---|---|---|
| agy R2-01 should-fix | 与grok R2-03合并处理：区分配置事实与内部追踪元数据，明确运行身份及版本的操作定义，保留已见agent/试次数差异。未采用“核心配置不同即可绕过缺身份门槛”的建议：任务要求采用grok的严格身份规则，且缺身份时不能确认同批运行。优先级2只适用于必要字段完整的对比；当前五对明确停在1，2–5不适用，避免条件互斥留给执行解释。 | [PREREG §4](PREREG.md#4-指标算术与来源判据)运行身份、优先级及五对预测表；[feasibility §4](feasibility.md#4-执行预算与降级) |
| agy R2-02 should-fix | 两段清理的实质要求采纳；未采用同时兼容ASCII与Unicode分隔符的建议。按任务及grok R2-01，将分隔符写死为字面 `+/-`，恰好一次；两段各strip并去全部星号、百分号、空白，保留末尾零。缺少、重复分隔符或非法数字串即提取失败并停止该项。这样与冻结原始字段一致，避免静默替代。 | [PREREG §4](PREREG.md#4-指标算术与来源判据)、[tools/audit_rules.py](tools/audit_rules.py) |
| agy R2-03 nit | 采纳消除分数重复的要求，与grok R2-05一致收敛为精度50 Decimal定点字符串。raw占位符只填百分数数字串，无分数、百分号或循环节；整数比只由模板外围保留，另存结果字段。 | [PREREG §6](PREREG.md#6-停止传播与交付) |
| agy R2-04 nit | 采纳：HTTP Last-Modified在类型上满足日期字段提取规范，同时限定为服务器修改时间，不证明出版日或运行日。 | [PREREG §4](PREREG.md#4-指标算术与来源判据)、[feasibility §2](feasibility.md#2-冻结提取路径与一手支撑) |
| grok R2-01 must-fix | 全部采纳：分隔符字面 `+/-`；两段清理；冻结前段 `68.1`/`40.0`、后段 `3.2`/`3.4`。§2A披露原始stderr数字串 `3.2164475807033743`/`3.380617018914066`。计算SE与原始stderr分别一位HALF_UP量化成定点串，须与后段三方完全相等才相符；缺分隔符提取失败并停止该项。 | [PREREG §2](PREREG.md#2-已知基线事前冻结的待检验项)、[§4](PREREG.md#4-指标算术与来源判据)、[§5](PREREG.md#5-区间与次级汇总)、[tools/audit_rules.py](tools/audit_rules.py) |
| grok R2-02 must-fix | 全部采纳：镜像与官方score均先量化一位HALF_UP，`40`/`40.0`原串区别只留事实列。sourceModelId、model、harness、reasoningEffort、externalUrl、sourceUrl及provenance完整字符串全部精确比较，冻结provenance对象字段与整数total。`M_A`/`M_F`分别编号AP-05/06，均预测“一致”；未来results逐项保存预测、实际抽取、量化分数、字段命中及是否相符。 | [PREREG §2](PREREG.md#2-已知基线事前冻结的待检验项)、[§4](PREREG.md#4-指标算术与来源判据)、[feasibility §2](feasibility.md#2-冻结提取路径与一手支撑) |
| grok R2-03 must-fix | 全部采纳：运行身份须同一原文同时命中官方row_id与对应榜单运行；模型/agent/effort不能替代。系统级配置字段只限模型、agent、effort操作、试次数、指标公式、数据集版本；单trial版本/verifier/timeout等不能触发。冻结事实state词表与已见字面；S1a/S2/S3/S5/S6逐对编号AP-07至AP-11，均预测“来源未完整披露”。八个有理数集合逐项编号AP-12至AP-19；交付函数循环全部 `0≤K≤N`，以Decimal半末位边界交叉乘N比较，计算中不含预测K。results记录预测/独立枚举/相符，偏离保存并停止该项解释。 | [PREREG §4](PREREG.md#4-指标算术与来源判据)、[§2](PREREG.md#2-已知基线事前冻结的待检验项)、[tools/audit_rules.py](tools/audit_rules.py) |
| grok R2-04 should-fix | 采纳：优先级5使用独立标签“同配置下算术不符”；五对均预测停在1，表前明确2–5不适用，因此3–5也不适用。 | [PREREG §4](PREREG.md#4-指标算术与来源判据) |
| grok R2-05 should-fix | 采纳：首句保留外围整数比K/210，raw仅填精度50 Decimal定点字符串；固定计算顺序及ROUND_HALF_EVEN上下文，定点串仅删除小数末尾零与空小数点，不选循环节写法。精确性来自整数比，50位字符串说明为计算近似；Fable raw为 `40`、一位展示 `40.0`。 | [PREREG §6](PREREG.md#6-停止传播与交付)、[tools/audit_rules.py](tools/audit_rules.py) |
| grok R2-06 should-fix | 采纳：CPython或NumPy版本任一不一致即停止主区间及分层敏感性；BeautifulSoup或Matplotlib不一致记偏离；pdftotext不一致使S5提取失败，不改用其他解析器。 | [PREREG §3](PREREG.md#3-输入资格与独立实现)、[feasibility §3](feasibility.md#3-配置背景与版本锁) |
| grok R2-07 nit | 采纳：S5以冻结唯一句命中为条件，印刷页码与pdftotext页序只作定位；唯一句已命中时页序差异不构成提取失败。 | [feasibility §2](feasibility.md#2-冻结提取路径与一手支撑) |
| grok R2-08 nit | 采纳：事前限定嵌入串仅与133/210的15位HALF_UP结果相同、不等于精确分数；精确不等用整数交叉乘积确认。此算术陈述不进来源主标签，不解释未读S1。 | [PREREG §4](PREREG.md#4-指标算术与来源判据) |

上级目录的PREREG、feasibility、response在修订前与仓库相同，无额外更新需要导入；仓库内R11lock文件为定稿。第一轮 [response.md](response.md) 保留为历史，冲突处以本轮规则为准。两份第二轮评审已原样复制入库。[README.md](README.md) 明确锁定为首次 push 到公开 GitHub 的 main 分支提交；[DOC_SHA256SUMS](DOC_SHA256SUMS) 覆盖全部公开文档、输入元数据及工具代码，排除清单自身。

本轮只交付规则函数并作合成案例验证、文档一致性和公开文本检查，不执行真实数据计数、兼容集合枚举、主标签判定、区间或模型。完整独立执行代码仍须在正式分析前冻结哈希。未push、未建远程、尚无公开锁定时间戳。
