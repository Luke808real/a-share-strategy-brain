# Lineage and Quality Gates

## Candidate lineage

任何 candidate 必须能够追踪：

candidate
→ factor
→ setup
→ state
→ universe
→ snapshot
→ canonical row
→ ASL row
→ source
→ fetched_at
→ code SHA

同一链路还应携带相应的配置版本、quality flags 与计算 as-of。缺失任一必要父项时，
candidate 不是可发布事实。

## Fail-closed gates

| Gate | Required proof | Failure action |
|---|---|---|
| Data | 来源、覆盖与质量可证明 | block downstream |
| PIT | 只使用当时可知事实 | invalidate output |
| Universe | 适用范围和日期可复现 | no candidate publication |
| State | deterministic / parity / lineage | no setup promotion |
| Intraday | immutable checkpoint 与 5m provenance | no B2 assertion |
| OOS | 固定协议与 append-only settlement | no prospective claim |

质量门的作用是保留不确定性，而不是通过宽松默认值产生结果。
