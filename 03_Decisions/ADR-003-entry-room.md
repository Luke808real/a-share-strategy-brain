---
type: strategy_decision
adr_id: ADR-003
title: 压力分层与Entry Room
status: ACCEPTED
decision_date: 2026-07-30
strategy_version: phase-2b2
---

# ADR-003 压力分层与Entry Room

## 原规则

单一S1既可能是B2突破平台，也可能被当作突破后的目标，导致结构矛盾。

## 新观察

锚点价和支撑簇不能作为上方压力；B2突破位上方还需要独立目标来判断剩余空间。

## 决策

区分`immediate_resistance`和`target_s1`。Entry Room使用阶段对应参考价到
target S1下沿的Decimal比例，分为NONE、THIN、SUFFICIENT、OPEN_SPACE。

## 被否决方案

- 将锚点价直接作为S1；
- target低于B2触发价仍计算正向收益空间；
- 没有目标时虚构价格或自动淘汰。

## 对历史信号的影响

S1、Entry Room及`is_entry_candidate`可能变化；B1/B2阈值不因此调整。

## 代码影响

新增压力候选审计、双层压力快照和Entry Room输出。

## 配置影响

增加THIN/SUFFICIENT的5%边界，未调整B1/B2/INVALID阈值。

## 测试影响

覆盖压力簇排除、目标高于预期B2、OPEN_SPACE和未来数据隔离。

## 是否需要重新生成黄金样本

需要；S1与入场资格输出发生变化。
