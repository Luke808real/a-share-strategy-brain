# Runtime and Observability

最终系统应能在一个清晰、可审计的状态面板中展示：

- DATA_DATE
- ASL_SHA
- SNAPSHOT
- GENERATION
- UNIVERSE_N/HASH
- ACTIVE_SETUP_N
- CANDIDATE_N
- CHECKPOINT
- OOS_ROWS
- BLOCKERS
- PRODUCTION
- FORWARD
- TRADEPLAN

每个字段需标注来源、as-of、质量状态或不可用原因。空值不能被伪装为零，未运行不能
被伪装为成功。

这是观察性与产品需求说明，不在本轮创建 runtime、CLI、数据库、缓存或监控服务。
