# iOS快捷指令：保存策略会话到Obsidian

创建名为“保存策略会话到Obsidian”的快捷指令：

1. 使用“获取剪贴板”取得已人工选择的会话文字。
2. 使用“询问输入”取得标题。
3. 再询问涉及股票代码；多个代码用逗号分隔。
4. 使用“当前日期”，格式化为 `yyyy-MM-dd`。
5. 用日期和当日人工递增序号生成稳定ID，例如
   `chat-2026-07-31-001`；同一天不得复用序号。
6. 把标题、ID、日期、股票代码和剪贴板内容套入
   `06_Conversations/Templates/CHAT_SESSION_TEMPLATE.md`。`content_hash`保留空值，
   由本地导入工具计算。
7. 用“存储文件”保存到iCloud中的Vault路径
   `07_Inbox/ChatGPT/<session_id>.md`，遇到同名文件时停止，不覆盖。
8. 以URL编码后的Vault名和笔记路径调用
   `obsidian://open?vault=<vault>&file=07_Inbox%2FChatGPT%2F<session_id>`。

回到电脑后先运行Inbox的dry-run。快捷指令只采集，不审核、不生成规则，也不修改
STRATEGY_MASTER。
