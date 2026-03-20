#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — 跨平台相容性檢查
# 路徑：setup/scripts/check-compat.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 全 Repo 跨平台健檢工具。掃描 .py、.sh、.md（技能）、hook，
# 依 6 條規則產出嚴重度分級報告。
#
# 用法：
#   python3 setup/scripts/check-compat.py              # 完整掃描
#   python3 setup/scripts/check-compat.py --quick       # 只看高風險
#   python3 setup/scripts/check-compat.py FILE          # 單檔檢查
#   python3 setup/scripts/check-compat.py --json        # JSON 輸出
#
# 規則：
#   1. 硬編碼路徑（🔴 高）
#   2. 平台限定指令（🟡 中）
#   3. 未遷移 Shell 腳本（🟡 中）
#   4. Python 環境假設（🟡 中）
#   5. Hook 安全性（🟡 中）
#   6. 換行符配置（🟢 低）

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── ANSI 顏色（支援 NO_COLOR） ──────────────────────────

_NO_COLOR = (
    os.environ.get("NO_COLOR")
    or (sys.platform == "win32" and not os.environ.get("WT_SESSION"))
)
RED = "" if _NO_COLOR else "\033[0;31m"
YELLOW = "" if _NO_COLOR else "\033[1;33m"
GREEN = "" if _NO_COLOR else "\033[0;32m"
DIM = "" if _NO_COLOR else "\033[0;90m"
BOLD = "" if _NO_COLOR else "\033[1m"
NC = "" if _NO_COLOR else "\033[0m"

# ── 排除目錄 ─────────────────────────────────────────────

EXCLUDE_DIRS = {".git", "node_modules", "venv", "__pycache__", "temp", "Tool Download"}

# ── 嚴重度 ───────────────────────────────────────────────

SEV_HIGH = "high"
SEV_MED = "medium"
SEV_LOW = "low"

SEV_LABEL = {
    SEV_HIGH: f"{RED}🔴 高{NC}",
    SEV_MED: f"{YELLOW}🟡 中{NC}",
    SEV_LOW: f"{GREEN}🟢 低{NC}",
}

SEV_LABEL_PLAIN = {
    SEV_HIGH: "🔴 高",
    SEV_MED: "🟡 中",
    SEV_LOW: "🟢 低",
}

# ── 偵測規則 ─────────────────────────────────────────────

# 規則 1：硬編碼路徑（🔴）——真正的跨平台問題
HARDCODED_PATH_PATTERNS = [
    (r'["\']\/Users\/', "/Users/ — macOS 限定家目錄"),
    (r'["\']\/home\/', "/home/ — Linux 限定家目錄"),
    (r'["\'][A-Z]:\\', "Windows 磁碟路徑 — 硬編碼"),
    (r'["\']\/opt\/homebrew', "/opt/homebrew — macOS Homebrew 路徑"),
]

# 規則 1b：os.path 用法（🟢 低）——功能上跨平台安全，但建議改用 pathlib
OSPATH_PATTERNS = [
    (r'\bos\.path\.join\b', "os.path.join — 建議改用 pathlib.Path"),
    (r'\bos\.path\.exists\b', "os.path.exists — 建議改用 Path.exists()"),
    (r'\bos\.path\.dirname\b', "os.path.dirname — 建議改用 Path.parent"),
    (r'\bos\.path\.basename\b', "os.path.basename — 建議改用 Path.name"),
]

# 規則 2：平台限定指令（🟡）——在 .py 的 subprocess 呼叫中
PY_PLATFORM_COMMANDS = [
    (r'subprocess\.\w+\([^)]*["\']sed\s', "sed — Windows 無內建版本"),
    (r'subprocess\.\w+\([^)]*["\']awk\s', "awk — Windows 無內建版本"),
    (r'subprocess\.\w+\([^)]*["\']grep\s', "grep — Windows 無內建版本"),
    (r'subprocess\.\w+\([^)]*["\']chmod\s', "chmod — Windows 無此指令"),
    (r'subprocess\.\w+\([^)]*["\']open\s', "open — macOS 限定（Windows 用 start）"),
    (r'\bos\.system\s*\(', "os.system() — 建議改用 subprocess.run()"),
]

