# 决策索引

| ADR | 状态 | 决策 | 冻结版本 |
|---|---|---|---|
| [[03_Decisions/ADR-001-dual-price-system]] | ACCEPTED | raw与point-in-time continuous双价格体系 | phase-2b2 |
| [[03_Decisions/ADR-002-snapshot-timing]] | ACCEPTED | 风险快照先冻结、后生效 | phase-2b2 |
| [[03_Decisions/ADR-003-entry-room]] | ACCEPTED | 压力分层与Entry Room | phase-2b2 |
| [[03_Decisions/ADR-004-setup-entry-decoupling]] | ACCEPTED | D-024 Setup生命周期与入场价值解耦 | phase-2b3 |
| [[03_Decisions/ADR-005-arbitrary-main-board-provider-boundary]] | ACCEPTED | D-025 任意主板单股票真实评价与Provider边界 | phase-2c1 |
| [[03_Decisions/ADR-006-multi-source-warehouse-reconciliation]] | ACCEPTED | D-026 多数据源行情仓库与显式对账 | phase-2c2a |

## Research checkpoints（非 ADR，不进入 production 冻结）

- FORWARD_EPOCH_0：overlay v0.1 hash `d527aa1d...`，audit v0.1 hash
  `43407eed...`，plan hash `0d1bb2b9...`；research branch
  `research/mainline-context-v01`，Draft PR #14；
  结论 `SYSTEMATIC_OVERLAY_BIAS_SUSPECTED=YES`；`SUPPORT_BREAK_V01=
  RESEARCH_INVALID_FOR_PROMOTION`；sector 仍为
  `LIMIT_UP_POOL_SECTOR_PROXY/LOW_CONFIDENCE`。
- MAINLINE CONTEXT V0.2 ACCEPTED：hash `9a53e500...`；
  `PIT_SUPPORT_FIX=ACCEPTED`；`CONTEXT_ENTRY_SEPARATION=ACCEPTED`；
  `OBSERVE_NOW_61_OF_78=NOT_SUITABLE_AS_HUMAN_SHORTLIST`；
  2026-08-03 FINAL HUMAN WATCH hash `8847f503...`。

新决策必须从 [[03_Decisions/ADR_TEMPLATE]] 创建，并在采纳后更新本索引、
[[01_Strategy/STRATEGY_MASTER]]、[[01_Strategy/RULE_CATALOG]]与
[[01_Strategy/CHANGELOG]]。
