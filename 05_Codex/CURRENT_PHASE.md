# 当前阶段

- 冻结策略版本：`phase-2c2b`
- 冻结代码标签：`phase-2c2b`
- 策略内容提交：`4a4fb8cb91b4f4fa1a8ba330254fe3b188f9ddbc`
- main集成提交：`d9e2065fb1c09e2032e59db48c5bb06e0e5dc2a6`
- 基线关系：`MERGE_EQUIVALENT_TREE`
- 当前知识库任务：Phase 2C.2B全市场数据验收已冻结；开始范围明确的Phase 2C.2C盘后交易计划
- 策略代码修改：禁止
- HTML报告、回测、自动交易：不在范围

## 已具备

双价格体系、setup/event分离、冻结快照、无未来数据replay、FULL/PRICE_ONLY、
B1/B2/INVALID、双层压力、Entry Room、setup终止、BaoStock/AKShare适配、任意
合法沪深主板单股的inspect/replay，以及D-024、D-025与D-026多源行情仓库。

## Phase 2C.2A多源行情仓库验收

- Tushare Pro七项能力探针`AVAILABLE`；Parquet+DuckDB仓库与七张元数据表就绪；
- `bootstrap`历史回填与`update`每日幂等增量通过；写锁串行化并发运行；
- 显式对账：五只股票2026-06-01..07-31共220行`CONFIRMED`、8行涨停池
  `PROVISIONAL`、0冲突、0隔离，`data-validate`全绿；
- 三源最新日期均到2026-07-31；BaoStock延迟场景由单测覆盖并审计
  `BAOSTOCK_LAGGING`；
- 审查修复：错误落库脱敏、历史原始行回退、涨停池同源冲突隔离、manifest
  源文件并集；默认离线187项、integration 15项通过；
- 尚未开放全市场扫描、HTML报告、回测或自动交易。

## Phase 2C.2B全市场数据验收与冻结

- 内容提交`4a4fb8c`由main普通merge commit`d9e2065`集成，annotated tag为
  `phase-2c2b`，内容tree与main集成tree一致；
- 固定快照`snap-2026-07-31-b5f84004de8a`的`data-validate`为`valid=true`且无问题；
- formal、CONFIRMED-only、`pool_mode=formal`全市场screen为3191只、1,844,543行，
  输出哈希`9abb16e4a5720503e4ffea5462067dc1b476d8022f0593a657c328f9836920ec`；
- 20只重建回放逐字段一致，11,378行，哈希
  `6c2ffc2235fabd9e32c3aff227fc27d9aac622cb68a1fa6c9ba99a8d1d18b418`；
- 4a4fb8c仅修正warehouse/data-validate的Tushare adjusted preclose语义及测试，
  未改变策略、screen、canonical或涨停池逻辑；
- 未开放数据库以外的新扫描范围、报告、回测或自动交易。

## Phase 2C.2C当前范围

当前只实现盘后最新横截面的B点预备候选与次日交易计划，使用独立的执行标签
`B1_PREP`，不改变冻结`setup_stage`、S1/S2、Entry Room、评分或阈值语义；不接入
自动下单、分钟数据、回测或新的基础设施。

## Phase 2C.1真实链路与Provider边界验收

- BaoStock日线与AKShare涨停池真实链路可用；
- inspect单日无状态评价可用；
- point-in-time replay逐日有状态回放可用；
- 截短回放与完整回放历史前缀一致，无未来回写；
- 默认离线测试和真实integration测试全部通过；
- 合法沪深主板单股已开放；inspect为无状态评价，replay为逐日状态回放；
- Provider重复记录、畸形字段、会话异常和短历史边界已覆盖并显式传播质量；
- 603918复验显示BaoStock可出现日线延迟；replay标记`STALE_DATA`而不伪造7月31日线；
- 尚未开放全市场扫描、数据库、Parquet、缓存、报告、回测或自动交易。

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
Issue草稿。代码仓库基线由人工批准的merge commit更新；本Vault不改变选股代码或参数。

## 真源说明

本Vault承认annotated tag `phase-2c1`解引用的策略内容提交为冻结实现。
main通过不同SHA但相同tree的merge commit集成该实现；只要内容提交仍为main祖先、
tag指向正确、tree和策略文件哈希一致且代码工作区干净，drift状态为CURRENT。
未经ADR采纳的后续实验不自动成为本知识库的冻结策略。
