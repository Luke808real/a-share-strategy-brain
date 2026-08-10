# Candidate and Intraday

## Candidate requirements

系统需要将以下层次分开、可追溯地表达：

- ACTIVE_SETUP
- Daily Factors
- M0
- M1
- M2
- Candidate Ranking
- Watchlist
- Live 5m
- Immutable 10:30 Checkpoint
- Intraday Features
- B2 Engine

候选排序、watchlist 和日内信号不得重写冻结 setup lifecycle 或 entry semantics。

## Current research references

以下是当前研究事实，不是 production rule，也不改变冻结阈值：

| Reference | Current statement | Validation level |
|---|---|---|
| B6 | volume_D / volume_T0 <= 0.85 | OBSERVATION / research-only |
| M1 | M1 = M0 + median_range_ratio | OBSERVATION / research-only |
| M2 | M2 = M1 + quiet_days_n | OBSERVATION / research-only |
| Primary comparison | M1 vs M0 | OBSERVATION / research-only |
| R8 intraday feature | breakout_hold_ratio is the strongest current intraday feature | OBSERVATION / research-only |

上述项目需要可审计的输入、样本、PIT 和后续验证，才能进入正式策略讨论；它们不
授权 production、Forward、TradePlan 或阈值调整。

## Intraday boundary

5m live facts、immutable 10:30 checkpoint、intraday feature 与 B2 engine 必须保留
时间戳、provenance、quality 和 checkpoint 版本。若 checkpoint 无法证明不可变或
5m 事实不完整，日内输出必须 fail closed。
