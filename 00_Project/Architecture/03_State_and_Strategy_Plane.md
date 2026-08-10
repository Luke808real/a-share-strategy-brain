# State and Strategy Plane

## Components

状态与策略平面由以下逻辑组件组成：

- Snapshot
- Universe
- State Generation
- Setup Accumulator
- Factor Engine
- Candidate Engine

冻结策略的规则语义不由本架构文档定义；请参阅
[[01_Strategy/STRATEGY_MASTER]] 与 [[01_Strategy/RULE_CATALOG]]。

## Required properties

每个组件必须支持：

- deterministic：相同输入、代码和配置产生相同结果；
- idempotent：安全重跑不会改变已确定结果；
- full / incremental parity：全量与增量在同一输入边界下可比较；
- lineage：输出可追溯到输入 snapshot、universe、state、代码与配置。

若无法证明上述条件，输出不能被作为正式 candidate、OOS 记录或生产决策支持。
