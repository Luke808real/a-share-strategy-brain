# Codex实施日志

## 2026-08-02 — RELAXED MEMORY BUDGET + FULL-MARKET SCALING CURVE

- 旧 hard 1.8GB guard 标记为 `SUPERSEDED_CONSERVATIVE_GUARD`；
  新 policy：soft 6GB / hard 10GB / swap delta abort 1GB；
- scaling（fresh process）：200=23.56s/2.22GB/swap0；
  500=61.32s/4.49GB/swap0；1000=122.43s/6.32GB/swap delta 726MB；
- 3191 未运行：1000 swap delta > 512MB gate，且线性外推 RSS 超 10GB 风险；
- RSS scaling class：SUBLINEAR（per code：11.1MB→9.0MB→6.3MB）；
  runtime 接近线性；
- incremental regression：7/30 rebuild 2.84s、7/31 incremental 0.76s、
  7/31 rebuild 2.65s；semantic fields 一致，仅 600906 `generated_at`
  provenance 差异（无 7/31 bar 的既有行为）；
- NEXT：`OPTIMIZE_RETAINED_PAYLOAD_MEMORY`（进入 3191 前需处理）。

## 2026-08-02 — CLEAN PERF PR #19

- branch `perf/screen-exact-one-pass`，PR #19 Draft；
- 生产实现：bounded loader + exact one-pass indicators（`IndicatorPrefixView`，
  `precomputed_indicators`/`indicator_end_index` API；无 monkeypatch）；
- 20-code：reference 60.23s → optimized 2.78s，output hash 与 reference 一致；
  full pytest 319 passed / 16 deselected；
- blocker：200-code optimized cold rebuild peak RSS 2.13GB > 1.8GB guard；
  500/3191 deferred；需要 FIX_RESOURCE_USAGE；
- PR #18 标注 promoted to #19；PR #16/#18 保持 Draft。

## 2026-08-02 — EXACT PYTHON ONE-PASS PRECOMPUTE V0.1

- DuckDB feature path NOT_SELECTED（Decimal exactness 失败，Python one-pass 已够快）；
- Prefix equivalence：11,173 rows compared，diff=0；
- Reference cold rebuild 60.23s → optimized 2.75s，speedup 21.87x；
- output hash / persisted state hash 均相等；
- counters：reference calculate_indicators calls=11,173、IndicatorPoint built=3,267,065；
  optimized full-series computations=20、IndicatorPoint built=11,173、
  calculate_indicators lookups=11,173；
- peak RSS ~502MB；
- decision：`PROMOTE_ONE_PASS_PRECOMPUTE_TO_PERF_PR`。

## 2026-08-02 — FEATURE PRECOMPUTE V0.1 MICRO PROTOTYPE

- Reference features（20 codes, 11,173 rows）one-pass Python：0.266s；
- DuckDB raw rolling sums/min/max：0.006s（约 40x）；
- Exact equivalence：FAILED；semantic diff count=18,956（末位 Decimal 舍入差异，
  DuckDB DECIMAL(38,28) window sum vs Python exact Decimal addition）；
- Integration experiment：NOT RUN（diff gate blocked）；
- Decision：`FIX_FEATURE_EQUIVALENCE`；
- 下一步候选：提高 DuckDB 精度或改用 Python O(N) prefix-sum 精确实现。

## 2026-08-02 — COLD STRATEGY REBUILD COMPUTE PROFILE V0.1

- 20-code cold rebuild（cProfile 口径）92.4s；bounded loader 下 peak RSS 419MB；
- strategy evaluation 89.4s（96.7%）；indicator/rolling 85.5s（92.5%）；
  canonical load 0.75s；evaluate_strategy_calls=11,173；
- `calculate_indicators` 每 bar 重新切片 MA/position_120 -> 每 code O(N²)；
- 可向量化纯 feature 占比约 92.5%；micro prototype 未做（时间/内存 guard）；
- STORAGE_DECISION：DUCKDB_QUERY_LAYER=APPROVED_DIRECTION，
  DUAL_PARQUET_PROJECTIONS=DEFER；
