# Vault总索引

## 真源边界

- 冻结策略唯一人类真源：[[01_Strategy/STRATEGY_MASTER]]
- 稳定规则ID与实现状态：[[01_Strategy/RULE_CATALOG]]
- 已采纳决策：[[03_Decisions/DECISION_INDEX]]
- 未冻结假设：[[04_Research/Candidate-Rules]]
- 案例索引：[[02_Cases/CASE_INDEX]]
- 当前阶段：[[05_Codex/CURRENT_PHASE]]
- 最新实现提示：[[05_Codex/NEXT_PROMPT]]
- 会话索引：[[06_Conversations/CONVERSATION_INDEX]]
- 人工审核队列：[[05_Codex/REVIEW_QUEUE]]
- 隐私边界：[[PRIVACY]]
- Agent Exchange：[[08_AgentExchange/README]]
- Agent写入政策：[[08_AgentExchange/AGENT_WRITE_POLICY]]
- 推理摘要索引：[[06_Conversations/REASONING_INDEX]]
- 策略实现队列：[[05_Codex/IMPLEMENTATION_QUEUE]]

## 研究入口

- [[04_Research/Blogger-Observations]]
- [[04_Research/Success-Case-Features]]
- [[04_Research/Research-Backlog]]

## 固定迭代流程

原始对话或截图 → 案例笔记 → Candidate Rule → 成败对照组 → ADR →
历史信号影响审查 → 更新冻结真源与规则目录 → Codex提示 → 代码与Golden
Regression → 验证冻结 → CHANGELOG。

任何单一样本或单一观点都必须停留在观察层，直到有充分对照样本和正式ADR。

## 自动化

- 创建案例：`python tools/new_case.py --help`
- 创建变更请求：`python tools/new_change_request.py --help`
- 重建案例索引：`python tools/build_case_index.py`
- 生成上下文包：`python tools/build_context_pack.py`
- 预检会话Inbox：`python tools/ingest_chat_inbox.py --dry-run`
- 生成人工审核增量：`python tools/build_context_delta.py`
- 更新策略基线哈希：`python tools/update_baseline_manifest.py`
- 检查代码基线drift：`python tools/check_strategy_drift.py`
- 校验Agent Exchange：`python tools/validate_agent_exchange.py`
- 构建推理与实现索引：`python tools/build_reasoning_index.py`
- 敏感信息扫描：`python tools/scan_sensitive_content.py`
- GitHub桥接状态：`tools/github_bridge_status.sh`
- 校验Vault：`python tools/validate_vault.py`
