# SECOND_LAUNCH_FACTOR_RESEARCH_V01

> 状态：`DRAFT_RESEARCH_ONLY`
> AS_OF：2026-08-08
> 目标策略：涨停回调 / 首板回踩再启动
> 生产影响：`NONE`
> 冻结规则影响：`NONE`
> 数据/代码仓库：`Luke808real/a-share-limit-pullback`
> 知识库仓库：`Luke808real/a-share-strategy-brain`
> 建议落点：`04_Research/Second-Launch-Factor-Research-V01.md`

## 1. 研究对象

当前研究的核心结构不是机械“N字形”，而是一个资金与价格结构过程：

```text
第一次强势资金表态（T0 / ATTACK）
→ 涨停后回调或整理（PULLBACK）
→ 卖压、成交与波动逐步收缩（CONTRACTION）
→ 第一次上涨成果仍被较好保留（HOLD）
→ 再次主动攻击关键位（ACTIVATION）
→ 突破后市场接受新价格（ACCEPTANCE）
→ 第二次趋势扩张（SECOND_LAUNCH）
```

研究目标不是证明“涨停后容易涨”，而是回答：

> 在已经出现有效 T0 并进入回调的股票中，哪些在 B 点之前可获得的因素，能稳定提高后续进入 SECOND_LAUNCH 的条件概率？

所有特征必须 point-in-time；观察日 D 之后的数据只能用于 outcome 标注，不能进入 feature。

## 2. 与当前冻结策略的关系

当前冻结状态机继续保持：

```text
LIMIT_ANCHOR
→ WATCH_PULLBACK
→ B1_READY
→ B2_READY
→ B2_CONFIRMED
```

本文研究不授权修改：

- `STRATEGY_MASTER`；
- B1 / B2 的冻结语义与阈值；
- `strategy.yaml`；
- state / setup_id / snapshot 语义；
- Production / Forward / TradePlan；
- generation promotion。

研究结论必须经历：

```text
OBSERVATION
→ HYPOTHESIS
→ VALIDATED
→ STRATEGY_CANDIDATE
→ ADR
→ 实现与黄金回归
→ 新冻结版本
```

单个成功案例、单个博主、单次回测或单一市场阶段不得直接成为冻结规则。

## 3. 外部研究定位

外部已有 A 股方法包括：

- N字战法；
- 单阳不破；
- 涨停双响炮；
- 龙回头 / 2+N；
- 涨停后回调低吸；
- 涨停后创新高再启动。

国外可用于解释和比较的框架包括 Bull Flag、VCP、Wyckoff Re-Accumulation、Breakout-Retest，但本项目研究主体仍以 A 股涨停制度和 A 股样本为准。

公开社区已有大量“固定回调天数 + 固定回撤 + 缩量 + 再突破”的规则策略，但目前未发现一套公开、成熟、完整覆盖以下内容的 A 股研究：

1. SUCCESS vs FAILED_BREAKOUT / NO_LAUNCH / STRUCTURE_FAIL 的大样本因子归因；
2. Price Hold / Gain Retention；
3. 高换手低价格损伤（Absorption）；
4. 成交量收缩与波动率收缩的组合；
5. Breakout 后 Acceptance；
6. 个股二波与板块二波同步；
7. 严格时间外 / walk-forward 增量验证。

因此外部规则后续只作为 `BENCHMARK`，不能作为本项目默认真值。

## 4. 当前高价值 A 股研究样本

第一批 Golden Success / High-Value Cases：

| code | name | 研究价值 |
|---|---|---|
| 002606 | 大连电瓷 | 浅回调、高位保持、较快二波；提示“成交不一定立刻缩，但价格可能跌不动” |
| 002498 | 汉缆股份 | 高能量版本；连续强攻、剧烈分歧后重新接受并再启动 |
| 600468 | 百利电气 | 普通首板后回调再启动，适合与同板块样本做 matched control |
| 600756 | 浪潮软件 | 较深回撤仍可能成功，适合研究 pullback depth 的非线性边界 |
| 601858 | 中国科传 | 长时间整理后再启动，适合研究 setup TTL / time decay |

这些案例只用于：

- feature discovery；
- feature sanity check；
- 公式与数据语义核对；
- 建立成功/失败的人工解释基线。

不得用 5 只成功股票直接推断统计规律。

### 4.1 优先 matched-control 场景

2026-07-23 前后电网 / 特高压板块提供了一个天然准对照实验：同一天、同板块、相似市场环境中多只股票出现第一次强势资金攻击，但后续二波质量不同。

优先研究：

```text
大连电瓷
汉缆股份
百利电气
三变科技
海兴电力
太阳电缆
顺钠股份
中国西电
双杰电气
...
```

目的：尽量控制 date / sector / market regime 后，再观察个股结构差异。