# 規則 2 延伸：技能 .md 中的 bash block（複用 skill-platform-check.py 規則）
SKILL_PLATFORM_PATTERNS = [
    (r"\bcommand\s+-v\b", "command -v"),
    (r"\bmkdir\s+-p\b", "mkdir -p"),
    (r"\bcp\s+", "cp（複製檔案）"),
    (r"(?<!\$env:)\b~\/", "~/（家目錄路徑）"),
    (r"\bkill\s+", "kill（終止程序）"),
    (r"\bchmod\s+", "chmod"),
    (r"\buname\b", "uname"),
    (r"\bopen\s+\"?https?:", "open URL"),
    (r"\bgrep\s+-", "grep"),
    (r"\bsed\s+-", "sed"),
    (r"\bawk\s+", "awk"),
]

# 規則 4：Python 環境假設（🟡）
PY_ENV_PATTERNS = [
    (r"^#!\/usr\/bin\/python3", "硬編碼 shebang — 建議 #!/usr/bin/env python3"),
    (r"\bimport\s+fcntl\b", "fcntl — Unix 限定模組"),
    (r"\bimport\s+termios\b", "termios — Unix 限定模組"),
    (r"\bimport\s+resource\b", "resource — Unix 限定模組"),
    (r"\bos\.getuid\(\)", "os.getuid() — Unix 限定"),
    (r"\bos\.getgid\(\)", "os.getgid() — Unix 限定"),
    (r"\bos\.symlink\(", "os.symlink() — Windows 需管理員權限"),
]


# ── 工具函式 ─────────────────────────────────────────────

def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return Path.cwd()
    return Path(result.stdout.strip())


def should_skip(path: Path, repo_root: Path) -> bool:
    """是否跳過此路徑"""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return True
    # 排除自身（規則定義字串會觸發 false positive）
    if rel.name == "check-compat.py":
        return True
    return any(part in EXCLUDE_DIRS for part in rel.parts)


def collect_files(repo_root: Path, target: Optional[Path] = None) -> dict:
    """收集要掃描的檔案，依類型分組"""
    if target:
        # 單檔模式
        suffix = target.suffix
        category = {
            ".py": "python",
            ".sh": "shell",
            ".md": "skill",
        }.get(suffix, "other")
        return {category: [target]}

    files = {"python": [], "shell": [], "skill": [], "hook": []}

    # Python 腳本
    for pattern in ["setup/**/*.py", "publish/**/*.py", "ai-core/**/*.py",
                     ".claude/scripts/**/*.py"]:
        for p in repo_root.glob(pattern):
            if not should_skip(p, repo_root):
                files["python"].append(p)

    # Shell 腳本
    for p in repo_root.rglob("*.sh"):
        if not should_skip(p, repo_root):
            files["shell"].append(p)

    # 技能 .md
    for pattern in ["ai-core/skills/*.md", "workspaces/*/skills/*.md",
                     "workspaces/*/*/skills/*.md"]:
        for p in repo_root.glob(pattern):
            if not should_skip(p, repo_root) and p.name != "README.md":
                files["skill"].append(p)

    # Hook 配置
    hook_dir = repo_root / "setup" / "hooks"
    if hook_dir.exists():
        for p in hook_dir.iterdir():
            if p.is_file():
                files["hook"].append(p)

    return files


# ── 規則檢查函式 ─────────────────────────────────────────

