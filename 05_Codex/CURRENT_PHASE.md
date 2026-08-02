# 当前阶段

- 冻结策略版本：`phase-2d0`
- 冻结代码标签：`phase-2d0`
- 策略内容提交：`e865de484e40e45b1d2044ee1c58247c76f3a758`
- main集成提交：`2cabcf6ca0885993185453c3384fcf346fa4ddff`
- 基线关系：`MERGE_EQUIVALENT_TREE`
- 当前知识库任务：Phase 2D.1A Execution Reality Check已完成并收口；不进入Forward Validation，下一步等待人工设计最小Forward Paper Validation / Daily Runner
- 策略代码修改：禁止
- HTML报告、回测、自动交易：不在范围

## Phase 2D.1A Execution Reality Check完成

- PR #13已获批准并以普通merge commit合入main；内容提交
  `b59f8e75b23588562af14babed0700f28b6e0066`，main集成提交
  `bd0121394a235b7c88219db44b6e187328c3198c`；
- 固定输入为`snap-2026-07-31-b5f84004de8a`的冻结Phase 2D.0 signals与31422条episodes，
  `evaluate_strategy_calls=0`；执行模型为T+1 daily-bar，成交日目标不可退出，T1阻塞止损在下一可交易开盘退出；
- T1 gross E[R]：B1 ALL严格/保守`+0.0049/-0.2230`；B1 setup>=80
  `+0.1707/-0.0204`（10bp `+0.0204/-0.1572`）；B1 entry>=80
  `+0.3954/+0.1121`（10bp `+0.2605/-0.0104`，20bp `+0.1280/-0.1313`）；
  B2 GAP `-0.0642/-0.0642`；B2 TRIGGER仍有170个order-ambiguous episodes；
- B1大R赢家在T+1下仍存在，但可执行优势对摩擦敏感；price-limit execution为`NOT_MODELED`；
- 本阶段未修改策略规则、阈值或历史优化结论，不提升任何策略规则；不进入5m数据、阈值搜索、评分优化、组合回测或策略修改；
- 当前状态：`EXECUTION_REALITY_CHECK_COMPLETE`；下一步仅等待人工设计最小Forward Paper Validation / Daily Runner。

## Phase 2D.0正式冻结

- PR #8已标记Ready并以普通merge commit合入main；内容提交
  `e865de484e40e45b1d2044ee1c58247c76f3a758`，main集成提交
  `2cabcf6ca0885993185453c3384fcf346fa4ddff`，annotated tag为`phase-2d0`；
- 内容提交与main集成提交tree一致；模式为`FINAL_VINTAGE_CAUSAL`，固定快照为
  `snap-2026-07-31-b5f84004de8a`；输出哈希见`BASELINE_MANIFEST.yaml`；
- 3191只、589个confirmed sessions、31422个episodes，运行时长3482.59秒；
- ACTIONABLE严格/保守E[R]：B1_READY=`-0.1580/-0.1902`，B2_READY=
  `-0.0979/-0.1111`，B2_CONFIRMED=`-0.0599/-0.0684`；
- 观察项：STRUCTURAL B2_READY严格E[R]=`+0.0803`；ACTIONABLE setup_quality
  `>=80`严格/保守=`+0.0257/+0.0084`；ACTIONABLE entry_quality `>=80`
  严格/保守=`+0.0769/+0.0621`；以上仅为观察，不升级为策略规则；
- 保留限制：FINAL_VINTAGE而非strict historical PIT、survivorship/coverage bias、
  daily OHLC ambiguity、成本未建模、A股T+1未完整建模；
- 不进入Phase 2D.1，不实现event cache、回测、全市场重筛或策略修改。

## Phase 2D.0 B2 execution outcome correction

- PR #10已标记Ready并以普通merge commit合入main；内容提交
  `5fbc275ad12b4089ac5deafd5ad4dd17e7143de5`，main集成提交
  `cbf9d49424fd487702d3bbeb6f7f733dd077dcbb`；该修正只改变冻结episodes的B2执行结果标注，
  不改变策略结构、阈值或策略文件哈希；
- 旧episodes哈希`23d3ff935cb44d523288c744c39abc231ce2c19a486b56ddfe057aa0809130af`标记为
  `SUPERSEDED_FOR_B2_EXECUTION_OUTCOME`，不得删除；corrected episodes哈希为
  `66d5943ffd4c83d8348d7b559ef9aa8ab9c041525471108a2f724fbedd84b093`；
- B1_READY严格E[R]仍为`-0.1580`；B2_READY由旧`-0.0979`修正为严格`-0.0079`、保守
  `-0.1216`；B2_CONFIRMED严格E[R]仍为`-0.0599`；
- 603918的2026-07-30 B2_READY不再记录10.68开盘成交，修正为`NO_FILL`、`NONE`、
  `REWARD_NON_POSITIVE_AT_TRIGGER`；
