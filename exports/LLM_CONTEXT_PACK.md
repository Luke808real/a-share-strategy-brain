# LLM Context Pack

> 用途：ChatGPT Project/Codex上下文。由本地确定性工具生成；不包含图片二进制或完整历史聊天原文。

## 1. Agent Handoff

> Source: [[00_Project/AGENT_HANDOFF]]

AS_OF: 2026-08-10T16:01:00+08:00

## READ FIRST

1. [[00_Project/AGENT_HANDOFF]]
2. [[00_Project/CURRENT_STATE]]
3. [[00_Project/PROJECT_CHARTER]]
4. [[00_Project/ROADMAP]]
5. [[01_Strategy/STRATEGY_MASTER]]
6. [[01_Strategy/RULE_CATALOG]]
7. 与任务直接相关的 Research / Decision 文档

不需要阅读整个仓库。先阅读当前任务的结果和证据，再决定是否可以推进。

## PROJECT

将 A 股低位/中低位强势涨停后的回调、B1/B2 与 SECOND_LAUNCH 过程，做成数据可靠、
语义明确、可统计验证且最终可支持人工决策的系统。

## WHERE WE ARE

PRE_R9_DATA_CLOSURE。Phase A 正在 closing；Phase B/C 处于 integration / closure；
Phase D 是下一 product milestone；Phase E+ 未获授权。PRIMARY_OOS=false，
OOS_ROWS=0，PRODUCTION=false，FORWARD=false，TRADEPLAN=false。

## FROZEN / DO NOT CHANGE

- [[01_Strategy/STRATEGY_MASTER]] 的冻结策略内容。
- [[01_Strategy/RULE_CATALOG]] 的冻结语义、B1/B2、setup_stage、Entry Room 和分数。
- [[01_Strategy/BASELINE_MANIFEST.yaml]]。
- 未经明确授权的 a-share-limit-pullback 或 ashare-lake 代码。
- OBSERVATION / HYPOTHESIS 的结论等级。

## CURRENT EXECUTION

ASL_BOUNDED_HISTORICAL_ST_BACKFILL_V01：RUNNING / RESULT_PENDING。
范围为 2026-03-30..2026-08-07，SYMBOL_N=3193，
POSITIVE_BAR_SYMBOL_DAY_N=286404，DERIVED_SUSPENSION_GAP_N=474。不得虚构最终 PASS，
也不得在结果出现前启动 state generation、R9、Forward、Production 或 TradePlan。

## OPEN BLOCKERS

P0：backfill/audit、08/07 state rebuild、ACTIVE_SETUP、immutable 10:30 checkpoint、
TTL suspension-age 语义、R9 provenance/old ASL_CODE_SHA pin。完整清单：
[[00_Project/BLOCKERS]]。

## NEXT GATE

先取得 bounded backfill 的 post-write audit，执行 exact-SHA independent review，再分类
PASS / BLOCKED 并更新 current documents。NEXT_GATE != AUTO_EXECUTE。

## DO NOT DO

- 不运行 full-market、R9、state generation、Forward、Production 或 TradePlan。
- 不处理当前 ASL backfill 本身，不改变 frozen rule / threshold。
- 不把研究观察写成 VALIDATED，不删除历史文档。
- 不直接 push main，不 merge PR，不保存 token、账号或本地绝对路径。

## AUTHORITY SHAS

- ASL_PROJECT_SHA: 0f16f3991a4c8793f96a585ecc938923edf978ac.
- V Flash review SHA: c5bd5b58f67356cd9bbd346e470c7ae325ffccb6.
- R9 freeze commit: 4d9e8fd7cdf0d3e4c631f8a970451c95f8c56aed.
- R7 coefficient SHA:
  39de709f424194be1a28d7e8e21be24c09824abc734027b29299a4b0452749ed.
- Thin projection: e00bb9adf1ded2e6bcbd2dfda0b8c8f7f72459ed.

State update protocol: [[00_Project/STATE_UPDATE_PROTOCOL]].

## 2. Current State

> Source: [[00_Project/CURRENT_STATE]]

---
schema_version: 1
as_of: 2026-08-10T16:01:00+08:00
project_stage: PRE_R9_DATA_CLOSURE
primary_strategy: SECOND_LAUNCH
production: false
forward: false
tradeplan: false
primary_oos: false
oos_rows: 0
---
# Current State

