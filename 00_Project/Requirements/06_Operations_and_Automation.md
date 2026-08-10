# Operations and Automation

## Target pipeline

最终自动化能力需要按可观测、可中止和可复跑的步骤覆盖：

daily data
→ snapshot
→ universe
→ state
→ setup
→ factors
→ watchlist
→ intraday
→ checkpoint
→ outcome
→ validation

每一步都需要明确输入、输出、quality gate、lineage 和失败状态。上游失败不能被
下游默认解释为零候选或正常市场。

## User-level concepts

最终用户级入口概念为：

- daily
- intraday
- status
- validate

它们描述产品需求，而不是本轮实现授权。本文件不创建 CLI，也不要求新服务、
数据库、缓存或自动交易能力。

## Operational expectations

运行记录应能够展示使用的 data date、snapshot、generation、universe、代码 SHA、
quality state、blocker 与授权模式。自动化必须尊重冻结工件和当前 gate，不能因为
任务调度而跨越 Research、OOS、Forward 或 Production 边界。
