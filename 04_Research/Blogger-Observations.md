# 博客观察记录

> 本文件保存原始人工观察，不等于策略事实。候选规则状态以
> [[01_Strategy/RULE_CATALOG]] 为准。

## 水发燃气

### 原始观察

- MA30明显位于股价上方；
- 跌破支撑后需要下一交易日快速修复；
- 若继续走弱，应转为S点或失效处理。

### 候选规则

`MA30_OVERHEAD`、`MA30_DOWNTREND_OVERHEAD`、`REPAIR_REQUIRED`、
`REPAIR_FAILED`。

### 不确定性

尚无明确MA30距离、斜率、修复幅度和修复期限，也缺少失败对照组。

## 新亚电缆

### 原始观察

- 支撑未完全跌破；
- 大阴线破坏短线形态；
- 下一交易日应出现强修复，否则降低持仓预期。

### 候选规则

`LARGE_BEARISH_DAMAGE`、`REPAIR_REQUIRED`。

### 不确定性

需区分结构失效、普通波动和仅影响Entry Quality的损伤，不能让单根阴线自动INVALID。

## 翠微股份

### 原始观察

- 多次长上影；
- 压力区反复受阻；
- 长时间不回踩均线；
- 冲高优先减仓，不宜继续追入。

### 候选规则

`REPEATED_UPPER_SHADOW`、`RESISTANCE_REJECTION_CLUSTER`、
`MA_RETEST_OVERDUE`。

### 不确定性

需冻结长上影定义、统计窗口、压力簇距离及“逾期”交易日数。

## 恒为科技

### 原始观察

多个交易日没有状态推进，对短线策略产生明显时间成本。

### 候选规则

`TIME_COST_AGING`、`TIME_COST_STALE`。现有`EXPIRED`已经是FROZEN的setup
终止语义，仅表示离开锚点有效窗口；本观察不能直接重定义该ID。

### 不确定性

需要比较不同阶段的合理等待时间，并区分候选排序降级和setup终止。

## 尾盘慢拉案例

### 原始观察

尾盘慢拉、快速洗盘后恢复、开盘快速修复可能包含日线无法识别的路径信息。

### 候选规则

`LATE_DAY_RAMP`、`FAST_WASHOUT_RECOVERY`、`OPENING_FAST_REPAIR`。

### 数据边界

以上三项明确需要分钟数据。当前日线程序不得实现、推断或用日线OHLC替代日内路径。

## 研究纪律

所有观察先进入 [[04_Research/Candidate-Rules]]，补齐成功/失败对照样本后才能创建ADR。