## PROJECT

- Project stage: PRE_R9_DATA_CLOSURE.
- Primary strategy: SECOND_LAUNCH.
- This is the overwrite-style current truth. Historical project states are in
  [[06_Conversations/StateSnapshots]].
- The current Project OS entry is [[00_Project/AGENT_HANDOFF]].

## STRATEGY

- Product sequence: T0 → PULLBACK → B1 → B2_READY → B2_CONFIRMED →
  SECOND_LAUNCH.
- Frozen strategy truth remains [[01_Strategy/STRATEGY_MASTER]] and
  [[01_Strategy/RULE_CATALOG]].
- No frozen rule, threshold, setup_stage, Entry Room or score change is implied
  by this state document.

## DATA

- Data architecture: ASL → Adapter → Canonical → Snapshot → Universe → State →
  Strategy/R9.
- ASL_PROJECT_SHA: 0f16f3991a4c8793f96a585ecc938923edf978ac.
- Historical ST positive evidence: READY.
- Historical ST negative evidence: READY.
- Current bounded historical window: 2026-03-30..2026-08-07.
- SYMBOL_N: 3193.
- POSITIVE_BAR_SYMBOL_DAY_N: 286404.
- DERIVED_SUSPENSION_GAP_N: 474.
- ASL_BOUNDED_HISTORICAL_ST_BACKFILL_V01 is RUNNING / RESULT_PENDING. No final
  PASS is asserted here.

## SNAPSHOT

- No post-backfill snapshot is asserted as current.
- An 08/07 state rebuild must be verified against the new ASL facts before it
  can be treated as current downstream evidence.

## STATE

- 08/07 state has not yet been rebuilt and verified on the new ASL facts.
- ACTIVE_SETUP has not yet been formally produced.
- Missing state output must not be interpreted as zero setup or normal market
  state.

## R9

- Protocol: r9-protocol-freeze-v04.
- Freeze commit: 4d9e8fd7cdf0d3e4c631f8a970451c95f8c56aed.
- R7 coefficient SHA:
  39de709f424194be1a28d7e8e21be24c09824abc734027b29299a4b0452749ed.
- Thin projection: e00bb9adf1ded2e6bcbd2dfda0b8c8f7f72459ed.
- PRIMARY_OOS=false and OOS_ROWS=0.
- R9 is not authorized to begin through this state update.

## VALIDATION

- V Flash consumer review SHA: c5bd5b58f67356cd9bbd346e470c7ae325ffccb6.
- V Flash PR #39: Draft / not merged.
- CODE_REVIEW: PASS.
- REMOTE_CI: NOT_VERIFIED.
- B6 volume_D / volume_T0 <= 0.85 is a research observation, not a production
  rule.
- M1 is the primary M1 vs M0 comparison; M1 = M0 + median_range_ratio and
  M2 = M1 + quiet_days_n are research observations.
- breakout_hold_ratio is the strongest current R8 intraday feature observation;
  it is not promoted to a production rule.

## CURRENT_EXECUTION

- Bounded task: ASL_BOUNDED_HISTORICAL_ST_BACKFILL_V01.
- Status: RUNNING / RESULT_PENDING.
- Scope is limited to the stated bounded historical ST backfill and its
  post-write audit. It does not authorize state generation, R9, Forward,
  Production or TradePlan.

## BLOCKERS

- P0-1: bounded historical ST backfill + post-write audit not closed.
- P0-2: 08/07 state not rebuilt and verified on new ASL facts.
- P0-3: ACTIVE_SETUP not formally produced.
- P0-4: live 5m immutable 10:30 checkpoint not closed-loop.
- P0-5: TTL suspension-age semantic conflict not finally reconciled.
- P0-6: R9 runtime provenance / old ASL_CODE_SHA pin must close before primary.
- Full list and priority boundary: [[00_Project/BLOCKERS]].

## DECISIONS

- No decision in this file promotes research observations or authorizes
  production, Forward, TradePlan, state generation or R9.
- TTL suspension-age remains unresolved; no implementation choice is made.
- NEXT_GATE is a review boundary, not an automatic execution instruction.

## NEXT_GATE

1. Receive the bounded backfill result and post-write audit.
2. Perform exact-SHA independent review and classify PASS or BLOCKED.
3. If PASS, update current state and blockers, then decide whether a state
   rebuild/verification task is authorized.