- corrected baseline后续仅用于低成本diagnosis；`evaluate_strategy_calls=0`。严格/保守差异
  记录为日线OHLC ambiguity observation；未来可用5m数据减少歧义，但本轮未接入；ashare-lake仍
  为`NOT_INTEGRATED`；
- PR #9继续保持Draft；其diagnosis输入切换到corrected episodes，不再引用旧的
  non-actionable B2_READY `+0.4509`交易期望。

## Corrected baseline diagnosis

- PR #9仍为Draft，已与最新main按普通merge同步；diagnosis只读取corrected episodes，输入哈希
  `66d5943ffd4c83d8348d7b559ef9aa8ab9c041525471108a2f724fbedd84b093`，
  `evaluate_strategy_calls=0`；
- diagnosis输出哈希：`diagnosis.json`=`ea717b3492d3656d36adb912dada6759664d89b18e5d5b804eebb96ae8ee20ee`，
  `diagnosis.md`=`829f2a524e0013845a9a7b6b656e79898bc2de326743871d6689647d7b788d7b`，运行时
  `0.7725s`；
- corrected actionable B2_READY：filled=1627、resolved=1605、ambiguous=172、ambiguous rate=`0.1072`，
  strict E[R]=`-0.0079`、conservative E[R]=`-0.1216`，差值=`-0.1137R`；
- non-actionable B2_READY不再有execution eligibility或trade expectancy；诊断仅报告pattern、
  trigger/future structure、quality、Entry Room、days since anchor和eligibility reasons；
- 分组固定为预先批准的quality、Entry Room和D+1/D+2/D+3/D+4/D+5+，不搜索新阈值、不升级规则。

## Phase 2D.0 descriptive research closeout

- PR #9（diagnosis）与PR #11（robustness/tail-gap）均以普通merge commit进入main；
  PR #9集成为`b199d4905d1d016c08a98cfde80672d60125af54`，PR #11集成为
  `8c288efae5abda486e723c49c94f19aa55e556f5`。项目级Codex配置独立以PR #12集成
  `c1d463366f0133043cc3733043fced1f52c56a88`；这些提交均不改变策略语义或阈值。
- 描述性输入仍为corrected episodes（SHA-256
  `66d5943ffd4c83d8348d7b559ef9aa8ab9c041525471108a2f724fbedd84b093`），
  `evaluate_strategy_calls=0`；固定快照为`snap-2026-07-31-b5f84004de8a`。
- ACTIONABLE B1_READY整体严格E[R]=`-0.1580`；setup_quality`>=80`原始
  `+0.1557`、entry_quality`>=80`原始`+0.1686`，但cap5后分别为`-0.1232`、
  `-0.1157`且年度方向不稳定，均不提升为策略规则。
- `R>=10`赢家的理论风险中位数约`0.52%`，普通赢家约`1.56%`；执行真实性仍未解决。
- ACTIONABLE B2_READY BREAKOUT_GAP_FILL整体严格/保守E[R]为`+0.0399/+0.0321`，
  年度方向不稳定且样本置信度低；BREAKOUT_TRIGGER_FILL仍有171个ambiguous episode、
  158只唯一股票，作为未来盘中数据候选。
- 状态：`DESCRIPTIVE_SIGNAL_STUDY_COMPLETE`；未批准任何策略修改，不进入Phase 2D.1，
  不接入5分钟数据、回测或新的统计切片。

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

## Phase 2C.2C正式冻结

- 内容提交：`b49c91285b9bb3b4294bc2b4c569c5f76e23ace0`；main普通merge提交：
  `6c601bfb511947768e5906b16620eb365a03399f`；annotated tag：`phase-2c2c`；
  内容提交与main集成提交tree一致；
- 固定快照：`snap-2026-07-31-b5f84004de8a`；验收输出hash：
  `927ef1d39d38e5b75e3cfbc696158befb507a468bd32c9db4ecdb28da492bd5c`；
- 横截面：universe=3191，ACTIONABLE=78，B1_PREP=0；B1_PREP=0是实际横截面结果，
  不是阻塞项；
- `603918`保持non-actionable；当未来交易日无法由离线快照可靠确定时，
  `for_trade_date`为`null`，不猜测周末或法定节假日；
- 本冻结只覆盖盘后TradePlan执行层，不改变既有setup生命周期、Entry Room、评分或
  策略阈值语义；不进入回测、aux-backfill或自动交易。

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

本Vault承认annotated tag `phase-2d0`解引用的策略内容提交为冻结实现。
main通过不同SHA但相同tree的merge commit集成该实现；只要内容提交仍为main祖先、
tag指向正确、tree和策略文件哈希一致且代码工作区干净，drift状态为CURRENT。
未经ADR采纳的后续实验不自动成为本知识库的冻结策略。
