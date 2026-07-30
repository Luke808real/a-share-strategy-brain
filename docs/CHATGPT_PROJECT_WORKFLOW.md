# ChatGPT Project上下文回流流程

1. 创建或使用“A股首板回踩再启动策略”Project，并把当前长期聊天移动到该Project。
2. 首次上传 `exports/LLM_CONTEXT_PACK.md`；后续优先上传
   `exports/LLM_CONTEXT_DELTA.md`，必要时补充 `CASE_CONTEXT_PACK.md`。
3. Project指令必须声明：STRATEGY_MASTER是冻结真源；PROPOSED不能当作FROZEN；
   新观点先进入Candidate Rules；不得为单只股票修改阈值。
4. 每次上传Delta后询问：
   “读取本次增量包，并说明新增案例、候选规则和待决策项。”
5. 对话结论仍需归档、人工审核，不能由ChatGPT直接改变冻结真源。

ChatGPT不会自动持续读取本地iCloud Vault。每次变化都必须上传Context Pack、连接
经过明确授权的私人仓库，或在对话中显式提供文件；本Vault不使用浏览器Cookie、
私有接口、OpenAI API或网络同步。
