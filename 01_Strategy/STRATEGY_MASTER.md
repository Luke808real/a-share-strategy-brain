# 冻结策略总纲

> 冻结版本：`phase-2c2b`
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
