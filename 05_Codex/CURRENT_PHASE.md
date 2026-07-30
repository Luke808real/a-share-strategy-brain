# 当前阶段

- 冻结策略版本：`phase-2b2`
- 冻结代码标签：`phase-2b2`
- 当前知识库任务：KB-1.3 GitHub知识桥接与策略迭代闭环
- 策略代码修改：禁止
- 数据库、Parquet、HTML、全市场扫描、回测、自动交易：不在范围

## 已具备

双价格体系、setup/event分离、冻结快照、无未来数据replay、FULL/PRICE_ONLY、
B1/B2/INVALID、双层压力、Entry Room、setup终止、BaoStock/AKShare适配。

## 当前研究

MA30高悬、损伤修复、多次长上影、时间成本、成功案例特征和分钟路径观察。
它们均未冻结，见 [[04_Research/Candidate-Rules]]。

## KB-1.2边界

会话Raw、Inbox、官方完整导出和截图只保留本地；只有人工审核后的Digest可进入
Full/Delta Context Pack。审核会话不自动接受Candidate Rule，不创建FROZEN规则，
不修改STRATEGY_MASTER。

## KB-1.3边界

Agent写入只能进入`chatgpt/*`分支和带人工审核标签的PR。CAPTURED案例、推理摘要
与PROPOSED草稿不能直接改变冻结策略；只有人工批准的Change Request可以进入代码
Issue草稿。代码仓库只读用于基线drift检查，本任务不修改选股代码或参数。

## 真源说明

本Vault初始化只承认annotated tag `phase-2b2`为冻结基线。代码仓库中任何未提交、
未打标签或尚未经ADR采纳的后续实验，不自动成为本知识库的冻结策略。
