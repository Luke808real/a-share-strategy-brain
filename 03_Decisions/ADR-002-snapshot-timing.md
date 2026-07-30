---
type: strategy_decision
adr_id: ADR-002
title: 风险快照先冻结后生效
status: ACCEPTED
decision_date: 2026-07-30
strategy_version: phase-2b2
---

# ADR-002 风险快照先冻结后生效

## 原规则

Support、Invalid与S1候选可能在计算当日立即参与事件或失效判断。

## 新观察

这会让当天形成的价位反向解释同一根K线，并在锚点日或首个B1日制造错误预警、
S2或INVALID。

## 决策

Support、Invalid、S1、B2 Trigger统一保存`frozen_as_of`与`eligible_from`，
且后者严格晚于前者。T日只使用previous signal中已生效的快照。

## 被否决方案

- 冻结日立即生效；
- 只给B2触发价设置时序；
- 依赖持久化层事后修正。

## 对历史信号的影响

锚点日和首次B1日不再触发基于新快照的事件或失效。

## 代码影响

纯函数显式接收previous signal并沿用不可变快照。

## 配置影响

不修改失效或事件阈值。

## 测试影响

增加冻结日不可使用、下一交易日起生效和未来数据不改变历史JSON测试。

## 是否需要重新生成黄金样本

需要；事件日期和失效日期可能改变。