- NEXT 建议：`BUILD_FEATURE_PRECOMPUTE_V0_1`。

## 2026-08-02 — LOCAL ANALYTICS STORAGE SPIKE V0.1

- PyArrow bounded loader：20-code 0.584s、200-code 1.26s（3191 物化因内存 guard 跳过）；
- DuckDB 直查当前 canonical Parquet：20-code 0.059s、200-code 0.085s、
  3191-code 0.181s、latest-day 0.069s；
- DuckDB code-major projection：20-code 0.024s、200-code 0.069s、
  3191-code 0.157s；date-major latest-day 0.002s；
- peak RSS 最高约 1.43GB（含 projection 构建）；CHDB_NOT_AVAILABLE；
- 结论：`ADOPT_DUCKDB_QUERY_LAYER` + `ADOPT_DUAL_PARQUET_PROJECTIONS`（可选）；
  不迁移 canonical 到 .duckdb；storage 影响 data load，不影响 60s cold strategy rebuild。

## 2026-08-02 — DAILY SCREEN FAST-PATH LOADER FIX + PARTIAL BENCHMARK

- perf branch 增加 bounded canonical loader：`load_canonical_market(codes=...)`
  使用 row-group metadata + `iter_batches`，不再无条件 `to_pylist()` 全量物化；
  `run_screen` 将 `--codes` 传入 loader；策略语义不变；
- 20-code probe：loader rows_read 3,145,728、materialized 11,173、0.59s、
  peak ~241MB；rebuild 7/30 59.05s、incremental 7/31 0.74s、rebuild 7/31 60.47s；
- 等价验证未完成：重跑时 RSS guard 中止（PID 68766 超内存），
  200/500/3191 全部 defer；
- 结论：`FAST_PATH_LOADER_FIX_REQUIRED` 已实施；`FAST_PATH_ALREADY_SUFFICIENT`
  尚未确认。

## 2026-08-02 — PUBLIC CHIP SNAPSHOT PROBE FAILED

- Tushare `cyq_chips`/`cyq_perf` 不可用（token 无效）；AKShare
  `stock_cyq_em` 不可用（eastmoney proxy 连接失败）；
- 未打印/记录 token；未自研筹码分布；
- 2026-08-03 frozen watch 不受影响。

## 2026-08-02 — CONTEXT V0.1 CLOSEOUT

- 正式结论：WEEKLY_CONTEXT_V01 / PRICE_VOLUME_CONTEXT_V01 =
  `REJECT_FOR_PROMOTION`；WASHOUT_POSSIBLE=`OBSERVE_ONLY`；
  JOINT_CONTEXT_V01=`REJECT`；
- RAW_WEEKLY_FEATURES=`UNDECIDED`；RAW_PRICE_VOLUME_FACTS=
  `RETAIN_AS_DESCRIPTIVE_EVIDENCE`；
- `NO_FURTHER_IN_SAMPLE_THRESHOLD_TUNING=true`；不做更多 slicing/threshold search。

## 2026-08-02 — HISTORICAL CONTEXT VALIDATION V0.1 + INCREMENTAL SCREEN AUDIT

- 历史验证输入 corrected episodes `66d5943f...`（31,422）+ Phase 2D.1A execution
  reality；`evaluate_strategy_calls=0`；
- H1 WEEKLY FAVORABLE → REJECT；NEUTRAL/UNFAVORABLE → OBSERVE；
- H4 WASHOUT_POSSIBLE 10bp `+0.1316` 但 cap5 `-0.8500`、年度不稳定 → OBSERVE；
- JOINT_CONTEXT_V01 10bp `-0.4851`、cap5 `-1.0598` → REJECT；
- 无 PROMOTE_CANDIDATE；sector 不参与；
- Incremental screen：state 已存在，但 `screen` 仍 full-materialize canonical；
  未跑全市场 benchmark，`trade-plan` ~4s；
