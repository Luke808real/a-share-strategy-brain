# 本地收件箱

本目录用于尚未处理的人工资料，默认不进入Git：

- `ChatGPT/`：按 `CHAT_SESSION_TEMPLATE.md` 整理的会话；
- `Screenshots/`：待归档截图；
- `Manual/`：其他人工笔记。

会话原文使用 `python tools/ingest_chat_inbox.py --dry-run` 预检，确认后再执行
默认导入。`--archive` 会在成功导入后把Inbox源文件移动到同样受Git忽略的
`06_Conversations/Processed/`。工具不会创建FROZEN规则或修改冻结策略真源。
