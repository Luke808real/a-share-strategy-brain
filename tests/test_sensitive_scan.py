from __future__ import annotations

from tools.scan_sensitive_content import scan_paths


def test_sensitive_scanner_blocks_token_email_phone_path_and_headers(tmp_path):
    token = "gh" + "p_" + ("A" * 30)
    api_key = "sk-" + ("B" * 30)
    local_path = "/" + "Users" + "/private-user/secret"
    content = "\n".join(
        (
            token,
            api_key,
            "person" + "@" + "example.com",
            "138" + "12345678",
            local_path,
            "Cookie" + ": session=secret",
            "Authorization" + ": Bearer secret",
        )
    )
    path = tmp_path / "secret.md"
    path.write_text(content, encoding="utf-8")

    findings = scan_paths(tmp_path, (path,))

    assert {finding.rule for finding in findings} == {
        "GitHub token",
        "OpenAI API key",
        "email address",
        "phone number",
        "local user directory",
        "Cookie header",
        "Authorization header",
    }


def test_sensitive_scanner_allows_sha256_manifest_value(tmp_path):
    path = tmp_path / "manifest.yaml"
    path.write_text(
        "baseline_hash: d256f7886fbe32093530d9541cac6804caeb5c26cd81b67bcd15946020775e98\n",
        encoding="utf-8",
    )

    assert scan_paths(tmp_path, (path,)) == ()
