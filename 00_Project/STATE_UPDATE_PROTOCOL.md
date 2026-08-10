# State Update Protocol

每轮重要任务结束后，按以下顺序处理状态：

AUTHOR_REPORT
↓
exact-SHA independent review
↓
PASS / BLOCKED
↓
update CURRENT_STATE
↓
update BLOCKERS
↓
update AGENT_HANDOFF
↓
if phase changed → ROADMAP
↓
archive previous state snapshot

## Evidence standard

AUTHOR_REPORT 必须指向输入、范围、精确 SHA、验证命令、输出和未解决限制。
independent review 需要检查提交、父子关系、实现/文档范围、测试/验证、产物与结论
分类。没有该审查，不得把任务结果写为 PASS。

## Update cadence

经常更新：

- [[00_Project/CURRENT_STATE]]
- [[00_Project/BLOCKERS]]
- [[00_Project/AGENT_HANDOFF]]

阶段变化才更新：

- [[00_Project/ROADMAP]]

contract 改变才更新：

- [[00_Project/Requirements/01_Product_and_Scope]]
- [[00_Project/Architecture/01_System_Context]]
- [[00_Project/PROJECT_CHARTER]]

## Archive and authorization

更新 CURRENT_STATE 前，将上一版本完整归档至
[[06_Conversations/StateSnapshots]]。不要把多个月历史继续追加到 current truth。
NEXT_GATE 只说明需要评审的边界；它不授权 Agent 自动执行后续任务。任何跨越
Research、OOS、Forward、Production 或冻结语义的操作仍需要明确授权。
