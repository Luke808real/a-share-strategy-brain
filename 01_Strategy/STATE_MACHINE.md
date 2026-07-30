# 状态机

## setup_stage

| 状态 | 确定性含义 | 主要进入条件 | 主要退出条件 |
|---|---|---|---|
| NORMAL | 当前无有效锚点 | 无有效涨停锚点 | 新有效锚点 |
| LIMIT_ANCHOR | 当日为锚点日 | 有效涨停锚点 | 后续交易日 |
| WATCH_PULLBACK | 锚点后观察 | B1结构未达阈值 | B1就绪、失效、新锚点或过期 |
| B1_READY | 回调企稳结构成立 | B1可用条件达阈值且可冻结支撑/失效 | B2就绪、失效、新锚点 |
| B2_READY | 触发价已冻结待确认 | 上一日B1或已有触发价 | B2确认、失效、新锚点 |
| B2_CONFIRMED | 已站稳冻结触发价 | 高点触发、收盘站稳、量价多数 | 失效、新锚点或过期 |
| INVALID | 当前setup结构失效 | 任一严重失效条件 | 仅由新setup替代 |

## event_flags

- `SUPPORT_WARNING`：已生效支撑受到威胁；
- `NEAR_S1`：尚未突破时接近S1；
- `S1_BREAKOUT`：收盘突破S1上沿；
- `S2_EXHAUSTED`：触及S1并出现衰竭组合。

`NEAR_S1`与`S1_BREAKOUT`互斥。INVALID清除普通支撑与S1事件。

## 时序

```text
T日计算候选
  └─ T日冻结快照（eligible_from > T）
       └─ T+1或之后由previous_signal沿用
            └─ eligible_from <= 当前交易日时才参与判断
```

## 终止

INVALIDATED优先记录首次失效日；新锚点将仍活动的旧setup标记为
SUPERSEDED_BY_NEW_ANCHOR；没有新锚点且离开有效窗口时标记EXPIRED。
