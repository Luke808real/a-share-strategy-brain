---
type: strategy_decision
adr_id: ADR-005
decision_id: D-025
title: 任意主板单股票真实评价与Provider边界
status: ACCEPTED
decision_date: 2026-07-31
strategy_version: phase-2c1
---

# ADR-005 任意主板单股票真实评价与Provider边界

## 原规则

Phase 2B.3仅对三只验证股票开放真实`inspect`与`replay`。BaoStock日线、AKShare
涨停池和策略引擎已有明确边界，但代码验证、重复日线、畸形字段、会话异常和评价模式
尚未在任意合法主板单股范围内冻结。

## 新观察

真实链路验收表明，代码格式合法、历史数据存在和请求日最终日线可用是不同事实。单一
Provider可能延迟，不能因此伪造当日行情、混用来源或让未来数据回写历史。无状态inspect
与逐日回放也不能因结果不同而被误判为策略矛盾。

## 决策

D-025正式冻结以下能力与边界：

- 单只、明确请求的沪深主板六位代码可真实评价；深市仅`000/001/002/003`，沪市仅
  `600/601/603/605`；其他板块和格式在Provider调用前拒绝；
- `inspect`固定为`STATELESS_INSPECT`，`replay`固定为`POINT_IN_TIME_REPLAY`；
- 日线、涨停池和信号输出显式保存Provider、版本、获取时间、质量、缺失字段及实际日期；
- 完全相同的日线重复可确定性去重并降级质量；冲突重复、畸形必填字段和会话错误显式
  失败或标记，不能静默吞掉；
- 请求日晚于实际最后日线时，replay标记`STALE_DATA`；不得伪造行情或以旧记录代替请求日；
- 不实施自动静默Provider回退，也不得拼接来自不同来源的同一根K线。

## 被否决方案

- 将所有六位数字直接交给Provider；
- 让inspect伪造`previous_signal`以匹配replay；
- 在策略层处理原始Provider重复或畸形字段；
- 因BaoStock延迟而补写、猜测或重用次日行情；
- 将Tushare、全市场落库、自动回退或数据拼接提前混入本阶段。

## 对历史信号的影响

不改变B1、B2、S1、INVALID、Entry Room或评分阈值。允许新增评价模式和更准确的
质量/缺失字段输出；完全相同重复记录被去重，冲突记录停止进入策略。原三只股票的
冻结结构投影保持不变。

## 代码影响

策略内容提交为`0b01abb057fea56ae8d06545585de7ac7d877522`，main集成提交为
`8052ca7fe832bc4134390ba14c8911022b143c7e`，两者tree等价。实现包含共享主板代码
解析、Provider边界加固及单股CLI/inspect/replay支持。

## 配置影响

未调整`strategy.yaml`中的B1、B2、S1、INVALID或Entry Room阈值。

## 测试影响

覆盖合法与非法主板前缀、前导零、两种评价模式、重复和冲突日线、畸形字段、Provider
会话异常、短历史资格、默认socket禁网，以及原三只和新增四只真实单股integration验收。

## 是否需要重新生成黄金样本

不需要策略语义黄金样本迁移；新增Provider质量和代码范围覆盖。603918显示Provider延迟
时`STALE_DATA`正确传播，作为数据完整性边界案例，仍保持`captured`。

## 证据与不确定性

Phase 2C.1离线与真实integration测试均通过。603918在2026-07-31的盘中案例尚未得到
BaoStock最终日线，证明多源数据完整性门禁是后续独立需求，不构成Phase 2C.1实现缺陷。
本决策不冻结Tushare接入、全市场扫描、数据库、Parquet、报告、回测或自动交易。
