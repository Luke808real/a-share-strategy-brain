# A股涨停回调策略第二大脑

这是 `a-share-limit-pullback` 的独立长期知识库，可直接作为 Obsidian Vault
打开，也可由 Git 进行版本管理。它不执行选股、行情下载、回测或交易。

当前冻结基线是 `phase-2b2`。冻结策略的人类可读唯一真源是
[[01_Strategy/STRATEGY_MASTER]]；所有未采纳观点必须先进入
[[04_Research/Candidate-Rules]]，不能直接修改冻结真源。

## 固定迭代流程

```text
原始对话或截图
→ 创建案例笔记
→ 保留原始数据和人工观点
→ 提炼为Candidate Rule
→ 加入成功或失败对照组
→ 达到足够样本后创建ADR
→ 审查是否影响历史信号
→ 更新STRATEGY_MASTER
→ 更新RULE_CATALOG
→ 生成Codex实现提示
→ 修改代码
→ 增加Golden Regression
→ 验证后冻结版本
→ 更新CHANGELOG
```

单只股票、单个博主或一次成功案例不能直接改变冻结规则。

## 常用命令

```bash
python tools/new_case.py \
  --code 002640 --name 跨境通 --date 2026-07-27 --outcome success

python tools/new_change_request.py \
  --title "增加MA30高悬风险" --status proposed

python tools/build_case_index.py
python tools/build_context_pack.py
python tools/validate_vault.py
pytest
```

生成的上下文包位于 `exports/LLM_CONTEXT_PACK.md`，可直接上传到 ChatGPT
Project。工具只读取本地 Markdown/YAML，不访问网络。

## 导航

- [[00_INDEX]]
- [[01_Strategy/STRATEGY_MASTER]]
- [[01_Strategy/RULE_CATALOG]]
- [[02_Cases/CASE_INDEX]]
- [[03_Decisions/DECISION_INDEX]]
- [[04_Research/Research-Backlog]]
- [[05_Codex/CURRENT_PHASE]]
- [[06_Conversations/CONVERSATION_INDEX]]
