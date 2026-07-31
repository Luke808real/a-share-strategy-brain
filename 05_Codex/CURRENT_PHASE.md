# 当前阶段

- 冻结策略版本：`phase-2b3`
- 冻结代码标签：`phase-2b3`
- 策略内容提交：`a5037091774d0b8d0b6ba686c332d012e640d7e6`
- main集成提交：`78ff7915e9bc77dca1201adea9ccd2febb58f15b`
- 基线关系：`MERGE_EQUIVALENT_TREE`
- 当前知识库任务：Phase 2B.3基线收口
- 策略代码修改：禁止
- 数据库、Parquet、HTML、全市场扫描、回测、自动交易：不在范围

## 已具备

双价格体系、setup/event分离、冻结快照、无未来数据replay、FULL/PRICE_ONLY、
B1/B2/INVALID、双层压力、Entry Room、setup终止、BaoStock/AKShare适配，以及
D-024 Setup生命周期与入场价值解耦。

## Phase 2C.0真实链路验收

- BaoStock日线与AKShare涨停池真实链路可用；
- inspect单日无状态评价可用；
- point-in-time replay逐日有状态回放可用；
- 截短回放与完整回放历史前缀一致，无未来回写；
- 默认离线测试和真实integration测试全部通过；
- 任意股票支持及Provider重复记录、缺失字段和会话异常边界留给Phase 2C.1；
- 尚未开放任意股票、全市场扫描、数据库、报告或回测。

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

本Vault承认annotated tag `phase-2b3`解引用的策略内容提交为冻结实现。
main通过不同SHA但相同tree的merge commit集成该实现；只要内容提交仍为main祖先、
tag指向正确、tree和策略文件哈希一致且代码工作区干净，drift状态为CURRENT。
未经ADR采纳的后续实验不自动成为本知识库的冻结策略。
