# Data Plane

## Source boundary

数据平面路径为：

ashare-lake
→ ASL adapter
→ canonical contracts

canonical contracts 至少需要覆盖：

- daily
- minute / 5m
- status
- corporate actions
- adjustment
- universe
- provenance
- quality

## Version vocabulary

以下三个 SHA 表示不同事实，不能混用：

| Field | Meaning |
|---|---|
| ASL_UPSTREAM_SHA | 当前已观察到的上游 ashare-lake 提交 |
| ASL_VALIDATED_UPSTREAM_BASE | 已通过项目验证、可作为消费基线的上游提交 |
| ASL_PROJECT_SHA | 项目针对适配/验证所记录的 SHA 指针 |

TRACK LATEST != RUN LATEST。追踪上游最新提交只用于发现变化；运行必须使用已明确
验证的输入、版本和质量门。最新并不自动成为可运行或可发布的基线。
