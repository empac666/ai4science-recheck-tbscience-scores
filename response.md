# R11fix 修订回应

2026-10-10；版本 **R11fix-1**。分别回应 [agy_review.md](agy_review.md) 与 [grok_review.md](grok_review.md)。所有must-fix的实质要求已落实；建议规则冲突时采用grok的更严格封闭规则。本文是第一轮修订历史记录，不是正式分析结果。第二轮定稿以 [response2.md](response2.md) 和R11lock版 [PREREG.md](PREREG.md) 为准；本表中的旧分隔符、首句raw表示、兜底标签及版本偏离规则已被第二轮规则替代。

| 意见 | 处理方式 | 修改位置 |
|---|---|---|
| agy R-01 must-fix | 定性为已有数据独立审计规程；独立分开已知基线A与冻结待检验B，公开锁定不早于查看 | [PREREG §2](PREREG.md#2-已知基线事前冻结的待检验项)、[README](README.md)、[feasibility §1](feasibility.md#1-冻结与已知信息) |
| agy R-02 must-fix | 纳入封闭有理数检验，报告完整兼容分子集合。未采纳全来源统一D={70,210,700}与新增来源标签：它允许借用另一原文分母、混淆兼容性与归因，故按grok R-06限制同原文N，Vals仅假定70/210方案列，S1/S2不重构 | [PREREG §4](PREREG.md#4-指标算术与来源判据)有理数检验表 |
| agy R-03 must-fix | 冻结每个对比对，单一主标签/固定优先级。未采用建议的“重构优先于披露”顺序：缺必要字段应先停止归因；兼容集合另列，不作来源标签 | [PREREG §4](PREREG.md#4-指标算术与来源判据)冻结对比对与优先级表 |
| agy R-04 should-fix | 逐字冻结对账重加总首句，写明未重跑模型、整数/精确百分数/一位展示、官方内部与镜像分判 | [PREREG §6](PREREG.md#6-停止传播与交付)首句 |
| agy R-05 should-fix | 显示算法全集仅HALF_UP/HALF_EVEN/DOWN，写原像端点，列全部命中；主值及有理数仅HALF_UP | [PREREG §4](PREREG.md#4-指标算术与来源判据)舍入规则 |
| agy R-06 should-fix | 主区间明确非分层、说明跨域无权重经验分布假设；固定域簇分层仅敏感性、另seed，不挑区间 | [PREREG §5](PREREG.md#5-区间与次级汇总)、[feasibility §3](feasibility.md#3-配置背景与版本锁) |
| agy R-07 should-fix | OpenAI全局最佳固定effort／逐任务oracle包络线均列未知；不能当确认配置或因果 | [PREREG §1](PREREG.md#1-问题与冻结记录)、[pick §1](pick.md#1-七说法与独立补充记录) |
| agy R-08 nit | 历史.html文件实际PDF，以二进制PDF流和pdftotext解析，不用HTML解析器 | [PREREG §3](PREREG.md#3-输入资格与独立实现)、[feasibility §2](feasibility.md#2-冻结提取路径与一手支撑) |
| agy R-09 nit | 实际环境精确锁CPython3.13.5、NumPy2.5.3及解析/绘图版本；变化记偏离 | [PREREG §3](PREREG.md#3-输入资格与独立实现)、[feasibility §3](feasibility.md#3-配置背景与版本锁) |
| grok R-01 must-fix | AP-01/02给出双路径143/84预测；results.json保存预测/实测/相符；任一路径偏离即保存并停止，不写成未知发现 | [PREREG §2](PREREG.md#2-已知基线事前冻结的待检验项)、[PREREG §6](PREREG.md#6-停止传播与交付) |
| grok R-02 must-fix | 首句逐字冻结必填整数、未舍入精确十进制、一位展示和两类判定词表；同句限定公开标签/未重跑/算术边界，外部数字不得入句；镜像失败不改官方 | [PREREG §6](PREREG.md#6-停止传播与交付)、[PREREG §4](PREREG.md#4-指标算术与来源判据)主算术判定 |
| grok R-03 must-fix | S1未读X63与S1a AA63.3分开；未读不入分子、不由原像相交解释原帖；图仍七原说法+两重算，补充只在来源表 | [PREREG §1](PREREG.md#1-问题与冻结记录)、[PREREG §4](PREREG.md#4-指标算术与来源判据)、[pick §1](pick.md#1-七说法与独立补充记录) |
| grok R-04 must-fix | 一手定义固定五项、任缺为未达；冻结逐文件路径/字符串/日期类型；OpenAI仅渲染不计，七数原始字节上限5/7，S1a不补S1 | [feasibility §2](feasibility.md#2-冻结提取路径与一手支撑)、[PREREG §4](PREREG.md#4-指标算术与来源判据)、[INPUTS_SHA256SUMS](INPUTS_SHA256SUMS) |
| grok R-05 must-fix | 外部五对仅对相应官方，官方展示/镜像各自冻结；缺必要字段→完整配置不同→同原值舍入→原像兼容，兜底披露；一个主标签，差异事实另列，不补对 | [PREREG §4](PREREG.md#4-指标算术与来源判据)优先级表 |
| grok R-06 must-fix | 仅同原文N；AA210、PDF700、官方210，Vals70/210仅假定；64.6不借N。HALF_UP/原精度/原像封闭枚举，完整集合含空集，预期集合披露；不恢复试次、不用百分数乘N填主分子 | [PREREG §4](PREREG.md#4-指标算术与来源判据)有理数表、[pick §1](pick.md#1-七说法与独立补充记录) |
| grok R-07 must-fix | 区间/SE限官方标签，不判外部显著性/正确性，不由作者±重叠推显著性；AP-03是已知K的SE预测。原accuracy_stderr是未量化数值，先与计算SE各一位HALF_UP，再同时等于±显示串，避免长串与短串直接比 | [PREREG §5](PREREG.md#5-区间与次级汇总)、[PREREG §2](PREREG.md#2-已知基线事前冻结的待检验项) |
| grok R-08 should-fix | 精度50 Decimal(K)/210×100，量化0.1；二进制浮点附属对照经Decimal.from_float和限定三算法记录相符/偏差；去±前段星号/百分号/空白保留末尾零；accuracy锁0–100、1e-10个百分点 | [PREREG §4](PREREG.md#4-指标算术与来源判据) |
| grok R-09 should-fix | 披露id/agent/effort、3vs10、AA、OpenAI、当前Vals、404、只抽1条、未锁字节及平衡设计；这些事实已约束次级标签 | [PREREG §2](PREREG.md#2-已知基线事前冻结的待检验项)、[feasibility §1](feasibility.md#1-冻结与已知信息) |
| grok R-10 should-fix | 口径复核只限同批官方试次，平衡设计标恒等式；外部无成对试次，不用口径标签解释差量 | [PREREG §4](PREREG.md#4-指标算术与来源判据)、[PREREG §5](PREREG.md#5-区间与次级汇总) |
| grok R-11 should-fix | 固定pass@1/pass@3公式；BenchLM仅leaderboard两行；Vals仅隐藏公告，内嵌Vals表不作09-11证据；当前40.00另列数值相同/身份未建立 | [PREREG §4](PREREG.md#4-指标算术与来源判据)、[feasibility §2](feasibility.md#2-冻结提取路径与一手支撑)、[PREREG §6](PREREG.md#6-停止传播与交付) |
| grok R-12 should-fix | 图固定七数+两官方重算，不加背景/排序/显著性；nearly twice不换算；一条配置不外推；17行只锁2id、10-09有限样本；禁止import可行性、两路径共用求和；三文档同一次查看 | [PREREG §1](PREREG.md#1-问题与冻结记录)、[PREREG §2](PREREG.md#2-已知基线事前冻结的待检验项)、[PREREG §3](PREREG.md#3-输入资格与独立实现)、[PREREG §6](PREREG.md#6-停止传播与交付) |
| grok R-13 nit | NumPy精确版及percentile linear；tb_news冻结但不参与终点；显示串清理；预算未计时，8小时硬停、区间未完省略 | [PREREG §3](PREREG.md#3-输入资格与独立实现)、[PREREG §4](PREREG.md#4-指标算术与来源判据)、[PREREG §5](PREREG.md#5-区间与次级汇总)、[feasibility §4](feasibility.md#4-执行预算与降级) |

全部should-fix/nit实质建议均采纳。两项未采用的具体建议（agy统一分母全集、建议归因排序）及理由已逐条写明；不留下开放算法或事后标签。

公开锁定前仍有边界：尚无公开push时间戳；独立执行代码和主分析尚待之后冻结/执行；外部逐试次/运行身份、未读原帖、OpenAI原始页和精确effort操作、任务字节锁仍缺失。它们按协议保留未知，不阻断现有官方输入的独立计数；不能据此升级因果结论。本轮不处理这些外部缺失、不跑主分析。
