# System Context

## System flow

ASL
↓
ASL Adapter
↓
Canonical
↓
Snapshot
↓
Universe
↓
State
↓
Setup
↓
Factors
↓
Candidate
↓
Intraday
↓
B2
↓
OOS / Decision Support

每一层必须向下一层传递 data date、provenance、quality 与代码/配置版本。下游
不得把缺失的上游事实解释为正常状态。

## Independent readiness

下列 readiness 是不同的问题，不能互相替代：

| Readiness | Meaning |
|---|---|
| LIVE_CORE_READY | 当前数据、snapshot、universe、state 和 candidate 的实时核心链路可用 |
| HISTORICAL_RESEARCH_READY | 历史样本、PIT、lineage 与验证足以支持研究结论 |
| R9_PROSPECTIVE_READY | 已满足 R9 协议、冻结、结算和前瞻性观察前提 |

当前状态只由 [[00_Project/CURRENT_STATE]] 声明。某一个 readiness 成立不代表其他
readiness 成立，也不代表生产授权。