Do not proceed merely because a next gate is listed.

## 3. Project Charter

> Source: [[00_Project/PROJECT_CHARTER]]

本 Charter 只保存长期稳定的项目意图与边界。当前执行、证据和 blocker 以
[[00_Project/CURRENT_STATE]] 与 [[00_Project/BLOCKERS]] 为准。

## Mission

项目研究并逐步构建以下第二波启动结构的、可审计的决策支持能力：

低位/中低位强势涨停
→ 第一次资金表态
→ 缩量回调洗筹
→ 关键支撑
→ B1
→ B2_READY
→ B2_CONFIRMED
→ SECOND_LAUNCH

目标是把该过程变成：

- data reliable
- rules explicit
- statistically testable
- prospectively validated
- decision-support capable

策略语义和阈值的冻结真源始终是 [[01_Strategy/STRATEGY_MASTER]] 与
[[01_Strategy/RULE_CATALOG]]。

## Non-goals

V01 不是：

- generic quant platform
- high-frequency system
- auto parameter mining
- multi-strategy framework
- automatic broker execution V1

本项目不以扩大技术栈或制造候选数量为目标；任何策略或执行能力都必须先经过相应
的数据、PIT、lineage 与验证门。

## Highest Priority

工作优先级固定为：

数据正确性
>
策略语义
>
PIT / lineage
>
Candidate generation
>
Intraday B2
>
Prospective OOS
>
Forward
>
Production

后续层不能绕过前序层的未关闭质量门。该顺序表达风险控制，不是自动执行授权。

## 4. 当前冻结策略摘要

> Source: [[01_Strategy/STRATEGY_MASTER]]

> 冻结版本：`phase-2d0`
> 代码仓库：`a-share-limit-pullback`
> 职责：当前冻结策略的人类可读唯一真源。

本文件只记录已冻结规则。博客观察、案例推论和待验证指标见
[[04_Research/Candidate-Rules]]，不得直接合并进本文件。

## 1. 策略目标

收盘后扫描沪深主板股票的涨停后回调结构，识别可复盘的B1/B2 setup。
系统只做盘后研究，不做盘中监控、券商连接、自动下单或收益回测。

## 2. 股票范围

- 沪深主板；
- 上市交易日不少于120日；
- 排除历史当日ST；
- 要求当日正常交易且原始OHLCV、preclose有效。

## 3. 双价格体系

- raw price：涨停价、支撑、压力、B2触发、失效价、成交与K线展示；
- point-in-time continuous price：均线、均线粘合、120日位置；
- continuous close按当时可知的`close/preclose`链式构造；
- 严格历史评价禁止使用今天重算的历史前复权序列。

决策来源：[[03_Decisions/ADR-001-dual-price-system]]。

## 0. 数据仓库与对账边界

- 正式回测/扫描快照只消费canonical数据；canonical行必须可追溯到单个
  `selected_provider`的完整原始行，禁止跨Provider字段拼接；
- Tushare与AKShare一致才`CONFIRMED`；BaoStock明确延迟但双源一致时不降级并
  审计`BAOSTOCK_LAGGING`；OHLC超容差冲突进入隔离，不发布canonical；
- Provider延迟不等于数据冲突；权限不足不得作为空数据处理；无静默回退；
- 数据抓取与对账只改变数据层，不改变本章第3节起的策略结构与阈值语义。

决策来源：[[03_Decisions/ADR-006-multi-source-warehouse-reconciliation]]。

## 4. 涨停锚点

锚点要求涨停收盘、成交有效，并识别一字板、T字板、首板、近期涨停次数与
连续性。涨停池完整时使用FULL profile；历史涨停池缺失时仅从价格推断并使用
PRICE_ONLY，不伪造封板时间、炸板次数或连板数。

锚点创建稳定`setup_id`并冻结`AnchorSnapshot`。

## 5. 结构生命周期

```text
NORMAL
  └─ LIMIT_ANCHOR
       └─ WATCH_PULLBACK
            └─ B1_READY
                 └─ B2_READY
                      └─ B2_CONFIRMED

任何有效setup ──严重结构失效──> INVALID
新有效锚点 ──> 新setup_id，旧setup SUPERSEDED
离开锚点窗口 ──> EXPIRED
```