- 分支：`research/context-historical-v01`（PR #15）、
  `perf/daily-screen-fast-path`（PR #16），均 Draft，不 merge。

## 2026-08-02 — FORWARD_EPOCH_0 HUMAN APPROVED FROZEN

- 2026-08-03 final human watch hash `8847f503...` 经 human 批准；
  status=`HUMAN_APPROVED_FROZEN`；
- CORE_B1=600227/000659/600578；B1_PULLBACK_WAIT=600844/002534；
  key B2 trigger observation=002242；
- 后续 historical research 不得 retroactively 修改此 epoch。

## 2026-08-02 — MAINLINE CONTEXT V0.2 ACCEPTED + 2026-08-03 FINAL HUMAN WATCH

- v0.2 corrected hash `9a53e500...` 被接受；`PIT_SUPPORT_FIX=ACCEPTED`；
  `V01_SUPPORT_WARNING=INVALID_FOR_RESEARCH_PROMOTION`；
- Entry Timing 移除未验证 3% 阈值，改为纯几何 `WAIT_TRIGGER / TRIGGER_CROSSED`；
- `OBSERVE_NOW_61_OF_78` 不再作为 human shortlist；
- 2026-08-03 final decision sheet hash `8847f503...`；
  buckets：CORE_B1=3、B1_PULLBACK_WAIT=2、B2_TRIGGER_WATCH=45、
  B2_POST_TRIGGER_WATCH=12、DIAGNOSTIC_ONLY=16；
- sector 仍为 `LOW_CONFIDENCE_PROXY`；production_strategy_changed=false。

## 2026-08-02 — FORWARD_EPOCH_0 Mainline Context v0.1 + Audit checkpoint

- 冻结研究基线：overlay v0.1 hash `d527aa1d...`，audit v0.1 hash
  `43407eed...`，source plan hash `0d1bb2b9...`；
- 代码 research branch `research/mainline-context-v01` head `eedd581c`，
  Draft PR #14 创建，未 merge；
- Audit结论：`SYSTEMATIC_OVERLAY_BIAS_SUSPECTED=YES`，原因是7/31冻结support被
  retroactively用于7/29–7/30判断；`SUPPORT_BREAK_V01=RESEARCH_INVALID_FOR_PROMOTION`；
- `PRICE_VOLUME_FACTS=RETAIN`，`WEEKLY_CONTEXT=RETAIN_FOR_RESEARCH`，
  `SECTOR_V01=LIMIT_UP_POOL_SECTOR_PROXY/LOW_CONFIDENCE/SELECTION_BIAS_PRESENT`；
- production_strategy_changed=false，8/3 forward plan changed=false；
- 下一轮：MAINLINE PULLBACK OBSERVATION OVERLAY v0.2 — CORRECTED。

## 2026-08-02 — Phase 2D.1A Execution Reality Check完成

- PR #13已获批准并以普通merge commit合入main；内容提交
  `b59f8e75b23588562af14babed0700f28b6e0066`，main集成提交
  `bd0121394a235b7c88219db44b6e187328c3198c`；
- 只读取冻结Phase 2D.0 signals与corrected episodes，输入快照为
  `snap-2026-07-31-b5f84004de8a`，31422条episodes，`evaluate_strategy_calls=0`；
- T+1 daily-bar结果：B1 ALL严格/保守`+0.0049/-0.2230`；B1 setup>=80
  `+0.1707/-0.0204`（10bp `+0.0204/-0.1572`）；B1 entry>=80
  `+0.3954/+0.1121`（10bp `+0.2605/-0.0104`，20bp `+0.1280/-0.1313`）；
  B2 GAP `-0.0642/-0.0642`；B2 TRIGGER仍有170个order-ambiguous episodes；
- B1 large-R赢家在T+1下仍存在，但可执行edge对摩擦敏感；price-limit execution为
  `NOT_MODELED`；未修改策略规则、阈值或历史优化结论；
