# GitHub知识桥接与策略迭代闭环

## 知识库写入

ChatGPT只在`chatgpt/*`分支创建CAPTURED案例、Reasoning Digest或PROPOSED草稿，
随后创建带`needs-human-review`标签的PR。用户审核并合并后，本地Vault使用
`tools/github_bridge_pull.sh`进行快进同步。

## 从案例到代码Issue

1. Agent Case通过Schema进入Incoming。
2. 人工把CAPTURED标记为REVIEWED，再显式提升为正式案例。
3. Candidate Rule积累成功样本和失败对照。
4. 人工建立ADR与Strategy Change Request。
5. 只有`approved_for_implementation`进入IMPLEMENTATION_QUEUE。
6. 生成代码Issue草稿：

```bash
python tools/build_code_issue_draft.py \
  --change-request-id CR-20260731-001
```

7. 人工复核后创建代码仓库Issue：

```bash
gh issue create \
  --repo Luke808real/a-share-limit-pullback \
  --title "[CR-20260731-001] 策略变更" \
  --body-file 05_Codex/ChangeRequests/IssueDrafts/CR-20260731-001.md
```

## 代码实现闭环

Codex根据Issue创建独立代码分支与PR。PR必须报告修改文件、配置变化、Golden
Regression、默认离线测试、integration测试、历史信号变化和回滚方法。ChatGPT
可以审查但不得合并。用户批准并合并后，才更新BASELINE_MANIFEST、
STRATEGY_MASTER、RULE_CATALOG和CHANGELOG，再重建Context Pack。

整个流程不自动创建交易指令，不自动修改阈值，也不自动合并任一仓库的PR。