同一天恰好有一个`setup_stage`，可以同时有多个`event_flags`。
详细规则见 [[01_Strategy/STATE_MACHINE]]。

## 6. B1

B1表达涨停后的回调企稳观察点，评价锚点后的交易日窗口、价格相对锚点、
支撑触及与守住、成交量收缩、无放量长阴和止跌K线。可用条件命中比例达到
配置阈值，并存在可冻结的支撑与初始失效价时进入`B1_READY`。

target S1、risk/reward、Entry Room、压力候选数量和压力质量不得参与B1结构门槛。
没有可靠target时仍可形成OPEN_SPACE的`B1_READY`。

首次B1冻结Support、Invalid、immediate resistance与target S1快照，但新快照
在冻结日不参与事件或失效判断。

## 7. B2

由同setup上一交易日B1推进到`B2_READY`并冻结触发价。触发价冻结当日不能确认。
后续`B2_CONFIRMED`同时要求：

- 当日最高价达到已生效触发价；
- 收盘不低于触发价；
- 其余可用B2量价条件命中比例达到阈值。

B2量价确认不读取S1空间；S1和Entry Room只影响入场价值与事件解释。

确认日最高价不能反向生成更高触发价。

## 8. 支撑、压力、S1与S2

支撑来自锚点价、平台、均线等raw-equivalent候选，经确定性聚类选择；支撑中心
默认不高于冻结日收盘，仅允许YAML中的极小上方容差。

压力候选来自涨停前左侧高点、涨停后首次上冲高点、最近20/60日高点和高点密集簇。
与锚点或Support簇重叠、或不在参考价上方的簇不能成为S1。

- `immediate_resistance`：最近有效压力，可对应预期B2突破平台；
- `target_s1`：位于预期B2触发价上方的下一有效压力；
- `NEAR_S1`与`S1_BREAKOUT`互斥；
- `S2_EXHAUSTED`要求触及S1，并满足回落、上影、放量、未站稳等多数条件。

## 9. 快照冻结与生效

Support、Invalid、S1、B2 Trigger都保存`frozen_as_of`与`eligible_from`，并满足：

```text
eligible_from > frozen_as_of
```

交易日T只能使用从T-1信号沿用且`eligible_from <= T`的快照。当日计算的新快照
可以输出给下一日，但不能反向影响当日事件、失效或确认。

决策来源：[[03_Decisions/ADR-002-snapshot-timing]]。

## 10. INVALID

结构失效包括：触及冻结失效价、有效跌破支撑、同时跌破锚点与raw-equivalent
MA10、放量跌破B1参考低点、连续放量阴线、已生效支撑破位后未及时恢复。

INVALID是同setup终态，保留明确失效原因；清除普通支撑与S1邻近事件，只允许保留
当日真实成立的`S2_EXHAUSTED`。失效价可以收紧，不能低于initial invalid price。

## 11. Entry Room与入场资格

仅在B1_READY、B2_READY、B2_CONFIRMED派生入场参考价：

- B1：当前收盘；
- B2_READY：当前收盘和冻结触发价的较高者；
- B2_CONFIRMED：当前收盘。

target S1下沿相对参考价的空间分为`NONE`、`THIN`、`SUFFICIENT`；
无可靠target时为`OPEN_SPACE`，S1和risk/reward为null，进入人工复核。

`is_entry_candidate`还要求数据不是UNUSABLE，且没有S1_BREAKOUT或
S2_EXHAUSTED。NONE淘汰新建仓；THIN和NEAR_S1只提示风险。

上述压力事件和入场空间不得把已成立的B1/B2改写为WATCH。INVALID仍可终止结构，
因为它表达结构失效而不是入场价值。

决策来源：[[03_Decisions/ADR-003-entry-room]]。

## 12. 评分与质量

FULL与PRICE_ONLY均保存`available_score`、`available_max_score`与
`normalized_score`。缺失规则从分子和分母同时移除，不计零分、不形成负面理由，
并记录quality flag。PRICE_ONLY本身不是负面条件。

`setup_quality_score`只评价锚点、回调、支撑、量价、K线、均线、形态和B1/B2
结构质量，不读取S1、risk/reward或Entry Room。`entry_quality_score`从结构质量
派生，只评价新建仓价值；NONE、S1_BREAKOUT、S2_EXHAUSTED或UNUSABLE为0，
THIN与可用risk/reward只做入场折减。OPEN_SPACE不因缺失target被记零分。

