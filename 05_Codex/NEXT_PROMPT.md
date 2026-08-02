# 最新Codex提示

当前没有获批的策略实现任务。Phase 2D.0冻结后，下一步仅允许对既有
`episodes.parquet`做低成本baseline diagnosis，不得重放或重筛。

诊断维度：

1. `stage × setup_quality`；
2. `stage × entry_quality`；
3. actionable 与 non-actionable `B2_READY`；
4. Entry Room 分组；
5. win R / loss R 分解。

诊断只能读取已冻结输出，不修改策略、阈值、配置或模型；不得实现event cache、回测、
报告或自动交易。任何新规则仍须先有足够对照样本、正式ADR和人工批准。
