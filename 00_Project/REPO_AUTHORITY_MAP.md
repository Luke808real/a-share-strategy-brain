# Repo Authority Map

三个仓库分工明确；同一事实不能在三个仓库都成为独立真源。

| Repository | Authority |
|---|---|
| a-share-strategy-brain | requirements / strategy knowledge / decisions / research / current state |
| a-share-limit-pullback | V Flash runtime / strategy implementation / snapshot / state / R9 integration |
| rootSunc/ashare-lake + validated project SHA | data plane |

## Authority boundary

| Fact type | Primary authority | Second Brain stores |
|---|---|---|
| Frozen strategy semantics | STRATEGY_MASTER / RULE_CATALOG | meaning, decision and SHA pointer |
| Research conclusion | reviewed research / accepted decision | conclusion status and evidence pointer |
| Runtime behavior | V Flash code and validated artifacts | status and exact SHA pointer |
| Data facts / lineage | ashare-lake and validated project SHA | data-plane status and SHA pointer |
| Project execution status | CURRENT_STATE | current status, blocker and next gate |

Second Brain 不复制实现代码、raw data 或另造数据真源。它保存 meaning、decision、
status 和 SHA pointer，使新 Agent 可以知道应到哪个仓库核对哪类事实。

## Conflict handling

当仓库之间的文字或状态发生冲突时，先依据当前用户明确指令，然后查
[[00_Project/CURRENT_STATE]] 的 pointer 和对应权威仓库的精确 SHA。不能只凭分支名、
最新提交或会话记忆覆盖已验证基线。
