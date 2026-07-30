# iOS快捷指令：保存案例截图草稿

创建“保存策略案例截图”快捷指令：

1. 从照片选择器选择截图，不自动读取整个照片库。
2. 依次询问六位股票代码、股票名称和观察日期。
3. 使用稳定文件名 `<code>-<date>-01.<ext>` 保存到
   `07_Inbox/Screenshots/`；同名时递增末尾序号，不覆盖。
4. 从 `02_Cases/Templates/CASE_TEMPLATE.md` 创建Watching案例草稿，原始事实不足
   的章节写 `TODO`，不要从截图猜测价格、成交量或指标。
5. 在案例的“原始数据”中用Obsidian相对路径引用截图；例如路径由
   `07_Inbox/Screenshots/`与实际文件名拼接，避免把示例占位符保存成链接。
6. 保存案例草稿到 `07_Inbox/Manual/`，打开Obsidian进行人工校对。

截图与Inbox默认不进入Git。本文只说明配置步骤，不尝试从Codex控制iPhone。