决策来源：[[03_Decisions/ADR-004-setup-entry-decoupling]]。

## 13. setup终止

- `ACTIVE`
- `INVALIDATED`
- `SUPERSEDED_BY_NEW_ANCHOR`
- `EXPIRED`

每个setup独立保存首次B1/B2/S1事件、失效日、闭合日和最终阶段，不跨setup混合。

## 14. 已冻结与尚未冻结

上述第2至13节为`phase-2b3`冻结语义。Phase 2B.3在Phase 2B.2基础上正式冻结
D-024结构生命周期与入场价值解耦。

## 15. Phase 2C.1单股票数据边界

`phase-2c1`冻结以下实现与数据边界，不改变第2至13节的策略语义或YAML阈值：

- `inspect`是`STATELESS_INSPECT`，不传入或伪造`previous_signal`；
- `replay`是`POINT_IN_TIME_REPLAY`，逐交易日传递上一日信号并保持无未来数据；
- 允许单只、明确请求的沪深主板六位代码：深市`000/001/002/003`，沪市
  `600/601/603/605`；创业板、科创板、北交所、B股和未知前缀在Provider调用前拒绝；
- Provider必须将来源、版本、获取时间、缺失字段和质量显式传播；完全相同的日线重复
  可确定性去重并降级质量，冲突重复必须报错；
- 代码格式合法不表示当日行情必然可用。请求日晚于实际最后日线时不得伪造数据，
  replay必须标记`STALE_DATA`。

本阶段只解除单股票白名单，不包含全市场扫描、数据库、Parquet、缓存、报告、回测、
自动交易或盘中逻辑。决策来源：[[03_Decisions/ADR-005-arbitrary-main-board-provider-boundary]]。

## 16. Phase 2C.2B数据验收边界

`phase-2c2b`冻结的是现有多源仓库和全市场日线验收结果，不改变第2至13节的策略
语义或`strategy.yaml`阈值：

- formal、CONFIRMED-only screen只消费固定canonical快照
  `snap-2026-07-31-b5f84004de8a`，覆盖3191只主板股票；
- `data-validate`必须报告`valid=true`且无问题，canonical行、manifest和哈希可追溯；
- 20只重建point-in-time replay逐字段与screen结果一致；
- Tushare adjusted `pre_close`不再被错误地强制等于上一交易日raw close，AKShare与
  BaoStock仍保留原有连续性校验；
- 本阶段不冻结辅助数据、报告、回测、自动交易或新的策略条件。

以下内容尚未冻结：

- MA30高悬、MA30下行压制；
- 大阴线损伤与下一日快速修复；
- 多次长上影与压力拒绝簇；
- setup时间成本；
- 分钟级尾盘慢拉、快速洗盘与开盘修复；
- 成功案例特征层。

它们只能在 [[04_Research/Candidate-Rules]] 中研究。

## 5. 状态机

> Source: [[01_Strategy/STATE_MACHINE]]

## setup_stage

| 状态 | 确定性含义 | 主要进入条件 | 主要退出条件 |
|---|---|---|---|
| NORMAL | 当前无有效锚点 | 无有效涨停锚点 | 新有效锚点 |
| LIMIT_ANCHOR | 当日为锚点日 | 有效涨停锚点 | 后续交易日 |
| WATCH_PULLBACK | 锚点后观察 | B1结构未达阈值 | B1就绪、失效、新锚点或过期 |
| B1_READY | 回调企稳结构成立 | B1可用条件达阈值且可冻结支撑/失效 | B2就绪、失效、新锚点 |
| B2_READY | 触发价已冻结待确认 | 上一日B1或已有触发价 | B2确认、失效、新锚点 |
| B2_CONFIRMED | 已站稳冻结触发价 | 高点触发、收盘站稳、量价多数 | 失效、新锚点或过期 |
| INVALID | 当前setup结构失效 | 任一严重失效条件 | 仅由新setup替代 |

## event_flags

- `SUPPORT_WARNING`：已生效支撑受到威胁；
- `NEAR_S1`：尚未突破时接近S1；
- `S1_BREAKOUT`：收盘突破S1上沿；
- `S2_EXHAUSTED`：触及S1并出现衰竭组合。

