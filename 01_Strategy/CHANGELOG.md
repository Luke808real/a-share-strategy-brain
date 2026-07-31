# 策略知识库变更日志

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
