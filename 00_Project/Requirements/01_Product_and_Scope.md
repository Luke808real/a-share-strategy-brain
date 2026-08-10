# Product and Scope

## Product

最终产品是一个基于既有 canonical snapshot 的 A 股涨停回调再启动决策支持系统，
而不是行情下载器、通用量化平台、券商客户端或自动交易系统。它需要把可追溯的
结构、候选、日内 B2 观察与结果验证呈现给人工决策者。

最终用户体验由四类入口组成：

- Premarket Watchlist
- Intraday B2 Update
- Daily Review
- OOS Validation

它们只能消费已通过相应质量门的事实；展示候选不等于发出交易指令。

## Operating modes

下列模式是产品边界定义，不是当前授权状态：

| Mode | Purpose | Cannot claim |
|---|---|---|
| Research | 历史描述、假设与可验证因子研究 | production effectiveness |
| Shadow | 按预定义逻辑记录但不驱动决策的运行观察 | prospective OOS completion |
| Prospective OOS | 预先固定协议下的前瞻性观察 | automatic promotion |
| Forward | 人工审核的纸面计划与后续结算 | broker execution |
| Production | 面向人工的决策支持 | autonomous trading |

历史 rehearsal 不等同于 prospective OOS。每种模式的当前状态只在
[[00_Project/CURRENT_STATE]] 中声明。

## System boundary

系统的责任边界是：

- 从已批准的数据平面读取可追溯的 canonical facts；
- 以 point-in-time 方式生成 snapshot、universe、state、setup、factor 与 candidate；
- 在可用的 5m 事实基础上更新日内 B2 观察；
- 记录 outcome 与验证证据；
- 输出带有明确质量、provenance 和授权边界的人工决策支持。

它不在本合同内执行券商下单、隐式参数搜索、未审计的数据回填或跨策略自动优化。

## Definition of Done

某项能力只有同时满足以下条件才可称为完成：

1. 输入数据有可审计 provenance、质量状态和时间边界；
2. 规则与 lifecycle 有明确、可测试的语义；
3. 处理保持 point-in-time、deterministic 与可复现；
4. 输出可沿 lineage 回溯到源数据与代码 SHA；
5. 对应的验证、退出门和人工授权状态明确；
6. 不把 OBSERVATION 或 HYPOTHESIS 表述为 VALIDATED 或生产规则。
