# 规则目录

状态只能使用：`OBSERVED`、`PROPOSED`、`ACCEPTED`、`REJECTED`、`FROZEN`、
`DEPRECATED`。`影响setup_stage`与`影响is_entry_candidate`分别记录结构生命周期
和新建仓资格，不得混用。

| rule_id | 名称 | 适用层级 | 状态 | 输入字段 | 判断语义 | 影响setup_stage | 影响is_entry_candidate | 代码实现 | 对应测试 | 来源决策 |
|---|---|---|---|---|---|---|---|---|---|---|
| ANCHOR_LOW_POSITION | 锚点低位 | Anchor评分 | FROZEN | point-in-time position_120 | 锚点前120日位置分层评分 | 否 | 间接排序 | 是 | test_strategy_engine | [[03_Decisions/ADR-001-dual-price-system]] |
| B1_SUPPORT_TOUCH | B1触及支撑 | B1结构 | FROZEN | low, high, SupportSnapshot | K线区间与支撑簇相交 | 是 | 是 | 是 | test_strategy_engine | [[03_Decisions/ADR-002-snapshot-timing]] |
| B2_CLOSE_ABOVE_TRIGGER | B2收盘站稳 | B2结构 | FROZEN | close, B2TriggerSnapshot | 收盘不低于已冻结且生效的触发价 | 是 | 是 | 是 | test_strategy_engine | [[03_Decisions/ADR-002-snapshot-timing]] |
| INVALID_SUPPORT_BREAK | 有效跌破支撑 | 结构失效 | FROZEN | close, SupportSnapshot | 收盘越过支撑下沿及配置buffer | 是 | 是 | 是 | test_replay | [[03_Decisions/ADR-002-snapshot-timing]] |
| ENTRY_ROOM_NONE | 无入场空间 | Entry Quality | FROZEN | entry_reference, target_s1.low | target下沿不高于入场参考价 | 否 | 是 | 是 | test_strategy_engine | [[03_Decisions/ADR-003-entry-room]] |
| EXPIRED | setup过期 | setup终止 | FROZEN | anchor window, trade_date | 锚点离开有效窗口且未被新锚点替代 | 是 | 是 | 是 | test_replay | [[03_Decisions/ADR-003-entry-room]] |
| SETUP_ENTRY_DECOUPLING | 结构与入场价值解耦 | 生命周期边界 | FROZEN | B1/B2 conditions, S1, risk/reward, Entry Room | setup阶段只读取结构条件，压力与入场价值不得反向改写阶段 | 是（仅结构输入） | 是（单独派生） | 是 | test_strategy_engine, test_replay | [[03_Decisions/ADR-004-setup-entry-decoupling]] |
| SETUP_QUALITY_SCORE | 结构质量评分 | Setup Quality | FROZEN | anchor, pullback, support, volume, kline, MA, B1/B2 | 评分不读取S1、risk/reward或Entry Room | 否 | 间接排序 | 是 | test_strategy_engine | [[03_Decisions/ADR-004-setup-entry-decoupling]] |
| ENTRY_QUALITY_SCORE | 新建仓价值评分 | Entry Quality | FROZEN | setup_quality, Entry Room, risk/reward, events, data quality | 仅派生入场价值，不修改setup_stage | 否 | 是 | 是 | test_strategy_engine | [[03_Decisions/ADR-004-setup-entry-decoupling]] |
| MAIN_BOARD_SINGLE_STOCK_SCOPE | 主板单股接入范围 | 输入与Provider边界 | FROZEN | six-digit code, exchange prefix | 仅允许配置的沪深主板前缀；在Provider调用前拒绝非范围代码 | 否 | 否 | 是 | test_instruments, test_cli | [[03_Decisions/ADR-005-arbitrary-main-board-provider-boundary]] |
| PROVIDER_QUALITY_PROPAGATION | Provider质量传播 | 数据质量边界 | FROZEN | provider metadata, quality flags, actual bar date | 不伪造缺失行情；重复与畸形字段显式记录，replay以STALE_DATA表示陈旧末日 | 否 | 是（UNUSABLE时否） | 是 | test_real_providers_offline, test_replay | [[03_Decisions/ADR-005-arbitrary-main-board-provider-boundary]] |
| LOW_BASE_BREAKOUT | 低位平台突破 | 案例特征 | OBSERVED | price history, position | 长期下跌后低位筑底并向上突破 | 否 | 否 | 否 | — | [[02_Cases/Success/002640-2026-07-27]] |
| MA_CLUSTER_RECLAIM | 收复均线簇 | 案例特征 | OBSERVED | close, MA5/10/20/30 | 单根强K线站上收敛均线簇 | 否 | 否 | 否 | — | [[02_Cases/Success/002640-2026-07-27]] |
| CLOSE_NEAR_HIGH | 收盘接近最高 | 案例特征 | OBSERVED | high, low, close | close_location_value接近1 | 否 | 否 | 否 | — | [[04_Research/Success-Case-Features]] |
| MA120_OVERHEAD | MA120上方压力 | Entry Quality研究 | OBSERVED | close, MA120 | MA120位于现价上方且距离较近 | 否 | 否 | 否 | — | [[02_Cases/Success/002640-2026-07-27]] |
| MA20_MA30_PULLBACK | 回踩MA20/30 | 案例特征 | OBSERVED | low, close, MA20, MA30 | 调整低点接近中期均线后重新走强 | 否 | 否 | 否 | — | [[04_Research/Success-Case-Features]] |
| LIMIT_UP_RELAUNCH | 涨停再启动 | 案例特征 | OBSERVED | OHLC, pct_change | 回踩后以涨停K线重新启动 | 否 | 否 | 否 | — | [[02_Cases/Success/600199-2026-07-28]] |
| RESISTANCE_BREAKOUT | 压力突破 | 案例特征 | OBSERVED | close, prior resistance | 收盘站上人工观察压力 | 否 | 否 | 否 | — | [[02_Cases/Success/600199-2026-07-28]] |
| FAST_REPAIR | 快速修复 | 案例特征 | OBSERVED | OHLC, moving averages | 回踩后快速收复MA5/10 | 否 | 否 | 否 | — | [[02_Cases/Success/002891-2026-07-28]] |
| STRONG_RECLAIM | 强势收复 | 案例特征 | OBSERVED | open, high, low, close, MA | 开盘近低点且收盘近高点并收复均线 | 否 | 否 | 否 | — | [[02_Cases/Success/002891-2026-07-28]] |
| MA30_OVERHEAD | MA30高悬 | 风险候选 | PROPOSED | close, MA30 | MA30明显位于现价上方，可能限制修复空间 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| MA30_DOWNTREND_OVERHEAD | 下行MA30压制 | 风险候选 | PROPOSED | MA30 slope, close | 下行MA30在现价上方形成动态压力 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| REPAIR_REQUIRED | 次日修复要求 | 风险候选 | PROPOSED | support break, next-day OHLC | 结构受损后下一交易日需快速修复 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| REPAIR_FAILED | 修复失败 | 失效候选 | PROPOSED | next-day close, support, MA | 应修复而未修复时降低预期或失效 | 待研究 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| LARGE_BEARISH_DAMAGE | 大阴线损伤 | 风险候选 | PROPOSED | OHLC, volume, MA | 大阴线破坏短线形态但未必跌破支撑 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| REPEATED_UPPER_SHADOW | 多次长上影 | 压力候选 | PROPOSED | upper shadow sequence | 多个交易日长上影可能表示压力反复拒绝 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| RESISTANCE_REJECTION_CLUSTER | 压力拒绝簇 | 压力候选 | PROPOSED | highs, closes, S1 | 相近压力区域多次冲高回落 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| MA_RETEST_OVERDUE | 均线回踩逾期 | 时间候选 | PROPOSED | trade days, MA distance | 长时间不回踩均线可能提高追入风险 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| TIME_COST_AGING | setup时间老化 | 时间候选 | PROPOSED | stage history, trade days | 多日无阶段推进产生时间成本 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| TIME_COST_STALE | setup停滞 | 时间候选 | PROPOSED | stage history, trade days | 超过候选窗口后不再适合短线新建仓 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| LATE_DAY_RAMP | 尾盘慢拉 | 分钟研究 | PROPOSED | minute bars | 尾盘缓慢拉升的日内路径 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| FAST_WASHOUT_RECOVERY | 快速洗盘修复 | 分钟研究 | PROPOSED | minute bars | 日内快速下探后收回关键位 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |
| OPENING_FAST_REPAIR | 开盘快速修复 | 分钟研究 | PROPOSED | minute bars | 开盘后快速收复前一日损伤 | 否 | 待研究 | 否 | — | [[04_Research/Blogger-Observations]] |

## 维护规则

- 稳定ID不得重新解释；语义变化应新建ID或ADR。
- OBSERVED/PROPOSED不得写入冻结策略总纲。
- 任何状态变化必须由ADR记录，并同步测试与CHANGELOG。
