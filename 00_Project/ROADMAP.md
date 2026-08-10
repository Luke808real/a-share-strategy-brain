# Roadmap

阶段状态只描述项目规划位置。详细 current facts、open blocker 和下一 gate 请读取
[[00_Project/CURRENT_STATE]]、[[00_Project/BLOCKERS]] 与
[[00_Project/AGENT_HANDOFF]]。

## PHASE A — Data Foundation

GOAL：建立可信、可追溯的 ASL → adapter → canonical 数据基础。

STATUS：closing。

DONE：数据平面、PIT 与 quality-gate 合同已定义。

EXIT GATE：当前 bounded historical ST backfill 及 post-write audit 关闭，且相关
provenance 与质量证据经独立审查通过。

NOT IN SCOPE：策略阈值修改、候选制造、R9、Forward、Production。

## PHASE B — Snapshot / State

GOAL：建立可重放、可追溯的 snapshot、universe 与 state。

STATUS：integration / closure。

DONE：状态平面的 deterministic、idempotent、full / incremental parity 要求已定义。

EXIT GATE：新 ASL facts 上的重建验证和 lineage 证据完成。

NOT IN SCOPE：绕过数据 gate 的 state generation 或策略变更。

## PHASE C — Setup Engine

GOAL：在冻结语义下实现可审计的 setup accumulator。

STATUS：integration / closure。

DONE：setup 生命周期、冻结真源与 unresolved TTL 边界已分离记录。

EXIT GATE：ACTIVE_SETUP 正式产出并通过冻结语义、PIT 和 lineage 验证。

NOT IN SCOPE：自行决定 TTL suspension-age 语义或改变 B1/B2 阈值。

## PHASE D — Candidate Engine

GOAL：形成质量受控的 daily factor、candidate ranking 与 watchlist。

STATUS：next product milestone。

DONE：候选和日内需求、lineage 与质量门已定义。

EXIT GATE：有效 ACTIVE_SETUP、可复现 factors、ranking 与 provenance 可审计。

NOT IN SCOPE：production rule promotion、自动参数搜索或 TradePlan 自动执行。

## PHASE E — Intraday B2

GOAL：在可验证的 5m facts 与 immutable checkpoint 上提供 B2 观察。

STATUS：not yet authorized。

DONE：日内需求与 fail-closed boundary 已定义。

EXIT GATE：live 5m checkpoint 闭环、provenance、PIT 与 B2 验证完成。

NOT IN SCOPE：未经授权的日内服务、自动交易或规则改写。

## PHASE F — Prospective R9

GOAL：按冻结协议完成 prospective OOS。

STATUS：not yet authorized。

DONE：R9 原则和候选 blocker 已记录。

EXIT GATE：60 initial sessions、append-only ledger 与预先定义的结算证据完成。

NOT IN SCOPE：refit、recalibration、performance stopping 或自动 promotion。

## PHASE G — Forward Paper

GOAL：形成经过人工审核的前瞻纸面计划。

STATUS：not yet authorized。

DONE：Forward 与 OOS/Production 的边界已定义。

EXIT GATE：前瞻 OOS 证据、风险边界和人工决策明确。

NOT IN SCOPE：券商执行或把研究结论当 production。

## PHASE H — Production Decision Support

GOAL：提供可追溯的人工决策支持。

STATUS：not yet authorized。

DONE：最终运行观测字段与质量门已定义。

EXIT GATE：数据、策略、OOS、运营和人工治理门全部关闭。

NOT IN SCOPE：自动 broker execution。

## PHASE I — Optional Broker Execution

GOAL：仅在单独授权和治理完成后评估可选券商执行。

STATUS：not yet authorized。

DONE：无。

EXIT GATE：单独的产品、风险、合规、安全与人工审批决定。

NOT IN SCOPE：V01 默认范围内的任何自动下单。
