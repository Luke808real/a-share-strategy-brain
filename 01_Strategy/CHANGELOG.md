# 策略知识库变更日志

## 2026-08-02 — Phase 2D.1A Execution Reality Check完成

- PR #13以普通merge commit`bd0121394a235b7c88219db44b6e187328c3198c`进入main，内容提交为
  `b59f8e75b23588562af14babed0700f28b6e0066`；仅增加冻结episodes的T+1 daily-bar执行现实检查，
  不修改B1/B2、评分、阈值或策略文件；
- T1 gross E[R]：B1 ALL严格/保守`+0.0049/-0.2230`；B1 setup>=80
  `+0.1707/-0.0204`；B1 entry>=80`+0.3954/+0.1121`；B2 GAP`-0.0642/-0.0642`；
  B2 TRIGGER仍有170个order-ambiguous episodes；
- B1 large-R赢家在T+1下仍存在，但可执行edge对交易摩擦敏感；price-limit execution为
  `NOT_MODELED`；历史优化保持冻结，未推广任何策略规则；
- 状态：`PHASE 2D.1A EXECUTION_REALITY_CHECK_COMPLETE`；下一步等待人工设计最小
  Forward Paper Validation / Daily Runner。

## 2026-08-02 — Phase 2D.0 descriptive research收口

- corrected episodes描述性研究以ACTIONABLE cohort为准：B1_READY整体严格E[R]为`-0.1580`；
  setup_quality`>=80`和entry_quality`>=80`原始分别为`+0.1557`、`+0.1686`，cap5后
  分别为`-0.1232`、`-0.1157`且年度不稳定，因此不提升为策略规则。
- `R>=10`赢家理论风险中位数约`0.52%`，普通赢家约`1.56%`；执行真实性仍是未解决限制。
- B2 GAP整体严格/保守E[R]为`+0.0399/+0.0321`，年度不稳定、低置信度；B2 TRIGGER
  有171个ambiguous episode、158只唯一股票，留作未来盘中数据候选。
- 本次仅增加描述性诊断与tail/gap检查，未修改B1/B2、评分、阈值或策略文件；
  Phase 2D.0状态为`DESCRIPTIVE_SIGNAL_STUDY_COMPLETE`，不进入Phase 2D.1。

## 2026-08-02 — Phase 2D.0 B2 execution outcome correction

- 人工批准PR #10进入main；内容提交为`5fbc275`，main普通merge提交为`cbf9d49`；
- 仅修正冻结episodes的`B2_READY`执行结果标注：旧的limit-style开盘成交改为breakout-trigger
  语义；未修改策略结构、阈值、strategy.yaml或策略文件哈希；
- 旧episodes哈希`23d3ff935cb44d523288c744c39abc231ce2c19a486b56ddfe057aa0809130af`标记为
  `SUPERSEDED_FOR_B2_EXECUTION_OUTCOME`；corrected episodes哈希为
  `66d5943ffd4c83d8348d7b559ef9aa8ab9c041525471108a2f724fbedd84b093`；
- B2_READY严格E[R]由`-0.0979`修正为`-0.0079`，保守E[R]=`-0.1216`；B1_READY严格
  `-0.1580`、B2_CONFIRMED严格`-0.0599`保持不变；
- 603918回归由错误的10.68 `OPEN_FILL/+2.5161R`修正为`NO_FILL/NONE/REWARD_NON_POSITIVE_AT_TRIGGER`；
- 严格/保守差异记录为日线OHLC ambiguity observation，5m数据仅作为未来参考；ashare-lake仍未集成；
- PR #9 diagnosis切换corrected episodes，non-actionable B2_READY不再作为可执行交易期望。
- corrected diagnosis输出哈希为`diagnosis.json`=`ea717b3492d3656d36adb912dada6759664d89b18e5d5b804eebb96ae8ee20ee`、
  `diagnosis.md`=`829f2a524e0013845a9a7b6b656e79898bc2de326743871d6689647d7b788d7b`；
- actionable B2_READY ambiguity：172/1605=`0.1072`，strict/conservative差值为`-0.1137R`；
  non-actionable cohort不再输出trade expectancy。

## 2026-08-02 — Phase 2D.0正式基线

- 人工批准PR #8进入main；策略实现内容提交为`e865de4`，main普通merge提交为
  `2cabcf6`，annotated tag `phase-2d0`解引用到`e865de4`，两者tree一致；
- 固定快照`snap-2026-07-31-b5f84004de8a`以`FINAL_VINTAGE_CAUSAL`模式完成结果基线：
  3191只、589个confirmed sessions、31422个episodes、3482.59秒；
- ACTIONABLE严格/保守E[R]：B1_READY=`-0.1580/-0.1902`、B2_READY=
  `-0.0979/-0.1111`、B2_CONFIRMED=`-0.0599/-0.0684`；STRUCTURAL B2_READY
  严格E[R]=`+0.0803`；高质量setup与entry分组的正向结果仅作observation；
- 保留历史vintage真实性、覆盖/生存偏差、OHLC顺序、成本与A股T+1限制；不因负期望
  调整策略，不进入Phase 2D.1；下一步只做既有episodes的低成本baseline diagnosis。

## 2026-08-01 — Phase 2C.2C基线冻结