`NEAR_S1`与`S1_BREAKOUT`互斥。INVALID清除普通支撑与S1事件。

## 时序

```text
T日计算候选
  └─ T日冻结快照（eligible_from > T）
       └─ T+1或之后由previous_signal沿用
            └─ eligible_from <= 当前交易日时才参与判断
```

## 终止

INVALIDATED优先记录首次失效日；新锚点将仍活动的旧setup标记为
SUPERSEDED_BY_NEW_ANCHOR；没有新锚点且离开有效窗口时标记EXPIRED。

## 6. 最近已采纳决策

> Sources: [[03_Decisions/DECISION_INDEX]]及最近三份ACCEPTED ADR

### ADR-004 Setup生命周期与入场价值解耦

> Source: [[03_Decisions/ADR-004-setup-entry-decoupling]]

D-024正式冻结以下语义：

- `setup_stage`只表达结构生命周期；
- B1结构门槛不读取target S1、risk/reward或Entry Room；
- B2量价确认不读取S1空间；
- `setup_quality_score`只评价结构质量；
- `entry_quality_score`只评价新建仓价值；
- `S1_BREAKOUT`与`S2_EXHAUSTED`影响入场资格，但不修改`setup_stage`；
- INVALID仍是结构终止条件；
- OPEN_SPACE可以保持`B1_READY`或`B2_READY`。

### ADR-005 任意主板单股票真实评价与Provider边界

> Source: [[03_Decisions/ADR-005-arbitrary-main-board-provider-boundary]]

D-025正式冻结以下能力与边界：

- 单只、明确请求的沪深主板六位代码可真实评价；深市仅`000/001/002/003`，沪市仅
  `600/601/603/605`；其他板块和格式在Provider调用前拒绝；
- `inspect`固定为`STATELESS_INSPECT`，`replay`固定为`POINT_IN_TIME_REPLAY`；
- 日线、涨停池和信号输出显式保存Provider、版本、获取时间、质量、缺失字段及实际日期；
- 完全相同的日线重复可确定性去重并降级质量；冲突重复、畸形必填字段和会话错误显式
  失败或标记，不能静默吞掉；
- 请求日晚于实际最后日线时，replay标记`STALE_DATA`；不得伪造行情或以旧记录代替请求日；
- 不实施自动静默Provider回退，也不得拼接来自不同来源的同一根K线。

### ADR-006 多数据源行情仓库与显式对账

> Source: [[03_Decisions/ADR-006-multi-source-warehouse-reconciliation]]

- Tushare Pro为主日线来源；AKShare（sina日线端点）为日线校验源；
  AKShare/东方财富提供涨停池；BaoStock负责历史补录与第三来源校验；
- Parquet保存原始与canonical大数据主体，DuckDB保存运行/能力/文件/快照/对账
  元数据；原始行含`provider/provider_version/fetched_at/ingest_run_id/
  source_unit/normalized_unit/row_hash`；
- 对账状态：`PROVISIONAL/CONFIRMED/INCOMPLETE/CONFLICTED/QUARANTINED`；
  Tushare与AKShare一致才`CONFIRMED`；BaoStock滞后但双源一致时仍`CONFIRMED`
  并审计`BAOSTOCK_LAGGING`；OHLC超容差冲突进入隔离，不发布canonical；
- 禁止静默Provider回退、禁止字段级拼接；canonical整行来自
  `selected_provider`，通过`source_row_hash`与manifest哈希回溯；
- snapshot不可变，`as_of`读取只使用不晚于该边界的早期发布；
  bootstrap/update幂等，写锁串行化并发运行；
- Token只从环境变量读取，缺失返回`TUSHARE_TOKEN_NOT_CONFIGURED`，任何日志、
  异常、元数据与报告均脱敏。

## 7. 当前PROPOSED规则

> Sources: [[01_Strategy/RULE_CATALOG]]、[[04_Research/Candidate-Rules]]

