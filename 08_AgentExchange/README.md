# Agent Exchange

本目录是ChatGPT、Codex与人工审核之间的结构化交换边界：

- `Incoming/`：尚未提升的CAPTURED或REVIEWED输入；
- `Processed/`：已明确提升的输入；
- `Rejected/`：人工拒绝但保留审计记录的输入；
- `Schemas/`：机器可验证的JSON Schema；
- `Templates/`：供Agent或人工填写的Markdown模板。

所有Agent写入必须遵守 [[08_AgentExchange/AGENT_WRITE_POLICY]]，走
`chatgpt/*`分支和Pull Request。Incoming可以进入Context Pack的“待审核输入”，
但不得进入冻结策略摘要。
