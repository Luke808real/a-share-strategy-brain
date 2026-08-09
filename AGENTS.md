# AGENTS — Strategy / Research Knowledge Authority

This repository is the strategy / research knowledge authority, NOT the
executable truth for implementation behavior. Exact code behavior is
determined by exact HEAD + tests in the code repository
(a-share-limit-pullback).

## Authority Matrix

| Question | Authority |
|---|---|
| 当前用户明确任务 | 当前用户指令 |
| 代码实际行为 | exact HEAD + tests（code repo） |
| 数据 lineage / availability | manifests / SHA / committed reports |
| 当前研究结论 | latest authoritative research report |
| frozen strategy semantics | STRATEGY_MASTER + RULE_CATALOG + BASELINE_MANIFEST |
| 当前项目阶段 | `PROJECT_STATE_SNAPSHOT.md` |
| 历史记录 | IMPLEMENTATION_LOG / archived reports |

`DESIGNED / IMPLEMENTED / VALIDATED / PROMOTED` must not be treated as
equivalent. A stale phase note must not override newer exact-HEAD facts, data
provenance, or reviewed research reports.

## Current-state pointer

Read `PROJECT_STATE_SNAPSHOT.md` first. `05_Codex/CURRENT_PHASE.md` below its
header is a HISTORICAL IMPLEMENTATION LOG, not current authority.

## Research taxonomy

`OBSERVATION / HYPOTHESIS / SUPPORTED_HYPOTHESIS / VALIDATED /
STRATEGY_CANDIDATE / PROMOTED`, with orthogonal `IMPLEMENTATION_STATUS` and
`PRODUCTION_STATUS`. SUPPORTED != VALIDATED != PROMOTED. Historical time
splits are `DEVELOPMENT_STABILITY`, not automatic clean OOS; clean prospective
validation is an R9-style protocol (see code-repo
`.codex/skills/ashare-prospective-validation`).

## Write policy pointer

Frozen strategy files are immutable here (`01_Strategy/STRATEGY_MASTER.md`,
`RULE_CATALOG.md`, `BASELINE_MANIFEST.yaml`, `STATE_MACHINE.md`). Durable
artifacts must not contain user-specific absolute paths; use
`A_SHARE_STRATEGY_BRAIN_ROOT` or sibling `../a-share-strategy-brain`; if not
found: `KB_UNAVAILABLE` — do not guess another path.

## Privacy

No credentials, tokens, raw market data, or personal identifiers in durable
artifacts.

## Cross-repo boundary

Strategy semantics live here; executable behavior lives in the code repo.
Research results are recorded here only after a reviewed code-repo report.
