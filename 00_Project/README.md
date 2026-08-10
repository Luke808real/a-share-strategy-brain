# Project OS

本目录是 a-share-strategy-brain 的长期 Project OS。它把稳定需求、架构、
路线图、当前状态、Blocker 与 Agent 接力协议分开保存；它不复制运行时代码，
也不替代冻结策略真源。

## READ FIRST

新 Agent 固定按以下顺序读取：

1. [[00_Project/AGENT_HANDOFF]]
2. [[00_Project/CURRENT_STATE]]
3. [[00_Project/PROJECT_CHARTER]]
4. [[00_Project/ROADMAP]]
5. [[01_Strategy/STRATEGY_MASTER]]
6. [[01_Strategy/RULE_CATALOG]]
7. 与当前任务直接相关的 Research / Decision 文档

不要求新 Agent 阅读整个仓库。先用上述入口恢复范围、状态和约束，再按任务扩展
到直接相关的证据。

## Truth Priority

事实冲突时，按以下优先级处理：

1. 用户当前明确指令
2. [[00_Project/CURRENT_STATE]]
3. 最新正式验证报告 / accepted decision
4. [[01_Strategy/STRATEGY_MASTER]] / [[01_Strategy/RULE_CATALOG]]
5. Research
6. Conversations / archive

冻结策略语义仍由 STRATEGY_MASTER 与 RULE_CATALOG 定义。CURRENT_STATE 记录的是
当前项目事实、执行边界与阻塞项，不能单方面提升规则状态。

## Project OS map

- [[00_Project/PROJECT_CHARTER]]：低频变化的使命、边界与优先级。
- [[00_Project/Requirements/01_Product_and_Scope]]：分层产品与需求合同。
- [[00_Project/Architecture/01_System_Context]]：系统平面、lineage 与质量门。
- [[00_Project/ROADMAP]]：阶段目标、退出门与授权边界。
- [[00_Project/CURRENT_STATE]]：唯一 overwrite-style current truth。
- [[00_Project/BLOCKERS]]：只保留仍然 OPEN 的 blocker。
- [[00_Project/AGENT_HANDOFF]]：2–5 分钟恢复项目的接力入口。
- [[00_Project/REPO_AUTHORITY_MAP]]：三个仓库的真源边界。
- [[00_Project/STATE_UPDATE_PROTOCOL]]：完成重要任务后的状态更新协议。

## Maintenance boundary

CURRENT_STATE、BLOCKERS 与 AGENT_HANDOFF 经常更新。ROADMAP 只在阶段变化时更新；
Requirements、Architecture 与 PROJECT_CHARTER 只在合同或架构改变时更新。历史状态
进入 [[06_Conversations/StateSnapshots]]，不得继续追加到 current truth。