## 5. Outcome 与样本原则

第一版应优先复用已有 frozen case set，不为获得更好结果重新修改 outcome 定义。

当前历史研究中已有约：

```text
SUCCESS             409
FAILED_BREAKOUT     950
NO_LAUNCH          1730
STRUCTURE_FAIL     5415
UNKNOWN             242
TOTAL              8746
```

正式实现前必须重新确认：

- 这些数字对应的 case-set ID / manifest；
- outcome definition 是否仍为最新有效定义；
- 样本是否 point-in-time；
- inferred anchor / 缺失数据的 quality flag；
- UNKNOWN 是否排除或单独分析。

若无法确认，fail closed，不重新猜测 cohort。

## 6. 第一版核心因子家族

### F1 — ATTACK

研究第一次资金攻击是否真正有信息量：

```text
t0_return
t0_volume_ratio_5d
t0_volume_ratio_20d
t0_turnover
t0_range_pct
t0_close_location
t0_gap
t0_position_20d
t0_position_60d
pre_t0_return_5d
pre_t0_return_20d
t0_breakout_20d
prior_limitup_n
```

核心问题：低位 / 中低位高质量首板是否比高位事件更容易形成第二波。

### F2 — HOLD

研究第一波上涨成果在回调中保留多少：

```text
pullback_depth_close
max_drawdown_from_post_t0_high
impulse_retrace_ratio
t0_gain_retention
low_vs_t0_open
low_vs_t0_mid
low_vs_pre_t0_close
days_above_t0_mid
days_above_pre_t0_close
low_vs_ma5
low_vs_ma10
low_vs_pre_high
```

重点 HYPOTHESIS：`Price Hold / Gain Retention` 可能比“某一天是否缩量”更接近结构强弱本质。

### F3 — CONTRACTION

把“洗盘”从叙事转成可观测变量：

```text
pullback_volume_ratio
min_volume_ratio
volume_slope
median_range_ratio
range_slope
atr_contraction
quiet_days_n
```

同时研究：

- Volume Contraction；
- Volatility Contraction。

重点不是固定某一天 `< T0 volume * 0.5`，而是整个 pullback 窗口的供给与波动变化过程。

### F4 — ABSORPTION

研究“成交很多但价格跌不下去”的结构：

```text
price_damage_per_turnover
max_drawdown_per_cumulative_turnover
negative_return_per_turnover
```

核心 HYPOTHESIS：在相似换手量下，价格损伤越小，可能代表更强的承接 / supply absorption。

该因子依赖可靠 turnover lineage；coverage 不足时必须标记 `BLOCKED_BY_DATA`，不得用 UNKNOWN 补齐。

### F5 — TIME

```text
days_since_t0
days_to_pullback_low
days_from_low_to_activation
pullback_duration
quiet_days_n
```

核心问题：是否存在非线性的最佳时间窗口，以及 setup 是否随时间衰减。

不得先假设 T+3、T+5 或固定 TTL 为真。

### F6 — ACTIVATION

第一版先做日线层：

```text
high_vs_pullback_high
close_vs_pullback_high
breakout_strength
relative_volume
close_location
```

核心问题：第二次攻击什么质量更容易进入真正扩张。

### F7 — ACCEPTANCE（后阶段）

需要分钟 / 5m 数据：

```text
breakout_hold_ratio
vwap_acceptance_ratio
retest_depth
false_break_duration
post_break_30m_return
post_break_60m_return
```

核心定义：

```text
ACTIVATE != ACCEPT
```

触碰或突破关键位只代表重新攻击；突破后能否在关键位、VWAP、前收等价格上方持续交易，才代表市场接受。

### F8 — CONTEXT（独立数据 gate）

候选包括：

```text
sector_limitup_n
sector_up_ratio
sector_median_return
sector_relative_strength
sector_reactivation_n
market_up_down_breadth
market_limitup_downlimit_n
```

重点 HYPOTHESIS：

```text
个股 N / second-launch
×
板块 N / second-launch
```

可能显著强于只有个股单独发动。

历史 sector / concept mapping 必须 point-in-time；若没有可靠 lineage，V01 不实现该 family。

## 7. 当前重点 HYPOTHESES

### H1 — PRICE_HOLD

T0 后价格保持在高位、第一波涨幅被较好保留，可能比单日缩量更重要。

### H2 — SUPPLY_CONTRACTION

成交量趋势下降与价格振幅趋势下降的组合，可能比任一单指标更有区分度。

### H3 — ABSORPTION

高换手 / 高成交但低价格损伤，可能是与纯缩量不同的另一类强势整理。

### H4 — TIME_NONLINEAR_DECAY

二波并非固定 T+N；可能存在“过快未充分整理 → 最佳窗口 → 过久失效”的非线性时间结构。

