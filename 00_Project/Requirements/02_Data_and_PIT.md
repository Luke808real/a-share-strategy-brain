# Data and PIT

## Primary data plane

ASL 是 primary data plane。系统通过 ASL adapter 读取 canonical contracts，再由
snapshot、universe、state 与策略平面消费。数据范围至少包括：

- daily
- 5m / minute
- preclose
- turnover
- ST
- suspension
- price limit
- corporate action
- adjustment factor
- historical universe
- provenance

数据源变化不得改变策略语义；语义来源仍是
[[01_Strategy/STRATEGY_MASTER]] 与 [[01_Strategy/RULE_CATALOG]]。

## Canonical contract

每个 canonical 事实都必须有来源、时间边界、质量状态与可追溯标识。缺字段、
provider 冲突、历史覆盖不足或质量未知时必须公开该限制，而不是在下游静默补齐。

## PIT and fail-closed rules

以下原则是强制的：

- NO FUTURE DATA：任一日期只消费当时已经可知且可用的数据。
- NO ABSENCE -> NORMAL：缺少不代表正常、非 ST、未停牌或没有事件。
- FAIL CLOSED：无法证明输入可靠或时间正确时，禁止把结果提升为可用 candidate。

历史 universe、ST、停牌、复权和涨跌停的语义必须使用对应日的可证明事实。任何
backfill、adapter 或 canonical 变更都需要重新验证其对下游的影响范围。
