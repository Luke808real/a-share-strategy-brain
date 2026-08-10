# 最新Codex提示

当前没有获批的策略实现任务。Phase 2D.0 corrected baseline已冻结；下一步仅允许对
corrected `episodes.parquet`做低成本baseline diagnosis，不得重放或重筛。

正式输入：

- Snapshot：`snap-2026-07-31-b5f84004de8a`
- Corrected episodes SHA-256：
  `66d5943ffd4c83d8348d7b559ef9aa8ab9c041525471108a2f724fbedd84b093`
- 旧episodes SHA-256：
  `23d3ff935cb44d523288c744c39abc231ce2c19a486b56ddfe057aa0809130af`
- 旧baseline状态：`SUPERSEDED_FOR_B2_EXECUTION_OUTCOME`

诊断维度：

1. stage × setup_quality：B1_READY、B2_READY、B2_CONFIRMED × `<60`、`60-70`、`70-80`、`>=80`；
2. stage × entry_quality：同上；
3. actionable 与 non-actionable B2_READY：pattern outcome、trigger reach/future structure、
   setup/entry quality、Entry Room、days since anchor、eligibility reasons；
4. B2_READY ambiguity：actionable cohort的filled、resolved、ambiguous count/rate、strict
   与 conservative expectancy；
5. Entry Room：OPEN_SPACE、THIN、SUFFICIENT、NONE的episodes、filled、strict win rate、
   strict E[R]、conservative E[R]、ambiguous rate；
6. days_since_anchor：保持D+1、D+2、D+3、D+4、D+5+固定分组；
7. win R / loss R分解。

保留`resolved <30`的`SMALL_SAMPLE`与`resolved <100`的`LOW_CONFIDENCE`标记；不搜索新阈值、
不自动挑选最佳分组或组合。non-actionable cohort不得再展示旧的`+0.4509`交易期望，也不得
解释为“被gating排除的高收益交易”。

诊断只能读取corrected episodes，不修改策略、阈值、配置或模型；不得调用`evaluate_strategy`、
重跑causal replay、full-market screen、provider download、snapshot finalize，不实现event
cache、回测、HTML报告或自动交易。预期秒级；若超过5分钟停止并报告原因。

PR #9继续保持Draft，不合并；ashare-lake仍为`NOT_INTEGRATED`。任何新规则必须先有足够
对照样本、正式ADR和人工批准。
