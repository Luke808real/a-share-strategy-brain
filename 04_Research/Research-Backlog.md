# 研究待办

## P0：数据与对照组

- 为三个成功案例补齐完整日线、成交量、涨停池和后续5/10/20日表现；
- 每个成功标签至少收集同定义失败样本；
- 建立修复成功、修复失败与自然波动三组对照；
- 核对截图日期、股票名称与人工结论。

## P1：可日线验证

- 冻结MA30_OVERHEAD距离和斜率候选定义；
- 定义LARGE_BEARISH_DAMAGE而不与INVALID重复；
- 定义REPEATED_UPPER_SHADOW的交易日窗口；
- 比较TIME_COST_AGING对Entry Quality与setup终止的不同处理；
- 冻结候选特征的分母、缺失值和point-in-time口径。

## P2：需要新数据边界

- 分钟数据研究LATE_DAY_RAMP；
- 分钟数据研究FAST_WASHOUT_RECOVERY；
- 分钟数据研究OPENING_FAST_REPAIR。

这些项目只列为研究待办，不授权修改当前Provider或策略引擎。

## ADR触发条件

有明确规则语义、足够成败对照、历史信号影响分析和预期测试后，才从
[[03_Decisions/ADR_TEMPLATE]]创建正式决策。
