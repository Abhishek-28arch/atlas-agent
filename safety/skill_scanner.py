"""
JARVIS — safety/skill_scanner.py
Static security scanner for skill files — detects dangerous patterns
Inspired by OpenClaw's skill-scanner.ts
"""

import re
import os
from dataclasses import dataclass, field
from rich.console import Console

console = Console()


@dataclass
class ScanFinding:
    """Represents a security finding in a skill file."""
    rule_id: str
    severity: str  # "critical", "warn", "info"
    file: str
    line: int
    message: str
    evidence: str


@dataclass
class ScanSummary:
    """Summary of a skill scan."""
    scanned_files: int = 0
    critical: int = 0
    warn: int = 0
    info: int = 0
    findings: list = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return self.critical == 0


# ─── Rule Definitions ────────────────────────

# Line-level rules — match specific patterns per line
LINE_RULES = [
    {
        "rule_id": "dangerous-exec",
        "severity": "critical",
        "message": "Shell command execution detected",
        "pattern": re.compile(r'\bos\.system\s*\(|os\.popen\s*\('),
    },
    {
        "rule_id": "dangerous-subprocess",
        "severity": "critical",
        "message": "Subprocess execution detected",
        "pattern": re.compile(r'\bsubprocess\.(run|call|Popen|check_output|check_call)\s*\('),
        "requires_context": re.compile(r'import\s+subprocess|from\s+subprocess'),
    },
    {
        "rule_id": "dynamic-code-execution",
        "severity": "critical",
        "message": "Dynamic code execution detected (eval/exec/compile)",
        "pattern": re.compile(r'\b(eval|exec|compile)\s*\('),
    },
    {
        "rule_id": "dangerous-import",
        "severity": "critical",
        "message": "Dynamic import detected (__import__)",
        "pattern": re.compile(r'__import__\s*\('),
    },
    {
        "rule_id": "file-write",
        "severity": "warn",
        "message": "File write operation detected",
        "pattern": re.compile(r'open\s*\(.+["\']w["\']|\.write\s*\('),
    },
    {
        "rule_id": "network-request",
        "severity": "warn",
        "message": "Network request detected",
        "pattern": re.compile(r'requests\.(get|post|put|delete|patch)\s*\(|urllib\.request|httpx\.|aiohttp'),
    },
    {
        "rule_id": "env-access",
        "severity": "warn",
        "message": "Environment variable access detected",
        "pattern": re.compile(r'os\.environ|os\.getenv\s*\('),
    },
    {
        "rule_id": "crypto-mining",
        "severity": "critical",
        "message": "Possible crypto-mining reference",
        "pattern": re.compile(r'stratum\+tcp|stratum\+ssl|coinhive|cryptonight|xmrig', re.IGNORECASE),
    },
    {
        "rule_id": "pickle-load",
        "severity": "critical",
        "message": "Unsafe deserialization (pickle.load) — arbitrary code execution risk",
        "pattern": re.compile(r'pickle\.loads?\s*\(|cPickle\.loads?\s*\('),
    },
]

# Source-level rules — patterns that combine across the whole file
SOURCE_RULES = [
    {
        "rule_id": "potential-exfiltration",
        "severity": "critical",
        "message": "File read combined with network send — possible data exfiltration",
        "pattern": re.compile(r'open\s*\(.+["\']r["\']|\.read\s*\('),
        "requires_context": re.compile(r'requests\.(post|put)|httpx\.post|urllib\.request'),
    },
    {
        "rule_id": "obfuscated-code",
        "severity": "warn",
        "message": "Large base64 payload detected (possible obfuscation)",
        "pattern": re.compile(r'base64\.(b64decode|decodebytes)\s*\(\s*["\'][A-Za-z0-9+/=]{100,}'),
    },
    {
        "rule_id": "env-harvesting",
        "severity": "critical",
        "message": "Env var access combined with network send — possible credential harvesting",
        "pattern": re.compile(r'os\.environ|os\.getenv'),
        "requires_context": re.compile(r'requests\.(post|put)|httpx\.post|urllib\.request'),
    },
    {
        "rule_id": "reverse-shell",
        "severity": "critical",
        "message": "Possible reverse shell pattern detected",
        "pattern": re.compile(r'socket\.socket.*connect|/bin/(ba)?sh|nc\s+-'),
    },
]


