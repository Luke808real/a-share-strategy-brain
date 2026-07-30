# LLM Context Pack

> 用途：ChatGPT Project/Codex上下文。由本地确定性工具生成；不包含图片二进制或完整历史聊天原文。

## 1. 当前阶段

> Source: [[05_Codex/CURRENT_PHASE]]

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

## 2. 当前冻结策略摘要

> Source: [[01_Strategy/STRATEGY_MASTER]]

> 冻结版本：`phase-2b2`
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

首次B1冻结Support、Invalid、immediate resistance与target S1快照，但新快照
在冻结日不参与事件或失效判断。

## 7. B2

由同setup上一交易日B1推进到`B2_READY`并冻结触发价。触发价冻结当日不能确认。
后续`B2_CONFIRMED`同时要求：

- 当日最高价达到已生效触发价；
- 收盘不低于触发价；
- 其余可用B2量价条件命中比例达到阈值。

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

决策来源：[[03_Decisions/ADR-003-entry-room]]。

## 12. 评分与质量

FULL与PRICE_ONLY均保存`available_score`、`available_max_score`与
`normalized_score`。缺失规则从分子和分母同时移除，不计零分、不形成负面理由，
并记录quality flag。PRICE_ONLY本身不是负面条件。

## 13. setup终止

- `ACTIVE`
- `INVALIDATED`
- `SUPERSEDED_BY_NEW_ANCHOR`
- `EXPIRED`

每个setup独立保存首次B1/B2/S1事件、失效日、闭合日和最终阶段，不跨setup混合。

## 14. 已冻结与尚未冻结

上述第2至13节为`phase-2b2`冻结语义。以下内容尚未冻结：

- MA30高悬、MA30下行压制；
- 大阴线损伤与下一日快速修复；
- 多次长上影与压力拒绝簇；
- setup时间成本；
- 分钟级尾盘慢拉、快速洗盘与开盘修复；
- 成功案例特征层。

它们只能在 [[04_Research/Candidate-Rules]] 中研究。

## 3. 状态机

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

## 4. 最近已采纳决策

> Sources: [[03_Decisions/DECISION_INDEX]]及最近三份ACCEPTED ADR

### ADR-001 双价格体系

> Source: [[03_Decisions/ADR-001-dual-price-system]]

raw price用于交易结构；point-in-time continuous close按当时可知的
`close/preclose`链式构造并用于均线、粘合和120日位置。

### ADR-002 风险快照先冻结后生效

> Source: [[03_Decisions/ADR-002-snapshot-timing]]

Support、Invalid、S1、B2 Trigger统一保存`frozen_as_of`与`eligible_from`，
且后者严格晚于前者。T日只使用previous signal中已生效的快照。

### ADR-003 压力分层与Entry Room

> Source: [[03_Decisions/ADR-003-entry-room]]

区分`immediate_resistance`和`target_s1`。Entry Room使用阶段对应参考价到
target S1下沿的Decimal比例，分为NONE、THIN、SUFFICIENT、OPEN_SPACE。

## 5. 当前PROPOSED规则

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

## 6. 成功案例摘要

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

## 7. 失败案例摘要

> Source: [[02_Cases/CASE_INDEX]]及Failure案例

暂无案例。

## 8. 当前待办

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

## ADR触发条件

有明确规则语义、足够成败对照、历史信号影响分析和预期测试后，才从
[[03_Decisions/ADR_TEMPLATE]]创建正式决策。

## 9. 最新Codex提示

> Source: [[05_Codex/NEXT_PROMPT]]

当前没有获批的策略实现任务。

下一次实现前，必须先：

1. 从Candidate Rules选择一个有足够对照样本的规则；
2. 创建正式ADR；
3. 明确它影响setup_stage、is_entry_candidate、Entry Quality还是仅解释；
4. 列出历史信号、配置、Provider与黄金样本影响；
5. 获得用户确认后再形成范围明确的Codex实现提示。

禁止将三个成功截图或单一博客观点直接转化为阈值。

## 10. 已人工审核会话

> Source: [[06_Conversations/CONVERSATION_INDEX]]及human_reviewed/accepted Digests；不读取Raw。

暂无已人工审核会话。

## 11. 最近已审核案例

> Source: [[02_Cases/CASE_INDEX]]。

- [[02_Cases/Success/002640-2026-07-27]]：002640 跨境通，case_status=observed，outcome=success
- [[02_Cases/Success/002891-2026-07-28]]：002891 中宠股份，case_status=observed，outcome=success
- [[02_Cases/Success/600199-2026-07-28]]：600199 金种子酒，case_status=observed，outcome=success

## 12. 最近可审计推理摘要

> Source: [[06_Conversations/REASONING_INDEX]]；仅包含human_reviewed/accepted。

暂无已审核推理摘要。

## 13. 待审核Agent Intake

> 下列内容尚未进入正式策略摘要，仅供人工审核。

暂无待审核Agent Intake。

## 14. 获批代码变更请求

> Source: [[05_Codex/IMPLEMENTATION_QUEUE]]；仅包含approved_for_implementation。

暂无获批代码变更请求。

## 15. 代码仓库基线与drift

> Source: `01_Strategy/BASELINE_MANIFEST.yaml`及本地Git只读状态。

- 代码仓库：`Luke808real/a-share-limit-pullback`
- 冻结策略版本：`phase-2b2`
- 冻结tag：`phase-2b2`
- 冻结commit：`85e1f916cbb33cc42b65ee16d74ca0301cba7b44`
- 当前分支：`milestone/phase-2b2-freeze`
- 当前commit：`85e1f916cbb33cc42b65ee16d74ca0301cba7b44`
- drift状态：`DIRTY_WORKTREE`
