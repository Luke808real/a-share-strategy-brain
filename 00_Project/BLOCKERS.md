# Blockers

本文件只保存仍然 OPEN 的 blocker。已关闭项目应进入 state snapshot、正式验证报告或
decision，而不是继续留在这里。优先级不构成自动执行授权。

## P0

1. bounded historical ST backfill + post-write audit 未关闭。
2. 08/07 state 尚未在新 ASL facts 上重建验证。
3. ACTIVE_SETUP 尚未正式产出。
4. live 5m immutable 10:30 checkpoint 未闭环。
5. TTL suspension-age semantic conflict 未最终核对。
6. R9 runtime provenance / old ASL_CODE_SHA pin 需在 primary 前关闭。

## P1

1. 5 delisted terminal evidence。
2. historical delisted adj refresh。
3. broader delisted discovery。

## P2

1. Production。
2. Forward。
3. TradePlan。

当前执行与下一 gate 见 [[00_Project/CURRENT_STATE]]。每个 blocker 的关闭都需要可追溯
证据、精确 SHA 独立审查和明确 PASS；不得用缺失输出、口头结论或历史记录代替。
