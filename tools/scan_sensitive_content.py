"""Scan Git-eligible knowledge files for common secrets and personal data."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Iterable, Sequence

try:
    from .vaultlib import vault_root
except ImportError:
    from vaultlib import vault_root


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str


RULES = (
    (
        "GitHub token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    ),
    (
        "OpenAI API key",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "email address",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    ),
    (
        "phone number",
        re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)"),
    ),
    (
        "local user directory",
        re.compile(r"/Users/[A-Za-z0-9._-]+(?:/|\b)"),
    ),
    (
        "Cookie header",
        re.compile(r"(?im)^\s*Cookie\s*:\s*\S+"),
    ),
    (
        "Authorization header",
        re.compile(r"(?im)^\s*Authorization\s*:\s*(?:Bearer|Basic)\s+\S+"),
    ),
)
TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".py",
        ".toml",
        ".yaml",
        ".yml",
        ".json",
        ".sh",
        ".txt",
        ".gitignore",
    }
)


def git_eligible_paths(root: Path) -> tuple[Path, ...]:
    completed = subprocess.run(
        (
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
        ),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(
        root / value
        for value in sorted(completed.stdout.splitlines())
        if value
    )


def scan_paths(root: Path, paths: Iterable[Path]) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    for path in sorted(set(paths), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        if path.name == ".gitignore":
            suffix_allowed = True
        else:
            suffix_allowed = path.suffix.lower() in TEXT_SUFFIXES
        if not suffix_allowed or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in RULES:
                if pattern.search(line):
                    findings.append(
                        Finding(path=path, line=line_number, rule=label)
                    )
    return tuple(findings)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan Git-eligible files for secrets and personal data"
    )
    parser.add_argument("--path", type=Path, action="append")
    args = parser.parse_args(argv)
    root = vault_root()
    paths = (
        tuple(path.expanduser().resolve() for path in args.path)
        if args.path
        else git_eligible_paths(root)
    )
    findings = scan_paths(root, paths)
    if findings:
        print(f"Sensitive content scan failed with {len(findings)} finding(s):")
        for finding in findings:
            try:
                label = finding.path.relative_to(root).as_posix()
            except ValueError:
                label = finding.path.name
            print(f"- {label}:{finding.line}: {finding.rule}")
        return 1
    print(f"Sensitive content scan passed: {len(paths)} eligible file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