- `FAST_WASHOUT_RECOVERY`（分钟研究）：日内快速下探后收回关键位；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `LARGE_BEARISH_DAMAGE`（风险候选）：大阴线破坏短线形态但未必跌破支撑；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `LATE_DAY_RAMP`（分钟研究）：尾盘缓慢拉升的日内路径；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `MA30_DOWNTREND_OVERHEAD`（风险候选）：下行MA30在现价上方形成动态压力；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `MA30_OVERHEAD`（风险候选）：MA30明显位于现价上方，可能限制修复空间；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `MA_RETEST_OVERDUE`（时间候选）：长时间不回踩均线可能提高追入风险；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `OPENING_FAST_REPAIR`（分钟研究）：开盘后快速收复前一日损伤；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `REPAIR_FAILED`（失效候选）：应修复而未修复时降低预期或失效；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `REPAIR_REQUIRED`（风险候选）：结构受损后下一交易日需快速修复；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `REPEATED_UPPER_SHADOW`（压力候选）：多个交易日长上影可能表示压力反复拒绝；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `RESISTANCE_REJECTION_CLUSTER`（压力候选）：相近压力区域多次冲高回落；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `TIME_COST_AGING`（时间候选）：多日无阶段推进产生时间成本；代码实现=否；来源=[[04_Research/Blogger-Observations]]
- `TIME_COST_STALE`（时间候选）：超过候选窗口后不再适合短线新建仓；代码实现=否；来源=[[04_Research/Blogger-Observations]]

## 8. 成功案例摘要

> Source: [[02_Cases/CASE_INDEX]]及Success案例

### 002640 跨境通 (2026-07-27)

> Source: [[02_Cases/Success/002640-2026-07-27]]

- 状态：observed；置信度：medium
- 标签：LOW_BASE_BREAKOUT, MA_CLUSTER_RECLAIM, CLOSE_NEAR_HIGH, MA120_OVERHEAD
- 可提炼特征：LOW_BASE_BREAKOUT、MA_CLUSTER_RECLAIM、CLOSE_NEAR_HIGH、MA120_OVERHEAD。
- 不能得出的结论：不能证明这些特征具有统计优势，不能确认B1/B2标签，不能据此修改Entry Room阈值。
- 与当前策略关系：对应 [[04_Research/Success-Case-Features]] 的均线簇、收盘位置与MA120距离研究；
不改变 [[01_Strategy/STRATEGY_MASTER]]。

### 002891 中宠股份 (2026-07-28)

> Source: [[02_Cases/Success/002891-2026-07-28]]

- 状态：observed；置信度：medium
- 标签：MA20_MA30_PULLBACK, FAST_REPAIR, CLOSE_NEAR_HIGH, STRONG_RECLAIM
- 可提炼特征：MA20_MA30_PULLBACK、FAST_REPAIR、CLOSE_NEAR_HIGH、STRONG_RECLAIM。
- 不能得出的结论：不能从单一样本采纳REPAIR_CONFIRMED，不能定义修复时限、量能或幅度阈值。
- 与当前策略关系：可作为未来REPAIR_REQUIRED/REPAIR_FAILED对照研究的正向样本，当前规则仍保持
PROPOSED，见 [[04_Research/Candidate-Rules]]。

### 600199 金种子酒 (2026-07-28)

> Source: [[02_Cases/Success/600199-2026-07-28]]

- 状态：observed；置信度：medium
- 标签：MA20_MA30_PULLBACK, LIMIT_UP_RELAUNCH, RESISTANCE_BREAKOUT, CLOSE_NEAR_HIGH
- 可提炼特征：MA20_MA30_PULLBACK、LIMIT_UP_RELAUNCH、RESISTANCE_BREAKOUT、CLOSE_NEAR_HIGH。
- 不能得出的结论：不能证明MA20/30回踩必然有效，不能确认压力突破的程序簇，不能推导量价阈值。
- 与当前策略关系：可补充Entry Quality和成功案例特征研究，但当前Support选择、B1/B2与Entry Room
继续以冻结代码为准。

## 9. 失败案例摘要

> Source: [[02_Cases/CASE_INDEX]]及Failure案例

暂无案例。

## 10. 当前待办

> Source: [[04_Research/Research-Backlog]]

## P0：数据与对照组

- 为三个成功案例补齐完整日线、成交量、涨停池和后续5/10/20日表现；
- 每个成功标签至少收集同定义失败样本；
- 建立修复成功、修复失败与自然波动三组对照；
- 核对截图日期、股票名称与人工结论。

## P1：可日线验证

