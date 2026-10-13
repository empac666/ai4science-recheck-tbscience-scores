# Execution deviations / 执行偏离

实现修正与重执行：首轮 S1a 与 S5 提取失败，AP-07/AP-10/AP-12/AP-17 的 observed=null、matches=false；受影响项解释停止，其他独立结果保留。
AA 原正则匹配了同一最内层摘要中后续模型的分数；修正为把分数绑定到 GPT-6 Astra (Max)。PDF 原定位同时命中目录和正文；修正为 pdftotext -layout 的独立 §8.7 正文标题，再核对同一句。冻结文件、节点路径、预测、阈值与分母均未改变。
首轮代码、哈希、results.json、来源表及执行元数据完整保存于 artifacts/execution_01/；详见 artifacts/execution_history.json。最终执行代码已另行冻结后重执行；这是看过首轮结果后的实现修正，不声称盲态。
首轮自动生成报告曾错误宣称全部 AP 完成，现已由明确反映实际状态的最终 REPORT.md 取代；首轮诊断记录不删除。
Implementation corrections after an observed first execution are documented. No scientific protocol, input, extraction-node specification, prediction, threshold, denominator or seed changed. Original failures and original code are retained; the corrected code was frozen before re-execution.
第二轮辅助 task.toml 树核对误含 CI/归档/工具样例（154），现限定冻结基准正式 tasks/ 目录的 70 个任务；正式标签计数与全部 AP 未改变。第二轮结果与全部代码另存 artifacts/execution_02/。最终图删除补充 AA 数字，严格只显示七说法加两个重算值；英文链接置于第二条回复，总计三帖。Final review corrections were frozen before execution epoch 3; prior executions remain archived.