def scan_source(source: str, file_path: str) -> list[ScanFinding]:
    """Scan Python source code for dangerous patterns."""
    findings = []
    lines = source.split("\n")
    matched_rules = set()

    # ── Line Rules ──
    for rule in LINE_RULES:
        if rule["rule_id"] in matched_rules:
            continue

        # Check context requirement
        context_req = rule.get("requires_context")
        if context_req and not context_req.search(source):
            continue

        for i, line in enumerate(lines):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("#"):
                continue

            match = rule["pattern"].search(line)
            if match:
                findings.append(ScanFinding(
                    rule_id=rule["rule_id"],
                    severity=rule["severity"],
                    file=file_path,
                    line=i + 1,
                    message=rule["message"],
                    evidence=stripped[:120],
                ))
                matched_rules.add(rule["rule_id"])
                break

    # ── Source Rules ──
    matched_source = set()
    for rule in SOURCE_RULES:
        key = f"{rule['rule_id']}::{rule['message']}"
        if key in matched_source:
            continue

        if not rule["pattern"].search(source):
            continue

        context_req = rule.get("requires_context")
        if context_req and not context_req.search(source):
            continue

        # Find line for evidence
        match_line = 0
        evidence = ""
        for i, line in enumerate(lines):
            if rule["pattern"].search(line):
                match_line = i + 1
                evidence = line.strip()[:120]
                break

        findings.append(ScanFinding(
            rule_id=rule["rule_id"],
            severity=rule["severity"],
            file=file_path,
            line=match_line or 1,
            message=rule["message"],
            evidence=evidence or source[:120],
        ))
        matched_source.add(key)

    return findings


def scan_file(file_path: str) -> ScanSummary:
    """Scan a single Python file for security issues."""
    summary = ScanSummary(scanned_files=1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except (IOError, UnicodeDecodeError):
        return summary

    findings = scan_source(source, file_path)
    summary.findings = findings

    for f in findings:
        if f.severity == "critical":
            summary.critical += 1
        elif f.severity == "warn":
            summary.warn += 1
        else:
            summary.info += 1

    return summary


def scan_directory(directory: str) -> ScanSummary:
    """Scan all Python files in a directory."""
    total = ScanSummary()

    if not os.path.isdir(directory):
        return total

    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(directory, filename)
            result = scan_file(filepath)
            total.scanned_files += result.scanned_files
            total.critical += result.critical
            total.warn += result.warn
            total.info += result.info
            total.findings.extend(result.findings)

    return total


def print_scan_report(summary: ScanSummary):
    """Pretty print scan results."""
    if not summary.findings:
        console.print("[green]✓ Skill scan clean — no security issues found[/green]")
        return

    console.print(f"\n[bold]🔍 Skill Security Scan[/bold]")
    console.print(f"  Files scanned: {summary.scanned_files}")
    console.print(f"  Critical: [red]{summary.critical}[/red]")
    console.print(f"  Warnings: [yellow]{summary.warn}[/yellow]")
    console.print(f"  Info: [dim]{summary.info}[/dim]\n")

    for f in summary.findings:
        color = {"critical": "red", "warn": "yellow", "info": "dim"}.get(f.severity, "white")
        icon = {"critical": "🔴", "warn": "🟡", "info": "🔵"}.get(f.severity, "⚪")
        console.print(f"  {icon} [{color}][{f.severity.upper()}][/{color}] {f.message}")
        console.print(f"     {f.file}:{f.line}")
        console.print(f"     [dim]{f.evidence}[/dim]\n")
