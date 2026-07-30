# Agent写入政策

## GitHub边界

1. ChatGPT不得直接写`main`。
2. 分支只能使用：
   - `chatgpt/case-<case-id>`
   - `chatgpt/digest-<session-id>`
   - `chatgpt/proposal-<rule-id>`
3. 每次写入必须创建Pull Request，并添加`needs-human-review`标签。
4. ChatGPT不得合并自己的PR；只有用户可以批准合并。

## 允许创建

- CAPTURED案例；
- 可审计Reasoning Digest；
- PROPOSED规则草稿；
- draft或proposed Code Change Request。

## 禁止操作

- 将规则设为ACCEPTED或FROZEN；
- 修改STRATEGY_MASTER的冻结结论；
- 修改BASELINE_MANIFEST；
- 直接修改选股代码；
- 根据单只股票修改阈值；
- 保存或声称保存模型内部逐字chain-of-thought。

Agent提交必须脱敏。完整聊天、账号导出、截图、Token、Cookie、本地绝对路径和个人
账户信息不得进入PR。Incoming输入只代表待审核事实，不代表策略结论。
