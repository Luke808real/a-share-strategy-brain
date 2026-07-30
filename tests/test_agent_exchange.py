from __future__ import annotations

from pathlib import Path
import shutil

import pytest

from tools.agentlib import validate_agent_note
from tools.build_code_issue_draft import write_issue_draft
from tools.build_context_pack import build_context_pack_text
from tools.build_reasoning_index import build_implementation_queue_text
from tools.chatlib import with_content_hash
from tools.ingest_agent_case import ingest_agent_case
from tools.promote_agent_case import promote_agent_case, review_agent_case
from tools.validate_agent_exchange import validate_agent_exchange


def copied_vault(source: Path, destination: Path) -> Path:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
    )
    return destination


def case_intake_text(
    case_id: str = "case-002606-2026-07-29-001",
    *,
    status: str = "captured",
    title: str = "大连电瓷观察",
) -> str:
    return with_content_hash(
        f"""---
type: case_intake
case_id: {case_id}
stock_code: "002606"
stock_name: 大连电瓷
observation_date: 2026-07-29
source_session_id: chat-2026-07-31-bridge
source_digest: null
source_type: chatgpt
case_status: {status}
strategy_version: phase-2b2
market_status: 收盘后
image_refs: []
content_hash: ""
created_by: chatgpt
review_required: true
---

# {title}

## 图片可确认事实

只确认截图中可见文字，不推断缺失行情。

## 用户提供的背景

用户认为处于回调观察阶段。

## 数据限制

没有完整日线和涨停池。

## 当前setup状态

待程序验证。

## 支撑与压力

未知。

## B1/B2判断

证据不足。

## 风险事件

未知。

## 候选特征

缩量回调，仅作候选。

## 反对证据

缺少收盘后完整数据。

## 当前结论

进入人工观察。

## 置信度

low

## 次日验证条件

补充完整日线。

## 对冻结策略的影响

无。

## 建议动作

人工复核。
"""
    )


def write_case_source(tmp_path: Path, **kwargs: str) -> Path:
    path = tmp_path / "案例输入.md"
    path.write_text(case_intake_text(**kwargs), encoding="utf-8")
    return path


def change_request_text(status: str) -> str:
    return with_content_hash(
        f"""---
type: strategy_change_request
change_request_id: CR-20260731-001
source_cases:
- 002640-2026-07-27
source_rule_ids:
- MA30_OVERHEAD
current_strategy_version: phase-2b2
proposed_scope: 评估MA30高悬风险
affected_models:
- StrategySignal
affected_config:
- entry_quality
expected_history_impact: 不得改变既有B1日期
required_regression_cases:
- 002640-2026-07-27
status: {status}
content_hash: ""
created_by: human
review_required: true
---

# MA30高悬变更请求

## 当前规则

当前未冻结该风险。

## 新观察

来自案例观察。

## 成功样本

002640。

## 失败对照

TODO。

## 候选规则

MA30_OVERHEAD。

## 历史B1/B2日期影响

不得改变。

## INVALID影响

无。

## 新阈值需求

待研究。

## 必需测试

Golden Regression。

## 回滚方案

撤销新增入场评价。

## 人工审批

状态由人工维护。
"""
    )


def test_case_intake_schema_is_valid_and_chinese_round_trips(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    source = write_case_source(tmp_path)

    destination = ingest_agent_case(root, source)

    assert validate_agent_note(root, destination) == []
    assert "大连电瓷" in destination.read_text(encoding="utf-8")
    assert validate_agent_exchange(root) == []


def test_duplicate_case_id_and_content_hash_are_rejected(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    source = write_case_source(tmp_path)
    ingest_agent_case(root, source)
    duplicate = tmp_path / "重复.md"
    duplicate.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(ValueError) as captured:
        ingest_agent_case(root, duplicate)

    assert "duplicate case_id" in str(captured.value)
    assert "duplicate content_hash" in str(captured.value)


def test_captured_case_cannot_enter_success_and_agent_cannot_touch_master(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    master = root / "01_Strategy" / "STRATEGY_MASTER.md"
    before = master.read_bytes()
    source = write_case_source(tmp_path)
    ingest_agent_case(root, source)

    with pytest.raises(ValueError, match="CAPTURED"):
        promote_agent_case(
            root=root,
            case_id="case-002606-2026-07-29-001",
            outcome="success",
        )

    assert master.read_bytes() == before


def test_explicit_review_then_promotion_creates_observed_case(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    source = write_case_source(tmp_path)
    ingest_agent_case(root, source)
    review_agent_case(root, "case-002606-2026-07-29-001")

    result = promote_agent_case(
        root=root,
        case_id="case-002606-2026-07-29-001",
        outcome="watching",
    )

    assert "case_status: observed" in result.read_text(encoding="utf-8")
    assert "source_case_id" in result.read_text(encoding="utf-8")
    assert not (
        root
        / "08_AgentExchange"
        / "Incoming"
        / "case-002606-2026-07-29-001.md"
    ).exists()


def test_unreviewed_case_only_appears_in_pending_context_section(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    source = write_case_source(tmp_path)
    ingest_agent_case(root, source)

    context = build_context_pack_text(root)
    pending = context.index("## 13. 待审核Agent Intake")
    approved = context.index("## 14. 获批代码变更请求")

    assert "case-002606-2026-07-29-001" in context[pending:approved]
    assert "case-002606-2026-07-29-001" not in context[:pending]


def test_reasoning_digest_requires_opposition_and_uncertainty(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    template = (
        root
        / "08_AgentExchange"
        / "Templates"
        / "REASONING_DIGEST_TEMPLATE.md"
    ).read_text(encoding="utf-8")
    text = (
        template.replace("digest-session-id", "digest-session-001")
        .replace("session-id", "session-001")
    )
    path = (
        root
        / "06_Conversations"
        / "ReasoningDigests"
        / "digest-session-001.md"
    )
    path.write_text(with_content_hash(text), encoding="utf-8")

    errors = validate_agent_note(root, path)

    assert any("反对证据" in error for error in errors)
    assert any("不确定性" in error for error in errors)


def test_agent_schema_rejects_frozen_state(vault_root_path, tmp_path):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    path = write_case_source(tmp_path, status="FROZEN")

    errors = validate_agent_note(root, path)

    assert any("unsupported value" in error for error in errors)


def test_unapproved_request_stays_out_of_queue_and_approved_builds_issue(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    request = (
        root
        / "05_Codex"
        / "ChangeRequests"
        / "CR-20260731-001.md"
    )
    request.write_text(change_request_text("proposed"), encoding="utf-8")

    assert "CR-20260731-001" not in build_implementation_queue_text(root)
    with pytest.raises(ValueError, match="not approved"):
        write_issue_draft(root, "CR-20260731-001")

    request.write_text(
        change_request_text("approved_for_implementation"),
        encoding="utf-8",
    )
    issue = write_issue_draft(root, "CR-20260731-001")

    assert "CR-20260731-001" in issue.read_text(encoding="utf-8")
    assert "MA30_OVERHEAD" in issue.read_text(encoding="utf-8")