def check_rule1_hardcoded_paths(files: dict, repo_root: Path) -> list:
    """規則 1：硬編碼路徑（🔴）+ os.path 用法（🟢）"""
    findings = []
    for category in ["python"]:
        for filepath in files.get(category, []):
            try:
                lines = filepath.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, PermissionError):
                continue
            for i, line in enumerate(lines, 1):
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                # 🔴 高：真正的硬編碼路徑
                for pattern, desc in HARDCODED_PATH_PATTERNS:
                    if re.search(pattern, line):
                        rel = str(filepath.relative_to(repo_root))
                        findings.append({
                            "severity": SEV_HIGH,
                            "rule": 1,
                            "file": rel,
                            "line": i,
                            "desc": desc,
                            "source": line.strip()[:120],
                        })
                # 🟢 低：os.path 風格建議
                for pattern, desc in OSPATH_PATTERNS:
                    if re.search(pattern, line):
                        rel = str(filepath.relative_to(repo_root))
                        findings.append({
                            "severity": SEV_LOW,
                            "rule": 1,
                            "file": rel,
                            "line": i,
                            "desc": desc,
                            "source": line.strip()[:120],
                        })
    return findings


def check_rule2_platform_commands(files: dict, repo_root: Path) -> list:
    """規則 2：平台限定指令（🟡）"""
    findings = []

    # 2a: Python subprocess 呼叫
    for filepath in files.get("python", []):
        try:
            content = filepath.read_text(encoding="utf-8")
            lines = content.splitlines()
        except (UnicodeDecodeError, PermissionError):
            continue
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            for pattern, desc in PY_PLATFORM_COMMANDS:
                if re.search(pattern, line):
                    rel = str(filepath.relative_to(repo_root))
                    findings.append({
                        "severity": SEV_MED,
                        "rule": 2,
                        "file": rel,
                        "line": i,
                        "desc": desc,
                        "source": line.strip()[:120],
                    })

    # 2b: 技能 .md 中的 bash block 缺 PowerShell 配對
    for filepath in files.get("skill", []):
        try:
            content = filepath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        findings.extend(_check_skill_bash_blocks(filepath, content, repo_root))

    return findings


def _check_skill_bash_blocks(filepath: Path, content: str, repo_root: Path) -> list:
    """檢查技能 .md 的 bash block 是否有 PowerShell 配對"""
    findings = []
    blocks = _parse_code_blocks(content)
    bash_blocks = [b for b in blocks if b["lang"] in ("bash", "sh")]
    ps_blocks = [b for b in blocks if b["lang"] in ("powershell", "ps1", "pwsh")]

    # Step 邊界
    step_boundaries = []
    for i, line in enumerate(content.splitlines()):
        if re.match(r"^###\s+Step\s+\d+", line):
            step_boundaries.append(i + 1)

    def same_step(a: int, b: int) -> bool:
        sa = sb = 0
        for boundary in step_boundaries:
            if boundary <= a:
                sa = boundary
            if boundary <= b:
                sb = boundary
        return sa == sb

    for bb in bash_blocks:
        found = []
        for pattern, label in SKILL_PLATFORM_PATTERNS:
            if re.search(pattern, bb["code"]):
                found.append(label)
        if not found:
            continue
        has_ps = any(same_step(bb["line"], ps["line"]) for ps in ps_blocks)
        if not has_ps:
            rel = str(filepath.relative_to(repo_root))
            findings.append({
                "severity": SEV_MED,
                "rule": 2,
                "file": rel,
                "line": bb["line"],
                "desc": f"bash 區塊含 {'、'.join(found)}，缺 PowerShell 配對",
                "source": "",
            })
    return findings