- 最终验证：`316 passed, 16 deselected`，compileall与diff-check通过；冻结字段与
  `frozen_event_hash`未变化；
- 状态：`EXECUTION_REALITY_CHECK_COMPLETE`；不进入5m数据、阈值搜索、评分优化、组合回测或策略修改。

## 2026-08-02 — Phase 2D.0 descriptive research收口

- PR #9 diagnosis以普通merge commit`b199d4905d1d016c08a98cfde80672d60125af54`进入main；
  项目Codex配置作为独立PR #12以`c1d463366f0133043cc3733043fced1f52c56a88`进入main；
  PR #11 descriptive robustness/tail-gap以普通merge commit
  `8c288efae5abda486e723c49c94f19aa55e556f5`进入main。
- 仅读取corrected episodes（SHA-256
  `66d5943ffd4c83d8348d7b559ef9aa8ab9c041525471108a2f724fbedd84b093`）完成描述性
  diagnosis、tail、gap与风险几何检查；`evaluate_strategy_calls=0`，未replay、screen、provider或finalize。
- ACTIONABLE B1_READY整体严格E[R]为`-0.1580`；setup/entry`>=80`原始分别
  `+0.1557/+0.1686`，但cap5后分别为`-0.1232/-0.1157`，年度不稳定，未升级为策略规则。
- `R>=10`赢家理论风险中位数约`0.52%`，普通赢家约`1.56%`，执行真实性未解决；
  B2 GAP整体严格/保守`+0.0399/+0.0321`但年度不稳定且低置信度；B2 TRIGGER
  有171个ambiguous episode、158只唯一股票。
- 结论：`DESCRIPTIVE_SIGNAL_STUDY_COMPLETE`；无策略修改批准，不进入Phase 2D.1。

## 2026-08-02 — Phase 2D.0 corrected B2 outcome baseline

- PR #10已Ready并以普通merge commit合入main；内容提交`5fbc275ad12b4089ac5deafd5ad4dd17e7143de5`，
  main集成提交`cbf9d49424fd487702d3bbeb6f7f733dd077dcbb`；
- 仅对`snap-2026-07-31-b5f84004de8a`的31422条冻结episodes做B2_READY relabel，未重放、未重筛、
  未下载行情，`evaluate_strategy_calls=0`；B2_READY 10952条中6686条派生结果变化；
- 旧hash `23d3ff935cb44d523288c744c39abc231ce2c19a486b56ddfe057aa0809130af`保留并标记
  `SUPERSEDED_FOR_B2_EXECUTION_OUTCOME`；新hash为
  `66d5943ffd4c83d8348d7b559ef9aa8ab9c041525471108a2f724fbedd84b093`；
- B1_READY严格E[R] `-0.1580`不变；B2_READY严格/保守为`-0.0079/-0.1216`；B2_CONFIRMED严格
  `-0.0599`不变；603918错误开盘成交回归已修正为`NO_FILL`；
- 严格与保守差异只记录为日线OHLC ambiguity observation，不升级策略规则；未来5m数据仅作参考；
  ashare-lake仍为`NOT_INTEGRATED`；
- PR #9继续Draft，诊断改用corrected episodes，不再引用non-actionable B2_READY旧交易期望。
- PR #9 corrected diagnosis运行`0.7725s`，`evaluate_strategy_calls=0`；输出哈希为
  `diagnosis.json=ea717b3492d3656d36adb912dada6759664d89b18e5d5b804eebb96ae8ee20ee`、
  `diagnosis.md=829f2a524e0013845a9a7b6b656e79898bc2de326743871d6689647d7b788d7b`；
- actionable B2_READY ambiguity为172/1605=`0.1072`，strict/conservative差值=`-0.1137R`；
  non-actionable cohort只保留结构性分布，不解释为可执行收益。

## 2026-08-02 — Phase 2D.0基线冻结

