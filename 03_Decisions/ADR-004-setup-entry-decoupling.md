---
type: strategy_decision
adr_id: ADR-004
decision_id: D-024
title: Setup生命周期与入场价值解耦
status: ACCEPTED
decision_date: 2026-07-31
strategy_version: phase-2b3
---

# ADR-004 Setup生命周期与入场价值解耦

## 原规则

Phase 2B.2的B1条件曾读取target S1派生的risk/reward，B2量价确认曾读取S1剩余
空间。这使压力候选变化可能反向改变setup结构阶段。

## 新观察

setup是否成立与当前位置是否值得新建仓是两个不同问题。压力、目标和剩余空间可以
改变入场价值，但不应改写已由锚点、回调、支撑、量价、K线和均线确认的结构状态。

## 决策

D-024正式冻结以下语义：

- `setup_stage`只表达结构生命周期；
- B1结构门槛不读取target S1、risk/reward或Entry Room；
- B2量价确认不读取S1空间；
- `setup_quality_score`只评价结构质量；
- `entry_quality_score`只评价新建仓价值；
- `S1_BREAKOUT`与`S2_EXHAUSTED`影响入场资格，但不修改`setup_stage`；
- INVALID仍是结构终止条件；
- OPEN_SPACE可以保持`B1_READY`或`B2_READY`。

## 被否决方案

- 通过更换target S1提前或延后B1；
- 因Entry Room为NONE将已成立B1/B2降回WATCH；
- 因缺少S1而禁止OPEN_SPACE形成结构setup；
- 将S1空间重新加入B2量价确认条件。

## 对历史信号的影响

结构时间线只会因移除旧耦合条件而变化；S1、Entry Room、risk/reward和入场分数
仍可变化。真实样本中当前setup日期保持稳定，002606较早历史setup的首次
`B2_CONFIRMED`日期因解除S1空间门槛而变化。

## 代码影响

策略实现提交为`a5037091774d0b8d0b6ba686c332d012e640d7e6`。main通过等价tree的
merge commit集成为`78ff7915e9bc77dca1201adea9ccd2febb58f15b`。

## 配置影响

`minimum_risk_reward`从B1结构配置移动到Entry Room配置，数值保持不变；未调整
任何B1、B2、INVALID或Entry Room阈值。

## 测试影响

覆盖有无target S1、替换合法S1、risk/reward变化、OPEN_SPACE、Entry Room NONE、
S1事件和未来压力候选变化时的结构时间线不变量。

## 是否需要重新生成黄金样本

需要；新增结构质量与入场质量分层输出，并允许解除耦合后的历史状态差异。

## 证据与不确定性

Phase 2C.0已验证BaoStock、AKShare、inspect与point-in-time replay真实链路，
并确认截短回放历史前缀一致。任意股票支持和Provider重复记录、缺失字段等边界
问题留给Phase 2C.1，本决策不包含这些修复。
