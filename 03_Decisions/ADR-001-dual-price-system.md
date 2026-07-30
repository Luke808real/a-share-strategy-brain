---
type: strategy_decision
adr_id: ADR-001
title: 双价格体系
status: ACCEPTED
decision_date: 2026-07-30
strategy_version: phase-2b2
---

# ADR-001 双价格体系

## 原规则

早期设计倾向所有指标统一使用不复权价格。

## 新观察

原始价适合真实涨停、支撑、压力与成交，但长期均线和120日位置会被除权断点污染。
使用今天重算的历史前复权又会引入严格回放不可接受的未来信息。

## 决策

raw price用于交易结构；point-in-time continuous close按当时可知的
`close/preclose`链式构造并用于均线、粘合和120日位置。

## 被否决方案

- 全部只用raw；
- 直接下载今天口径的历史前复权；
- 在Provider层混合多个复权口径。

## 对历史信号的影响

历史均线与位置评价必须按T日重建，旧口径结果不可直接比较。

## 代码影响

增加continuous price与raw-equivalent MA计算。

## 配置影响

明确两类价格用途，不调整策略阈值。

## 测试影响

覆盖链式连续价、无未来数据及Decimal序列化。

## 是否需要重新生成黄金样本

需要；价格体系变化会影响历史均线与位置。
