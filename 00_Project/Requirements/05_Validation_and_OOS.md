# Validation and OOS

## Evidence layers

系统需要区分并记录：

- Historical research
- Replay
- Shadow
- Prospective OOS
- Outcome settlement
- FWD3
- FWD5
- MFE
- MAE
- append-only ledger

每层证据必须记录输入 provenance、代码版本、运行时间边界、输出和结论状态。
历史 rehearsal != prospective OOS。

## R9 protocol boundary

R9 的 prospective 原则是：

- 60 initial sessions
- no refit
- no recalibration
- no re-standardization
- no performance stopping

R9 开始前需要固定协议、输入、lineage 与结算标准。达到观察期不自动提升到
Forward、Production 或策略冻结；任何状态变化仍需证据和人工决策。

## Outcome settlement

Outcome 只能在预先定义的、point-in-time 可解释的规则下结算。FWD3、FWD5、MFE 和
MAE 是结果字段，不得回流为同一样本的参数调优。ledger 必须 append-only，以保留
每次前瞻判断与后续事实之间的审计链。