- 冻结MA30_OVERHEAD距离和斜率候选定义；
- 定义LARGE_BEARISH_DAMAGE而不与INVALID重复；
- 定义REPEATED_UPPER_SHADOW的交易日窗口；
- 比较TIME_COST_AGING对Entry Quality与setup终止的不同处理；
- 冻结候选特征的分母、缺失值和point-in-time口径。

## P2：需要新数据边界

- 分钟数据研究LATE_DAY_RAMP；
- 分钟数据研究FAST_WASHOUT_RECOVERY；
- 分钟数据研究OPENING_FAST_REPAIR。

这些项目只列为研究待办，不授权修改当前Provider或策略引擎。

## P0/P1：第二波启动因子研究（DRAFT）

- 初版研究方案：[[04_Research/Second-Launch-Factor-Research-V01]]
- 下一阶段：`R0 — CONTRACT & DATA READINESS`；尚未授权开发执行。

## ADR触发条件

有明确规则语义、足够成败对照、历史信号影响分析和预期测试后，才从
[[03_Decisions/ADR_TEMPLATE]]创建正式决策。

## 11. 已人工审核会话

> Source: [[06_Conversations/CONVERSATION_INDEX]]及human_reviewed/accepted Digests；不读取Raw。

暂无已人工审核会话。

## 12. 最近已审核案例

> Source: [[02_Cases/CASE_INDEX]]。

- [[02_Cases/Success/002640-2026-07-27]]：002640 跨境通，case_status=observed，outcome=success
- [[02_Cases/Success/002891-2026-07-28]]：002891 中宠股份，case_status=observed，outcome=success
- [[02_Cases/Success/600199-2026-07-28]]：600199 金种子酒，case_status=observed，outcome=success

## 13. 最近可审计推理摘要

> Source: [[06_Conversations/REASONING_INDEX]]；仅包含human_reviewed/accepted。

暂无已审核推理摘要。

## 14. 待审核Agent Intake

> 下列内容尚未进入正式策略摘要，仅供人工审核。

- [[08_AgentExchange/Incoming/case-603918-2026-07-31-001|case-603918-2026-07-31-001]]：603918 金桥信息，status=captured；数据限制=- 盘中截图不能视为最终日K，收盘价、最终成交量和最终上影线未知。
- 尚未使用项目真实 Provider 对 603918 做 point-in-time replay。
- 尚未确认锚点日、正式 setup_id、SupportSnapshot、InvalidPriceSnapshot、S1 和 Entry Room。
- 无法从截图确认机构或“主力”真实持仓变化。
- 当前没有足够失败对照，不能将“第四日低吸”直接冻结成策略规则。
- App 显示为前复权均线，可能与系统 point-in-time continuous → raw-equivalent MA 存在差异。；当前结论=- 该案例适合作为“突破后第四日 MA5 回踩快速修复”的成功候选样本。
- 可验证的核心不是“主力没跑”，而是“结构未明显破坏、关键支撑出现承接并快速收复”。
- 低吸观察点出现在 10.60—10.80 附近；11.69 已不属于低吸。
- 案例暂时保持 `captured`，需要收盘数据、后续走势和真实 replay 后才能升级为 `observed` 或 `validated`。

## 15. 获批代码变更请求

> Source: [[05_Codex/IMPLEMENTATION_QUEUE]]；仅包含approved_for_implementation。

暂无获批代码变更请求。

## 16. 代码仓库基线与drift

> Source: `01_Strategy/BASELINE_MANIFEST.yaml`及本地Git只读状态。

- 代码仓库：`Luke808real/a-share-limit-pullback`
- 冻结策略版本：`phase-2d0`
- 冻结tag：`phase-2d0`
- 策略内容commit：`e865de484e40e45b1d2044ee1c58247c76f3a758`
- main集成commit：`2cabcf6ca0885993185453c3384fcf346fa4ddff`
- 策略tree：`cb786d72f513baf67d936b61176c4c89a17acfb9`
- 基线关系：`MERGE_EQUIVALENT_TREE`
- 当前分支：`stabilize/pr-e-atomic-state-generation`
- 当前commit：`0f08348fd1fa7e04bdf468acc5516d6001e169b9`
- 观测main：`1cb5fb7a1792edccc18c70207340980377cbd4eb`
- 观测tag：`e865de484e40e45b1d2044ee1c58247c76f3a758`
- drift状态：`DIRTY_WORKTREE`
