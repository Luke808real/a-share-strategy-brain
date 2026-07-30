# 隐私与Git边界

## 只保留在本地或iCloud

- `07_Inbox/`中的会话、截图和人工原稿；
- `06_Conversations/Raw/`与`Processed/`中的完整聊天文字；
- ChatGPT官方导出ZIP、`conversations.json`及附件；
- `attachments/screenshots/`中的截图。

这些路径由 `.gitignore` 阻止进入Git。移动Vault前应确认iCloud端到端保护和设备
访问权限；不要把含账号、姓名、联系方式或未公开持仓的信息放进公共仓库。

## 可进入私人Git

人工确认后的Digests、脱敏案例、Candidate Rules、ADR、审核队列和Context Pack
可以进入私人Git。脱敏后的Reasoning Digest、Agent Case、Change Request也可以
提交。提交前仍应运行`python tools/scan_sensitive_content.py`并人工检查隐私；
“可提交”不等于“可公开”。

## 可上传到ChatGPT

优先上传 `exports/LLM_CONTEXT_PACK.md`、`LLM_CONTEXT_DELTA.md` 和必要的
`CASE_CONTEXT_PACK.md`。上传前检查脱敏，不上传Raw、完整账号导出或无关附件。

## 删除一个会话

先运行 `python tools/purge_session.py --session-id <id> --confirm <id>`。
工具会先检查冻结规则、已采纳ADR和确认案例的依赖；存在依赖时停止。成功后会删除
Raw、Digest、清单引用及尚未冻结的派生草稿，并重建可再生索引和上下文包。

## 重新生成上下文包

```bash
python tools/build_context_pack.py --rebuild-full
python tools/build_context_delta.py
python tools/validate_vault.py
```

生成工具不读取网络，也不把Raw原文写入上下文包。

GitHub发布必须通过`tools/github_bridge_publish.sh`。脚本不会暂存Raw、截图、ZIP、
账号导出或环境文件；没有`--confirm`时只做验证与预览。