### H5 — ACCEPTANCE_OVER_BREAKOUT

第二次突破后能否站住关键位，可能比简单 `new_high = true` 更重要。

### H6 — SECTOR_STOCK_SYNCHRONIZATION

个股和板块同步进入第二次扩张，可能显著提高个股二波成功率。

上述全部为 `HYPOTHESIS`，不是冻结规则。

## 8. 外部 Benchmark 计划

在项目自身 V01 因子跑出初版结果后，再实现传统公开规则基线：

```text
N字传统规则
龙回头 / 2+N
单阳不破
固定回调天数
固定回撤幅度
固定缩量比例
涨停后再创新高
热点板块过滤
```

比较：

```text
Benchmark only
vs
Benchmark + Price Hold
vs
Benchmark + Contraction
vs
Benchmark + Absorption
vs
Benchmark + Acceptance
vs
Benchmark + Context
```

关注增量指标：

```text
Delta AUC
Delta LogLoss
Delta Brier
Top-decile lift
SUCCESS rate lift
FAILED_BREAKOUT rate
3D / 5D / 10D MFE
MAE
Days-to-launch
```

若新因子没有稳定增量价值，应删除，而不是因为符合直觉而保留。

## 9. 统计与验证原则

第一版明确：`NO ML`。

先做：

- decile / quantile；
- SUCCESS rate；
- FAILED_BREAKOUT rate；
- Odds Ratio + 95% CI；
- AUC；
- Spearman；
- MFE / MAE；
- days-to-launch；
- year / board / regime stability。

优先观察连续变量是否具有单调关系或明确非线性区间。

之后才允许：

1. Logistic Regression；
2. 去共线 / factor family selection；
3. LightGBM / XGBoost；
4. permutation importance / SHAP；
5. interaction discovery。

机器学习用于发现非线性和交互，不用于替代规则解释。

### 9.1 时间验证

不得 random split。

必须使用按时间切割或 walk-forward：

```text
Discovery
→ Validation
→ Holdout
```

具体年份按 ASL 可证明的历史 coverage 与质量决定。

## 10. 研究路线

```text
R0  RESEARCH CONTRACT & DATA READINESS
    冻结 case set / outcome / PIT / 数据 coverage

R1  GOLDEN CASE STUDY
    5 个高价值成功样本 + matched controls

R2  DAILY FACTOR EXTRACTION
    全 cohort 日线特征

R3  UNIVARIATE ATTRIBUTION
    decile / OR / CI / MFE / MAE

R4  STABILITY
    year / regime / board / T0 type

R5  EXTERNAL BENCHMARK
    N字 / 龙回头 / 单阳不破等传统规则

R6  INCREMENTAL VALUE
    外部基线 vs 基线 + 本项目候选因子

R7  MULTIVARIATE
    Logistic first；ML later

R8  INTRADAY ACCEPTANCE
    5m / VWAP / breakout hold / retest

R9  WALK-FORWARD
    严格时间外验证

R10 STRATEGY CANDIDATE
    只有 VALIDATED 因子允许进入 ADR / 正式策略讨论
```

## 11. 第一开发任务（尚未授权执行）

开发开始时第一步不是写全市场模型，而是：

`SECOND_LAUNCH_FACTOR_RESEARCH_V01 — CONTRACT & DATA READINESS`

只做：

1. 定位并冻结当前有效 case set / manifest；
2. 验证 ASL / canonical query 是否能 PIT 读取样本所需 daily bars；
3. 检查 OHLCV / turnover / minute / sector 四类数据 coverage 与 lineage；
4. 为 factors_v01 输出可实现性矩阵。

目标输出：

| Factor | Data | Coverage | PIT Safe | V01 |
|---|---|---:|---|---|
| gain_retention | daily | TBD | TBD | GO/BLOCK |
| volume_slope | daily | TBD | TBD | GO/BLOCK |
| range_slope | daily | TBD | TBD | GO/BLOCK |
| price_damage_per_turnover | turnover | TBD | TBD | GO/BLOCK |
| sector_sync | sector | TBD | TBD | GO/BLOCK |
| vwap_acceptance | 5m | TBD | TBD | LATER |

禁止：

- 修改策略规则；
- 修改 state / snapshot 语义；
- 训练模型；
- full-market 重复重跑；
- Production / Forward / TradePlan；
- 为补字段绕过数据质量门。

## 12. 当前研究决策

```text
PRODUCTION_CHANGE = false
STRATEGY_FREEZE_CHANGE = false
FORWARD_CHANGE = false
TRADEPLAN_CHANGE = false
RESEARCH_ONLY = true
```

当前下一步：继续在 Thinker 会话中研究策略与案例；待用户明确授权后，再为数据仓 Codex 生成 R0 的最小可验证执行任务。
