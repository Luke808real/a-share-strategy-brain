# AGENT HANDOFF

AS_OF: 2026-08-10T16:01:00+08:00

## READ FIRST

1. [[00_Project/AGENT_HANDOFF]]
2. [[00_Project/CURRENT_STATE]]
3. [[00_Project/PROJECT_CHARTER]]
4. [[00_Project/ROADMAP]]
5. [[01_Strategy/STRATEGY_MASTER]]
6. [[01_Strategy/RULE_CATALOG]]
7. 与任务直接相关的 Research / Decision 文档

不需要阅读整个仓库。先阅读当前任务的结果和证据，再决定是否可以推进。

## PROJECT

将 A 股低位/中低位强势涨停后的回调、B1/B2 与 SECOND_LAUNCH 过程，做成数据可靠、
语义明确、可统计验证且最终可支持人工决策的系统。

## WHERE WE ARE

PRE_R9_DATA_CLOSURE。Phase A 正在 closing；Phase B/C 处于 integration / closure；
Phase D 是下一 product milestone；Phase E+ 未获授权。PRIMARY_OOS=false，
OOS_ROWS=0，PRODUCTION=false，FORWARD=false，TRADEPLAN=false。

## FROZEN / DO NOT CHANGE

- [[01_Strategy/STRATEGY_MASTER]] 的冻结策略内容。
- [[01_Strategy/RULE_CATALOG]] 的冻结语义、B1/B2、setup_stage、Entry Room 和分数。
- [[01_Strategy/BASELINE_MANIFEST.yaml]]。
- 未经明确授权的 a-share-limit-pullback 或 ashare-lake 代码。
- OBSERVATION / HYPOTHESIS 的结论等级。

## CURRENT EXECUTION

ASL_BOUNDED_HISTORICAL_ST_BACKFILL_V01：RUNNING / RESULT_PENDING。
范围为 2026-03-30..2026-08-07，SYMBOL_N=3193，
POSITIVE_BAR_SYMBOL_DAY_N=286404，DERIVED_SUSPENSION_GAP_N=474。不得虚构最终 PASS，
也不得在结果出现前启动 state generation、R9、Forward、Production 或 TradePlan。

## OPEN BLOCKERS

P0：backfill/audit、08/07 state rebuild、ACTIVE_SETUP、immutable 10:30 checkpoint、
TTL suspension-age 语义、R9 provenance/old ASL_CODE_SHA pin。完整清单：
[[00_Project/BLOCKERS]]。

## NEXT GATE

先取得 bounded backfill 的 post-write audit，执行 exact-SHA independent review，再分类
PASS / BLOCKED 并更新 current documents。NEXT_GATE != AUTO_EXECUTE。

## DO NOT DO

- 不运行 full-market、R9、state generation、Forward、Production 或 TradePlan。
- 不处理当前 ASL backfill 本身，不改变 frozen rule / threshold。
- 不把研究观察写成 VALIDATED，不删除历史文档。
- 不直接 push main，不 merge PR，不保存 token、账号或本地绝对路径。

## AUTHORITY SHAS

- ASL_PROJECT_SHA: 0f16f3991a4c8793f96a585ecc938923edf978ac.
- V Flash review SHA: c5bd5b58f67356cd9bbd346e470c7ae325ffccb6.
- R9 freeze commit: 4d9e8fd7cdf0d3e4c631f8a970451c95f8c56aed.
- R7 coefficient SHA:
  39de709f424194be1a28d7e8e21be24c09824abc734027b29299a4b0452749ed.
- Thin projection: e00bb9adf1ded2e6bcbd2dfda0b8c8f7f72459ed.

State update protocol: [[00_Project/STATE_UPDATE_PROTOCOL]].
