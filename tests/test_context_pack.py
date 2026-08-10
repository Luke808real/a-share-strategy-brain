from tools.build_context_pack import build_context_pack_text


EXPECTED_HEADINGS = (
    "## 1. Agent Handoff",
    "## 2. Current State",
    "## 3. Project Charter",
    "## 4. 当前冻结策略摘要",
    "## 5. 状态机",
    "## 6. 最近已采纳决策",
    "## 7. 当前PROPOSED规则",
    "## 8. 成功案例摘要",
    "## 9. 失败案例摘要",
    "## 10. 当前待办",
    "## 11. 已人工审核会话",
    "## 12. 最近已审核案例",
    "## 13. 最近可审计推理摘要",
    "## 14. 待审核Agent Intake",
    "## 15. 获批代码变更请求",
    "## 16. 代码仓库基线与drift",
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


def test_context_pack_bootstraps_from_project_os_current_truth(vault_root_path):
    output = build_context_pack_text(vault_root_path)
    bootstrap = output[: output.index("## 6. 最近已采纳决策")]

    assert "[[00_Project/AGENT_HANDOFF]]" in bootstrap
    assert "[[00_Project/CURRENT_STATE]]" in bootstrap
    assert "[[00_Project/PROJECT_CHARTER]]" in bootstrap
    assert "[[05_Codex/CURRENT_PHASE]]" not in bootstrap
    assert "project_stage: PRE_R9_DATA_CLOSURE" in bootstrap
    assert "production: false" in bootstrap
    assert "forward: false" in bootstrap
    assert "tradeplan: false" in bootstrap
    assert "primary_oos: false" in bootstrap
    assert "oos_rows: 0" in bootstrap
    assert "ASL_BOUNDED_HISTORICAL_ST_BACKFILL_V01" in bootstrap
    assert "RUNNING / RESULT_PENDING" in bootstrap
