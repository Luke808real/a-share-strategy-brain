# 成功案例候选特征

以下字段仅用于案例研究、特征比较、Entry Quality研究和后续黄金回归。
当前阶段不得影响`setup_stage`。

## 特征清单

- `ma_cluster_span_pct`
- `ma_reclaim_count`
- `close_location_value`
- `open_location_value`
- `pullback_trade_days`
- `pullback_depth_pct`
- `support_recovery_pct`
- `relaunch_volume_ratio`
- `distance_to_ma30_pct`
- `distance_to_ma120_pct`
- `stage_advance_trade_days`

## 冻结公式

```text
ma_cluster_span_pct =
    (max(MA5, MA10, MA20, MA30)
     - min(MA5, MA10, MA20, MA30))
    / close

close_location_value =
    (close - low) / (high - low)

open_location_value =
    (open - low) / (high - low)
```

若`high == low`，位置字段为不可用，不得伪造0或1。距离类字段统一明确分母和符号后
才能进入实现；缺失成交量时`relaunch_volume_ratio`不可用。

## 三个观察样本

| code | ma_cluster_span_pct | ma_reclaim_count | close_location | open_location | distance_to_ma120 |
|---|---:|---:|---:|---:|---:|
| 002640 | 0.0468 | 4 | 1.0000 | 0.0909 | +0.0556 |
| 600199 | 0.0522 | 4 | 1.0000 | 0.0000 | +0.0763 |
| 002891 | 0.0650 | 4 | 0.9718 | 0.0000 | +0.1325 |

上述值来自截图手工录入，仅用于形成研究问题，不构成统计结论。

## 待定义字段

- pullback起止点与交易日计数；
- pullback depth的锚点分母；
- support recovery相对Support下沿、中心或失效价；
- relaunch volume的比较窗口；
- stage advance的起始状态与截尾规则。
