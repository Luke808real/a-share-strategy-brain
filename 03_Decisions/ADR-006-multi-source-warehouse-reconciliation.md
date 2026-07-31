---
type: strategy_decision
adr_id: ADR-006
decision_id: D-026
title: 多数据源行情仓库与显式对账
status: ACCEPTED
decision_date: 2026-07-31
strategy_version: phase-2c2a
---

# ADR-006 多数据源行情仓库与显式对账

## 背景

单一日线源（BaoStock）会出现延迟，且无法判断数据是否完整；需要本地可追溯的
多源行情仓库，使日线、日历、复权、基本面与涨停池数据具备确定性、幂等更新和
point-in-time读取能力。

## 决策

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

## 后果

- 数据新鲜度不再由单一Provider门禁；Provider延迟与数据冲突被显式区分；
- 正式回测/扫描只能消费`CONFIRMED` canonical行（`PROVISIONAL`仅带标记保留）；
- 数据层改动不改变冻结策略结构与`strategy.yaml`阈值。
