# Candidate Rules

这里只保存尚未冻结的假设。稳定ID、状态与实现信息的唯一目录是
[[01_Strategy/RULE_CATALOG]]。下列ID必须保持`OBSERVED`或`PROPOSED`，不能被本文件
直接升级为FROZEN。

## 均线与压力

- `MA30_OVERHEAD` — 研究MA30在现价上方的空间约束。
- `MA30_DOWNTREND_OVERHEAD` — 研究下行MA30的动态压力。
- `MA120_OVERHEAD` — 观察MA120近压与后续成功率。
- `MA_CLUSTER_RECLAIM` — 观察强K线收复收敛均线簇。
- `MA20_MA30_PULLBACK` — 观察中期均线回踩后的再启动。
- `MA_RETEST_OVERDUE` — 研究长时间不回踩均线的追入风险。

## 损伤与修复

- `REPAIR_REQUIRED` — 结构受损后下一交易日是否需要修复。
- `REPAIR_FAILED` — 未修复应影响Entry Quality还是INVALID。
- `LARGE_BEARISH_DAMAGE` — 大阴线损伤但支撑未破的风险表达。
- `FAST_REPAIR` — 正向修复案例标签。
- `STRONG_RECLAIM` — 开盘近低、收盘近高并收复均线。

## 压力拒绝

- `REPEATED_UPPER_SHADOW` — 多次长上影的窗口与阈值。
- `RESISTANCE_REJECTION_CLUSTER` — 压力区反复冲高回落。
- `RESISTANCE_BREAKOUT` — 人工压力突破的观察标签。

## 低位与再启动

- `LOW_BASE_BREAKOUT` — 长期下跌后低位筑底突破。
- `LIMIT_UP_RELAUNCH` — 回踩后涨停式再启动。
- `CLOSE_NEAR_HIGH` — 收盘位置对后续表现的研究。

## 时间成本

- `TIME_COST_AGING` — 多日无状态推进的连续老化。
- `TIME_COST_STALE` — 是否只降低新建仓资格，或最终终止setup。

## 仅分钟数据

- `LATE_DAY_RAMP`
- `FAST_WASHOUT_RECOVERY`
- `OPENING_FAST_REPAIR`

这些规则需要分钟数据，当前日线Provider与策略引擎不得实现或推断。

## 进入ADR前的最低问题

1. 是否有明确输入和point-in-time计算方法？
2. 是否有成功与失败对照组，而非单一正向样本？
3. 影响setup_stage、is_entry_candidate、排序还是仅解释？
4. 缺失字段如何处理，是否会错误计零分？
5. 对历史信号日期和setup_id有何影响？
6. 是否需要重新生成黄金样本？
