# Strategy and Setup

冻结的定义、阈值和 setup_stage 真源在
[[01_Strategy/STRATEGY_MASTER]] 与 [[01_Strategy/RULE_CATALOG]]。本文件只定义
系统需要支持的产品 lifecycle，不复制或改写冻结规则。

## Product lifecycle

系统需要能够表达以下概念生命周期：

NO_SETUP
→ T0
→ PULLBACK
→ B1
→ B2_READY
→ B2_CONFIRMED
→ SECOND_LAUNCH
→ TAKE_PROFIT
→ FAILED
→ EXPIRED

该产品视图不能反向改写冻结的 LIMIT_ANCHOR、WATCH_PULLBACK、B1_READY、
B2_READY、B2_CONFIRMED、INVALID 或 setup/entry 分离语义。遇到名称或语义差异时，
冻结真源优先。

## Required concepts

每个可跟踪 setup 应能保存或引用：

- stable setup_id
- T0 / anchor reference
- setup age
- TTL state
- repeat confirmation
- first activation event
- failure reason
- expiration / supersession state

上述记录必须 point-in-time，并可回溯到其 snapshot、state 与输入事实。

## Unresolved semantic boundary

TTL 与 suspension-age 当前仍有 unresolved semantic conflict。任何 Agent 不得在
本需求文件、CURRENT_STATE 或实现中自行决定其处理方式；它在
[[00_Project/BLOCKERS]] 关闭前保持待核对状态。