- PR #8已标记Ready并以普通merge commit合入main；内容提交
  `e865de484e40e45b1d2044ee1c58247c76f3a758`，main集成提交
  `2cabcf6ca0885993185453c3384fcf346fa4ddff`，annotated tag为`phase-2d0`；
- 内容提交与main集成提交tree一致；固定快照为
  `snap-2026-07-31-b5f84004de8a`，模式为`FINAL_VINTAGE_CAUSAL`；
- 3191只、589个confirmed sessions、31422个episodes，运行时长3482.59秒；
- ACTIONABLE严格/保守E[R]：B1_READY=`-0.1580/-0.1902`，B2_READY=
  `-0.0979/-0.1111`，B2_CONFIRMED=`-0.0599/-0.0684`；STRUCTURAL B2_READY
  严格E[R]=`+0.0803`；
- setup_quality `>=80`严格/保守E[R]=`+0.0257/+0.0084`，entry_quality `>=80`
  严格/保守E[R]=`+0.0769/+0.0621`；均为观察，不升级为策略规则；
- 保留FINAL_VINTAGE非strict historical PIT、survivorship/coverage bias、daily
  OHLC ambiguity、成本未建模和A股T+1未完整建模等限制；
- 默认验证`.venv/bin/pytest -q`为269 passed、16 deselected，compileall与diff-check通过；
  未重跑full study，未修改策略或阈值；
- 下一步仅从既有`episodes.parquet`做低成本baseline diagnosis：stage×setup_quality、
  stage×entry_quality、actionable与non-actionable B2_READY、Entry Room以及win/loss R
  分解；不重放、不重筛、不实现event cache。

## 2026-08-01 — Phase 2C.2C基线冻结

- PR #7已由人工审查后标记Ready并以普通merge commit合入main；内容提交
  `b49c91285b9bb3b4294bc2b4c569c5f76e23ace0`，main集成提交
  `6c601bfb511947768e5906b16620eb365a03399f`，annotated tag为`phase-2c2c`；
- 内容提交与main集成提交tree一致；固定快照为
  `snap-2026-07-31-b5f84004de8a`，验收输出hash为
  `927ef1d39d38e5b75e3cfbc696158befb507a468bd32c9db4ecdb28da492bd5c`；
- 横截面为universe=3191、`ACTIONABLE=78`、`B1_PREP=0`，其中B1_PREP=0为真实
  结果而非阻塞；603918保持non-actionable；
- 无离线交易日历时TradePlan的`for_trade_date`显式为`null`，不使用自然日猜测；
- 默认测试`245 passed, 16 deselected`，compileall和diff-check通过；未进入回测、
  aux-backfill或自动交易。

## 2026-08-01 — Phase 2C.2B基线冻结

- 人工批准全市场日线验收结果进入正式基线；策略内容提交为`4a4fb8c`，main通过
  普通merge commit`d9e2065`集成，annotated tag`phase-2c2b`解引用到内容提交；
- 固定快照`snap-2026-07-31-b5f84004de8a`验证`data-validate valid=true/issues=0`；
- formal、CONFIRMED-only、`pool_mode=formal` screen为3191只、1,844,543行，
  hash=`9abb16e4a5720503e4ffea5462067dc1b476d8022f0593a657c328f9836920ec`；
- 20只rebuild replay为11,378行且逐字段一致，hash=
  `6c2ffc2235fabd9e32c3aff227fc27d9aac622cb68a1fa6c9ba99a8d1d18b418`；
- 4a4fb8c仅修复Tushare adjusted preclose校验语义和测试，未修改策略语义、阈值、
  canonical、screen或pool；不进入回测或报告阶段。

## 2026-07-31 — Phase 2C.2A基线收口

- 人工批准多数据源历史行情仓库与每日增量更新进入正式基线；
- 策略内容提交为`99190fda6aabb0abd1b6d6c1c1f0b2b019a4c42f`，main通过普通
  merge commit `c9ffe49052c86e305734c4ea47c01d43835ff251`集成；
