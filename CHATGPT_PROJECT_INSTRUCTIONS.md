# ChatGPT Project Instructions

1. 先读取 [[05_Codex/CURRENT_PHASE]]、[[01_Strategy/STRATEGY_MASTER]] 和
   [[01_Strategy/RULE_CATALOG]]。
2. 只把状态为 `FROZEN` 或 `ACCEPTED` 且已由ADR采纳的内容视为当前策略。
3. `OBSERVED`、`PROPOSED` 只能形成研究建议，不能被表述为已实现规则。
4. 不从单一案例、截图或博客观点修改阈值。
5. 所有价格、比例和评分计算保持 Decimal 语义；所有判断遵守无未来数据。
6. 任何变更先建立ADR，说明历史信号、代码、配置、测试和黄金样本影响。
7. 不伪造缺失行情、分钟数据、涨停池字段或人工结论。
8. 本Vault不授权数据库、全市场扫描、回测、自动交易或盘中监控。
9. 需要实现时，先由 [[05_Codex/NEXT_PROMPT]] 生成范围明确的Codex任务。
10. 输出结论时标注信息来源和不确定性。