- 人工批准PR #7进入main；策略实现内容提交为`b49c912`，main普通merge提交为
  `6c601bf`，annotated tag `phase-2c2c`解引用到`b49c912`，两者tree一致；
- 固定快照`snap-2026-07-31-b5f84004de8a`的TradePlan横截面为3191只，
  `ACTIONABLE=78`、`B1_PREP=0`；B1_PREP=0记录为真实结果，不构成阻塞；
- `603918`保持non-actionable；无法可靠知道下一开市日时`for_trade_date=null`；
- 本次仅冻结盘后TradePlan执行层，不修改冻结策略、strategy.yaml阈值、回测、
  aux-backfill或自动交易。

## 2026-08-01 — phase-2c2b正式基线

- 人工批准Phase 2C.2B全市场数据链路验收；策略内容提交`4a4fb8c`由main普通
  merge commit`d9e2065`集成，annotated tag`phase-2c2b`解引用到内容提交；
- 固定快照`snap-2026-07-31-b5f84004de8a`的`data-validate`为`valid=true`、issues=0；
- formal、CONFIRMED-only、`pool_mode=formal` screen为3191只、1,844,543行，
  hash=`9abb16e4a5720503e4ffea5462067dc1b476d8022f0593a657c328f9836920ec`；
- 20只rebuild replay为11,378行、逐字段一致，hash=
  `6c2ffc2235fabd9e32c3aff227fc27d9aac622cb68a1fa6c9ba99a8d1d18b418`；
- 本次仅冻结数据验收与Tushare adjusted preclose校验修复，不改变B1/B2/S1/INVALID、
  Entry Room、评分或阈值，不启动回测、报告或自动交易。

## 2026-07-31 — phase-2c2a正式基线

- 人工批准Phase 2C.2A进入main；策略内容提交`99190fd`由main merge commit
  `c9ffe49`集成，annotated tag `phase-2c2a`解引用到内容提交；
- 冻结D-026：Tushare Pro主日线、AKShare日线校验/涨停池、BaoStock历史补录
  与第三校验；Parquet原始层 + DuckDB元数据 + canonical快照；
- 冻结显式对账：`PROVISIONAL/CONFIRMED/INCOMPLETE/CONFLICTED/QUARANTINED`，
  Tushare+AKShare一致才CONFIRMED，BaoStock滞后不降级，冲突隔离不发布；
- 冻结canonical可追溯：整行取自selected_provider，禁止字段拼接，manifest记录
  源文件与canonical哈希，bootstrap/update幂等且快照不可变；
- Token仅从环境变量读取并全程脱敏；真实行情与`.env`不入Git；
- 审查修复写入锁、中断恢复、历史行回退与同源冲突隔离；默认离线测试187项、
  integration测试15项通过；未修改B1/B2/S1/INVALID/Entry Room语义或
  `strategy.yaml`阈值，未启动全市场扫描或回测。

## 2026-07-31 — phase-2c1正式基线

- 人工批准Phase 2C.1进入main；策略内容提交`0b01abb`由main merge commit
  `8052ca7`集成，annotated tag `phase-2c1`解引用到内容提交；
- 冻结D-025：支持任意合法沪深主板单股的`inspect`与`replay`，并明确两种评价模式；
- 冻结Provider质量传播、重复日线和缺失字段边界；代码格式合法不等于当日行情可用；
- 603918复验观察到BaoStock日线延迟，`STALE_DATA`正确传播；这不是策略或实现缺陷；
- 不包含全市场扫描、数据库、Parquet、缓存、报告、回测、自动交易或盘中逻辑；
- 未修改B1、B2、S1、INVALID、Entry Room语义或`strategy.yaml`阈值。

## 2026-07-31 — phase-2b3正式基线

- 人工批准D-024 Setup生命周期与入场价值解耦；
- `setup_stage`不再读取target S1、risk/reward或Entry Room；
- B2量价确认不再读取S1空间；
- 冻结`setup_quality_score`与`entry_quality_score`分层；
- annotated tag `phase-2b3`指向策略内容提交`a503709`；
- main集成提交`78ff791`与内容提交为祖先关系且tree完全一致；
- Phase 2C.0确认BaoStock、AKShare、inspect和point-in-time replay真实链路可用；
- 任意股票支持与Provider边界问题留给Phase 2C.1，尚未进入全市场扫描。

## phase-2b3

- 在phase-2b2真实数据链路、快照和Entry Room语义上解除结构/入场价值耦合；
- 保留INVALID作为结构终止，S1事件只影响新建仓资格；
- OPEN_SPACE允许保持`B1_READY`或`B2_READY`；
- 未调整任何策略阈值。

## 2026-07-30 — Vault初始化

- 以annotated tag `phase-2b2`作为冻结策略基线；
- 建立策略真源、规则目录、状态机、案例、ADR与研究分层；
- 录入三个成功观察案例和近期博客观察；
- 增加本地索引、上下文包与完整性校验工具；
- 未修改选股代码、YAML阈值、Provider或策略状态规则。

## phase-2b2

- 双价格体系；
- 风险快照统一先冻结后生效；
- immediate resistance与target S1分层；
- Entry Room和setup终止语义；
- 单股、无未来数据的真实日线内存回放。
