from tools.build_context_pack import build_context_pack_text


EXPECTED_HEADINGS = (
    "## 1. 当前阶段",
    "## 2. 当前冻结策略摘要",
    "## 3. 状态机",
    "## 4. 最近已采纳决策",
    "## 5. 当前PROPOSED规则",
    "## 6. 成功案例摘要",
    "## 7. 失败案例摘要",
    "## 8. 当前待办",
    "## 9. 最新Codex提示",
    "## 10. 已人工审核会话",
    "## 11. 最近已审核案例",
    "## 12. 最近可审计推理摘要",
    "## 13. 待审核Agent Intake",
    "## 14. 获批代码变更请求",
    "## 15. 代码仓库基线与drift",
)


def test_context_pack_section_order_is_stable(vault_root_path):
    output = build_context_pack_text(vault_root_path)
    positions = tuple(output.index(heading) for heading in EXPECTED_HEADINGS)

    assert positions == tuple(sorted(positions))
    assert all(
        f"> Source" in output[positions[index] :]
        for index in range(len(positions))
    )


def test_context_pack_is_identical_for_identical_input(vault_root_path):
    first = build_context_pack_text(vault_root_path)
    second = build_context_pack_text(vault_root_path)

    assert first == second
    assert "完整历史聊天原文" in first
    assert "\x00" not in first
