# Project Charter

本 Charter 只保存长期稳定的项目意图与边界。当前执行、证据和 blocker 以
[[00_Project/CURRENT_STATE]] 与 [[00_Project/BLOCKERS]] 为准。

## Mission

项目研究并逐步构建以下第二波启动结构的、可审计的决策支持能力：

低位/中低位强势涨停
→ 第一次资金表态
→ 缩量回调洗筹
→ 关键支撑
→ B1
→ B2_READY
→ B2_CONFIRMED
→ SECOND_LAUNCH

目标是把该过程变成：

- data reliable
- rules explicit
- statistically testable
- prospectively validated
- decision-support capable

策略语义和阈值的冻结真源始终是 [[01_Strategy/STRATEGY_MASTER]] 与
[[01_Strategy/RULE_CATALOG]]。

## Non-goals

V01 不是：

- generic quant platform
- high-frequency system
- auto parameter mining
- multi-strategy framework
- automatic broker execution V1

本项目不以扩大技术栈或制造候选数量为目标；任何策略或执行能力都必须先经过相应
的数据、PIT、lineage 与验证门。

## Highest Priority

工作优先级固定为：

数据正确性
>
策略语义
>
PIT / lineage
>
Candidate generation
>
Intraday B2
>
Prospective OOS
>
Forward
>
Production

后续层不能绕过前序层的未关闭质量门。该顺序表达风险控制，不是自动执行授权。