def _parse_code_blocks(content: str) -> list:
    """解析 Markdown fenced code blocks"""
    blocks = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^```(\w*)\s*$", lines[i])
        if m:
            lang = m.group(1).lower()
            start = i + 1
            code_lines = []
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"lang": lang, "code": "\n".join(code_lines), "line": start})
        i += 1
    return blocks


def check_rule3_unmigrated_shell(files: dict, repo_root: Path) -> list:
    """規則 3：未遷移 Shell 腳本（🟡）"""
    findings = []
    xplatform = repo_root / "ai-core" / "reference" / "cross-platform.yaml"
    if not xplatform.exists():
        return findings

    try:
        content = xplatform.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return findings

    # 簡易解析 migration_status（避免 PyYAML 依賴）
    in_migration = False
    for line in content.splitlines():
        if line.strip().startswith("migration_status:"):
            in_migration = True
            continue
        if in_migration:
            if not line.startswith(" ") and not line.startswith("\t") and line.strip():
                break
            m = re.match(r"\s+(.+?):\s+\{.*status:\s*active", line)
            if m:
                script = m.group(1).strip()
                findings.append({
                    "severity": SEV_MED,
                    "rule": 3,
                    "file": script,
                    "line": 0,
                    "desc": f"Shell 腳本仍在服役（status: active），建議遷移至 Python",
                    "source": "",
                })
    return findings


def check_rule4_python_env(files: dict, repo_root: Path) -> list:
    """規則 4：Python 環境假設（🟡）"""
    findings = []
    for filepath in files.get("python", []):
        try:
            lines = filepath.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, PermissionError):
            continue
        for i, line in enumerate(lines, 1):
            for pattern, desc in PY_ENV_PATTERNS:
                if re.search(pattern, line):
                    rel = str(filepath.relative_to(repo_root))
                    findings.append({
                        "severity": SEV_MED,
                        "rule": 4,
                        "file": rel,
                        "line": i,
                        "desc": desc,
                        "source": line.strip()[:120],
                    })
    return findings


def check_rule5_hooks(files: dict, repo_root: Path) -> list:
    """規則 5：Hook 安全性（🟡）"""
    findings = []
    for filepath in files.get("hook", []):
        try:
            content = filepath.read_text(encoding="utf-8")
            first_line = content.splitlines()[0] if content.strip() else ""
        except (UnicodeDecodeError, PermissionError):
            continue

        rel = str(filepath.relative_to(repo_root))

        # 檢查 shebang
        if first_line and not first_line.startswith("#!/"):
            findings.append({
                "severity": SEV_MED,
                "rule": 5,
                "file": rel,
                "line": 1,
                "desc": "Hook 缺少 shebang",
                "source": first_line[:80],
            })

        # 確認是否委派給 Python
        if "python" not in content and ".py" not in content:
            findings.append({
                "severity": SEV_MED,
                "rule": 5,
                "file": rel,
                "line": 0,
                "desc": "Hook 未委派給 Python 腳本（薄層模式）",
                "source": "",
            })
    return findings


def check_rule6_gitattributes(repo_root: Path) -> list:
    """規則 6：換行符配置（🟢）"""
    findings = []
    ga = repo_root / ".gitattributes"
    if not ga.exists():
        findings.append({
            "severity": SEV_LOW,
            "rule": 6,
            "file": ".gitattributes",
            "line": 0,
            "desc": ".gitattributes 不存在——換行符未正規化",
            "source": "",
        })
    else:
        content = ga.read_text(encoding="utf-8")
        if "text=auto" not in content:
            findings.append({
                "severity": SEV_LOW,
                "rule": 6,
                "file": ".gitattributes",
                "line": 0,
                "desc": ".gitattributes 缺少 '* text=auto' 規則",
                "source": "",
            })
    return findings


# ── 報告產出 ─────────────────────────────────────────────

def format_report(findings: list, file_counts: dict, repo_root: Path) -> str:
    """產出 Markdown 格式報告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_files = sum(len(v) for v in file_counts.values())

    high = [f for f in findings if f["severity"] == SEV_HIGH]
    med = [f for f in findings if f["severity"] == SEV_MED]
    low = [f for f in findings if f["severity"] == SEV_LOW]

    lines = [
        f"{BOLD}TeacherOS 跨平台相容性報告{NC}",
        "",
        f"掃描時間：{now}",
        f"掃描檔案：{total_files}（Python {len(file_counts.get('python', []))} + "
        f"Shell {len(file_counts.get('shell', []))} + "
        f"Skill {len(file_counts.get('skill', []))} + "
        f"Hook {len(file_counts.get('hook', []))}）",
        "",
    ]

    # 摘要
    lines.append(f"  {RED}🔴 高：{len(high)}{NC}  "
                 f"{YELLOW}🟡 中：{len(med)}{NC}  "
                 f"{GREEN}🟢 低：{len(low)}{NC}  "
                 f"✅ 安全：{total_files - len(set(f['file'] for f in findings))} 檔")
    lines.append("")

    if not findings:
        lines.append(f"{GREEN}所有檔案通過跨平台相容性檢查。{NC}")
        return "\n".join(lines)

    # 依嚴重度分組
    for sev, label, items in [
        (SEV_HIGH, SEV_LABEL[SEV_HIGH], high),
        (SEV_MED, SEV_LABEL[SEV_MED], med),
        (SEV_LOW, SEV_LABEL[SEV_LOW], low),
    ]:
        if not items:
            continue
        lines.append(f"{'─' * 50}")
        lines.append(f"{label}（{len(items)} 項）")
        lines.append("")
        for f in items:
            loc = f"第 {f['line']} 行" if f["line"] else ""
            lines.append(f"  [{f['file']}] {loc}")
            lines.append(f"  規則 {f['rule']}：{f['desc']}")
            if f["source"]:
                lines.append(f"  {DIM}{f['source']}{NC}")
            lines.append("")

    # 修正參考
    lines.append(f"{'─' * 50}")
    lines.append(f"{DIM}修正參考：ai-core/reference/cross-platform.yaml{NC}")
    lines.append(f"{DIM}技能指引：ai-core/skills/README.md Step 2{NC}")

    return "\n".join(lines)


def format_json(findings: list, file_counts: dict) -> str:
    """JSON 格式輸出"""
    return json.dumps({
        "timestamp": datetime.now().isoformat(),
        "file_counts": {k: len(v) for k, v in file_counts.items()},
        "summary": {
            "high": len([f for f in findings if f["severity"] == SEV_HIGH]),
            "medium": len([f for f in findings if f["severity"] == SEV_MED]),
            "low": len([f for f in findings if f["severity"] == SEV_LOW]),
        },
        "findings": findings,
    }, ensure_ascii=False, indent=2)


# ── 主程式 ───────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TeacherOS 跨平台相容性檢查",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="只檢查高風險（🔴）規則",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="JSON 格式輸出",
    )
    parser.add_argument(
        "files", nargs="*",
        help="指定檢查的檔案（省略則全 Repo 掃描）",
    )
    args = parser.parse_args()

    repo_root = get_repo_root()

    # 收集檔案
    if args.files:
        target = Path(args.files[0]).resolve()
        file_dict = collect_files(repo_root, target)
    else:
        file_dict = collect_files(repo_root)

    # 執行規則
    findings = []
    findings.extend(check_rule1_hardcoded_paths(file_dict, repo_root))

    if not args.quick:
        findings.extend(check_rule2_platform_commands(file_dict, repo_root))
        findings.extend(check_rule3_unmigrated_shell(file_dict, repo_root))
        findings.extend(check_rule4_python_env(file_dict, repo_root))
        findings.extend(check_rule5_hooks(file_dict, repo_root))
        findings.extend(check_rule6_gitattributes(repo_root))

    # 輸出
    if args.json_output:
        print(format_json(findings, file_dict))
    else:
        print(format_report(findings, file_dict, repo_root))

    # Exit code
    has_high = any(f["severity"] == SEV_HIGH for f in findings)
    sys.exit(1 if has_high else 0)


if __name__ == "__main__":
    main()