- annotated tag `phase-2c2a`解引用到策略内容提交，内容tree与main集成tree一致；
- 冻结D-026：Tushare主日线/AKShare校验/涨停池/BaoStock补录职责、Parquet+DuckDB
  仓库、五状态显式对账、canonical整行可追溯、快照不可变与point-in-time读取；
- 独立审查并修复：写锁串行化、中断恢复清理、错误落库Token脱敏、修订窗口历史
  原始行回退、涨停池同源冲突隔离、manifest源文件并集；
- 五只股票真实验收通过（220行CONFIRMED、0冲突、validate全绿），默认离线187项、
  integration 15项通过；未修改策略语义或YAML阈值，未启动全市场扫描或回测。

## 2026-07-31 — Phase 2C.1基线收口

- 人工批准任意沪深主板单股票检查与Provider边界加固进入正式基线；
- 策略内容提交为`0b01abb057fea56ae8d06545585de7ac7d877522`，main通过普通merge commit
  `8052ca7fe832bc4134390ba14c8911022b143c7e`集成；
- annotated tag `phase-2c1`解引用到策略内容提交，内容tree与main集成tree一致；
- 冻结D-025：共享代码解析、STATELESS_INSPECT、POINT_IN_TIME_REPLAY、Provider质量
  传播及BaoStock重复/异常边界；
- 603918复验确认BaoStock 2026-07-31日线延迟时不会伪造数据，replay输出`STALE_DATA`；
- 默认离线测试148项、integration测试14项通过；未修改策略语义或YAML阈值，未启动
  Phase 2C.2A、全市场扫描、数据库、Parquet、报告、回测或自动交易。

## 2026-07-30 — Strategy Brain初始化

- 创建独立Obsidian Vault；
- 建立冻结策略、候选规则、案例、ADR、研究和会话分层；
- 实现确定性案例索引、上下文包和Vault校验；
- 增加完全离线测试；
- 未修改`a-share-limit-pullback`策略代码。

后续每次Codex实现记录任务边界、commit、测试、黄金样本变化及是否冻结。

## 2026-07-31 — KB-1.2会话归档与上下文回流

- 增加本地Inbox、Raw、Digest、Processed、审核队列及导入/同步清单；
- 支持结构化手工会话与官方ChatGPT ZIP/JSON的本地预览、筛选和去重导入；
- 增加确定性Digest、显式审核、案例/变更请求提升和带依赖保护的会话清理；
- 将已审核会话纳入Full Pack，并增加基于同步清单的Delta Pack；
- 增加隐私边界、ChatGPT Project流程和两个iOS快捷指令说明；
- 未访问网络，未修改策略代码、strategy.yaml或冻结策略结论。

## 2026-07-31 — KB-1.3 GitHub知识桥接

- 增加Agent Exchange Schema、模板、写入政策和PR模板；
- 增加Agent Case校验、人工复核、正式案例提升和Reasoning Index；
- 增加Change Request实现门禁、代码Issue草稿与两仓闭环说明；
- 增加GitHub pull/publish/status桥接脚本及敏感信息扫描；
- 扩展Full/Delta Pack，区分待审核输入、已审核推理、获批变更与代码drift；
- 未修改选股策略代码、参数、STRATEGY_MASTER冻结结论。

## 2026-07-31 — Phase 2B.3基线收口

- 人工批准D-024 Setup生命周期与入场价值解耦进入正式冻结基线；
- 策略内容提交为`a5037091774d0b8d0b6ba686c332d012e640d7e6`；
- main集成提交为`78ff7915e9bc77dca1201adea9ccd2febb58f15b`；
- 两提交为祖先关系、diff为空且tree完全一致；
- annotated tag `phase-2b3`解引用到策略内容提交；
- 新增支持等价tree merge commit的确定性drift检查及离线测试；
- Phase 2C.0真实链路验收通过，Provider边界修复留给Phase 2C.1；
- 未修改策略代码或strategy.yaml阈值，未启动Phase 2C.1。
