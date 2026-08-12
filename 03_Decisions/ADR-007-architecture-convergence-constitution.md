---
type: strategy_decision
adr_id: ADR-007
title: 三仓架构收敛宪法（Three Planes / Seven Domains）
status: PROPOSED
decision_date: 2026-08-13
strategy_version: null
---

# ADR-007 三仓架构收敛宪法

> 说明：`decision_date` 目前记录提案日期；正式采纳日期由人工决策后更新。

## 原规则

- Brain 自身不执行选股、行情下载、回测或交易；`STRATEGY_MASTER` 是冻结策略的人类可读唯一真源。
- Runtime 实施冻结策略语义；数据链路经 canonical/warehouse 边界进入。
- ASL 已合入 main 的数据路径为 `ASL → ashare_lake.query → asl_query_adapter → snapshot → validator → state → strategy`，但 `ST_READY=NO`、`PROVENANCE_GAP=OPEN`、`PRODUCTION_CUTOVER=NO_GO`，未授权生产切换。

## 新观察

- `ARCHITECTURE_CONVERGENCE_V01`（SHA-256 `e2b467d89cdecb15c9cb18a74b81429caa66a8b8c602d47525afafd63669d064`）定义了长期目标态：三 Plane 分权、Runtime 七 Domain、依赖方向、真相所有权、Promotion 契约与 REF-R0→R8 分阶段收敛。
- 该架构书是目标态协议，不授权任何策略、Forward、Production、TradePlan、Live 或数据切换行为；重构轮次只做重构（REF-R0 基线已冻结并三读通过）。

## 决策

采纳三仓职责协议作为架构收敛的共同对齐目标：

1. **Data Plane（ashare-lake）** 只回答“市场事实上发生了什么”，拥有采集、适配器、回退、落湖、公司行为、历史 ST、停牌、日历、raw OHLCV/分钟线、复权事实、provenance、质量与 PIT 数据边界；不含 B1/B2/R9/setup_stage/SECOND_LAUNCH/watchlist/TradePlan 语义。
2. **Runtime Plane（a-share-limit-pullback）** 只回答“给定当前可知市场事实，策略系统如何计算”，拥有 canonical 消费者契约、Feature、setup 生命周期/State、eligibility/ranking/presentation、Replay/Daily、未来 Live 接口与 Evidence；不决定研究观察是否升级为正式规则。
3. **Control Plane（a-share-strategy-brain，本仓）** 只回答“我们为什么这么做、当前相信什么、什么已冻结、什么仍是假设”，拥有 Strategy/Research/Decision/Project/Promotion/Agent 真相；不执行选股、行情下载、回测或交易。
4. 单一策略真源只在 `01_Strategy/`；Runtime 不得在启动时动态读取 Brain 构建策略（AC-10），规则升级必须经 ADR → Frozen Contract → Code Change → Regression → Human Review。
5. Runtime 目标七域为 Domain/Data/Features/State/Selection/Runtime/Evidence + Interfaces，依赖只允许 domain ← data、features ↑ state ↑ selection ↑ runtime ↑ interfaces 及 runtime → evidence；Domain 不 import 高层，Feature 不 import selection/runtime/ASL 内部，State 不 import selection/filesystem/provider，Selection 不 import raw provider/ASL/filesystem。
6. Promotion 生命周期冻结为 OBSERVATION → HYPOTHESIS → RESEARCH_CANDIDATE → SUPPORTED → PROMOTION_CANDIDATE → ADR_APPROVED → FROZEN_CONTRACT → IMPLEMENTED → GOLDEN_VERIFIED → RUNTIME_ACTIVE；`SUPPORTED != PROMOTED`。Brain→Runtime 必须携带 STRATEGY_VERSION/ADR_ID/RULE_IDS/FEATURE_IDS/语义与 artifact 预期/兼容性/迁移与 Golden 要求；Runtime→Brain 必须返回 IMPLEMENTATION_SHA/测试/差分/Golden/artifact hash/契约版本/评审结果。
7. 收敛按 REF-R0→R8 逐轮独立验收；每轮 Refactor PR 必须回答 TASK_ID/BASE_SHA/允许文件/五类变化标志/INVARIANT/差分与 Golden/性能差/前后 SHA，且禁止混入新因子、阈值、系数、规则、数据源、生产或 Forward 行为。

## 被否决方案

- 一次性把目录改成目标形态并删除旧实现：违反 Strangler 与 REF-R8 删除门禁。
- Runtime 在启动时 clone Brain 并解析 `STRATEGY_MASTER.md` 动态构建策略：违反 AC-10 与单一真源协议。
- 由 Data Plane 或 Runtime 自行产生策略真相副本：违反单一策略真源。

## 对历史信号的影响

无。本 ADR 只确立架构协议；不改写历史 snapshot、generation、episode、outcome、receipt、hash 或 forward epoch。

## 代码影响

- 本仓：无代码路径变化，仅决策记录。
- Runtime：后续轮次新增 `docs/architecture-constitution.md` 与 `tests/test_architecture_constitution.py`（只断言当前已成立的规则与冻结配置哈希）。
- ASL：后续轮次补充数据边界文档；不改变查询契约。

## 配置影响

无。`config/strategy.yaml` 与 `config/trade_plan.yaml` 哈希保持不变。

## 测试影响

本仓 vault 校验须通过；无行为测试变化。REF-R1 验收证据为三仓文档一致、Runtime 冻结引用差分零变化。

## 是否需要重新生成黄金样本

否。零行为、零策略、零数据/schema/artifact 变化。

## 证据与不确定性

- 架构书附件 SHA-256：`e2b467d89cdecb15c9cb18a74b81429caa66a8b8c602d47525afafd63669d064`。
- REF-R0 基线证据：Runtime 任务分支 `codex/architecture-convergence-v01` 的 `.goal-task/architecture-convergence-v01/ref-r0-baseline-v03.md`（全市场重建输出哈希 `9abb16e4…` 与冻结 `FULL_MARKET_HASH` 一致）。
- 不确定性：本 ADR 为 PROPOSED，须人工审核后更新状态与 `DECISION_INDEX.md`；REF-R3 完成前 ASL 生产切换仍受 `ST_READY/PROVENANCE_GAP/CUTOVER` 三门阻塞。
