# PROJECT_STATE_SNAPSHOT

Current state only — not a historical log. Values are conservatively compiled
from the latest reviewed research reports, `05_Codex/CURRENT_PHASE.md`
(historical log), and committed code-repo reports. Anything that cannot be
confirmed from the repos is marked explicitly.

AS_OF: 2026-08-09（本地整理；未做远端完整审计）

## ARCHITECTURE

```text
DATA_SOURCE: ASL（rootSunc/ashare-lake upstream；本地候选 @
  04bd94936587b35cae55c833627260866d025184，RESEARCH_ONLY）
ASL status: CANDIDATE / NOT_ACTIVE（ASL_ACTIVE_CHANGED=false；
  生产数据层仍为既有 canonical 快照族）
```

## PRODUCTION

```text
SNAPSHOT: snap-2026-07-31-b5f84004de8a（既有 frozen 快照；正式状态见
  code-repo manifests；NOT_YET_REMOTE-AUDITABLE 的细节不在此猜测）
STATE: 既有 state generation（详见 code repo / CURRENT_PHASE 历史）
STRATEGY_VERSION: phase-2d0（来源 CURRENT_PHASE 2026-08-08；
  NOT_YET_REMOTE-AUDITABLE）

PRODUCTION: 按既有授权状态；无新增 promotion
FORWARD: 未进入新的 Forward Validation（历史日志记录）
TRADEPLAN: 按既有授权状态；无新增 TradePlan 变更
```

## RESEARCH

```text
R0-R8: development evidence COMPLETE（research branches；
  结论级别 SUPPORTED_HYPOTHESIS 上限；未 VALIDATED）
R7: COMPLETE — multivariate attribution（R7B 结果：
  research/second-launch-factor-r7b-multivariate-execution-v01）
R8: COMPLETE — intraday acceptance（chronology-fix 后结果：
  research/second-launch-factor-r8b-chronology-fix-v01；
  旧 R8B 结果标记 INVALIDATED_BY_UNSORTED_BAR_ORDER）

PRE_R9_DESIGN_STATUS=GO
  （pre-R9 设计/协议决策已做出；Gate2A=PASS、Gate2B semantics=PASS）
R9_ACCUMULATION_IMPLEMENTATION=PATCH_REQUIRED
  （pre-accumulation boundary hardening 尚未完成）
R9_ACCUMULATION=NOT_STARTED
R9_OOS_ROWS_WRITTEN=0
REMOTE_AUDIT_STATUS=NOT_YET_REMOTE_AUDITABLE
LOCAL_PRE_R9_LINEAGE=PENDING_PUSH
  （本地 R9 准备 lineage 尚未推送；不得视为远端权威；
   与 R0-R8 已推送的 research branches 区分）
prospective validation skill 已建立（code-repo
  .codex/skills/ashare-prospective-validation）
```

## CURRENT AUTHORITY

```text
research report: SECOND_LAUNCH_FACTOR_R8B_INTRADAY_ACCEPTANCE_RESULTS_V01
  （chronology-fix 修订版；R8A contract 为 frozen protocol）
dataset: ASL 5m research lake（R8_ASL_DATA_ROOT；
  dataset lock 3914887a81908dfc6745c412a3f0406c3ba6a7ddc7e7e2902b0af0fb730add9a；
  270,000 rows / 40 partitions；LOCAL，未提交 raw bars）
local pending: R0-R8 research branches 已推送但未合并 main ->
  RESEARCH_BRANCH_ONLY / NOT_MAIN_MERGED；PRE-R9 准备 lineage 未推送 ->
  PENDING_PUSH（见 RESEARCH 段）
```

## BLOCKERS

```text
- R9 prospective validation 尚未开始（需人工设计最小 forward 观测协议）
- ASL 生产切层 / ST_READINESS 未完成（CURRENT_PHASE 历史记录；
  PRODUCTION_CUTOVER=NO_GO）
```

## NEXT_ACTION

```text
人工审查本 snapshot 与 Governance Refresh V02；
随后设计 R9 最小 forward 观测协议（不自动开始）。
```
