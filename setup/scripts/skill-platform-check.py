#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — Skill 跨平台檢查
# 路徑：setup/scripts/skill-platform-check.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 功能：掃描技能 .md 檔案，檢查是否有 bash code block
#       缺少對應的 PowerShell 版本。僅輸出黃色警告，不攔截。
#
# 用法：
#   1. 指定 commit range（opening 技能呼叫）：
#      python3 skill-platform-check.py --range abc1234..def5678
#
#   2. 指定檔案（手動檢查）：
#      python3 skill-platform-check.py file1.md file2.md
#
#   3. 無引數（嘗試 ORIG_HEAD..HEAD，供 post-merge hook 使用）：
#      python3 skill-platform-check.py

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ── ANSI 顏色 ─────────────────────────────────────────

YELLOW = "\033[1;33m"
DIM = "\033[0;90m"
NC = "\033[0m"

# ── 平台專屬指令偵測規則 ──────────────────────────────
# 來源：ai-core/reference/cross-platform.yaml skill_writing_rules
# 這些指令出現在 ```bash 區塊中時，必須有對應的 ```powershell 區塊

PLATFORM_SPECIFIC_PATTERNS = [
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


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return Path.cwd()
    return Path(result.stdout.strip())


def get_skill_files_from_range(repo_root: Path, commit_range: str) -> list[Path]:
    """從 commit range 找出變動的技能 .md 檔案。"""
    result = subprocess.run(
        [
            "git", "diff", "--name-only", "--diff-filter=ACMR",
            commit_range, "--",
            "ai-core/skills/*.md",
            "workspaces/*/skills/*.md",
        ],
        capture_output=True, text=True, cwd=str(repo_root),
    )
    if result.returncode != 0:
        return []

    files = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if line:
            p = repo_root / line
            if p.is_file():
                files.append(p)
    return files


def get_skill_files_from_orig_head(repo_root: Path) -> list[Path]:
    """從 ORIG_HEAD..HEAD 找出變動的技能 .md 檔案（post-merge hook 用）。"""
    orig_head_file = repo_root / ".git" / "ORIG_HEAD"
    if not orig_head_file.is_file():
        return []

    orig_head = orig_head_file.read_text(encoding="utf-8").strip()
    if not orig_head:
        return []

    return get_skill_files_from_range(repo_root, f"{orig_head}..HEAD")


def parse_code_blocks(content: str) -> list[dict]:
    """
    解析 Markdown 中的 fenced code block。
    回傳 [{"lang": "bash", "code": "...", "line": 行號}, ...]
    """
    blocks = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^```(\w*)\s*$", lines[i])
        if m:
            lang = m.group(1).lower()
            start_line = i + 1
            code_lines = []
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "lang": lang,
                "code": "\n".join(code_lines),
                "line": start_line,
            })
        i += 1
    return blocks


def find_step_for_line(content: str, target_line: int) -> str:
    """找出某行所屬的 Step 標題。"""
    lines = content.split("\n")
    current_step = "(frontmatter)"
    for i, line in enumerate(lines):
        m = re.match(r"^###\s+(Step\s+\d+.*)", line)
        if m:
            current_step = m.group(1).strip()
        if i + 1 >= target_line:
            break
    return current_step


def check_skill_file(filepath: Path) -> list[str]:
    """
    檢查單一技能檔案的跨平台相容性。
    回傳警告訊息列表（可能為空）。
    """
    content = filepath.read_text(encoding="utf-8")
    blocks = parse_code_blocks(content)
    warnings = []

    bash_blocks = [b for b in blocks if b["lang"] in ("bash", "sh")]
    ps_blocks = [b for b in blocks if b["lang"] in ("powershell", "ps1", "pwsh")]

    # 找出所有 Step 標題的行號，用於判斷兩個 block 是否在同一個 Step
    step_boundaries = []
    content_lines = content.split("\n")
    for i, line in enumerate(content_lines):
        if re.match(r"^###\s+Step\s+\d+", line):
            step_boundaries.append(i + 1)  # 1-based

    def same_step(line_a: int, line_b: int) -> bool:
        """判斷兩個行號是否在同一個 Step 區段內。"""
        step_a = 0
        step_b = 0
        for boundary in step_boundaries:
            if boundary <= line_a:
                step_a = boundary
            if boundary <= line_b:
                step_b = boundary
        return step_a == step_b

    for bb in bash_blocks:
        # 檢查是否有平台專屬指令
        found_specific = []
        for pattern, label in PLATFORM_SPECIFIC_PATTERNS:
            if re.search(pattern, bb["code"]):
                found_specific.append(label)

        if not found_specific:
            continue

        # 有平台專屬指令，檢查同一 Step 內是否有 PowerShell block
        has_ps_pair = any(
            same_step(bb["line"], ps["line"])
            for ps in ps_blocks
        )

        if not has_ps_pair:
            step = find_step_for_line(content, bb["line"])
            cmds = "、".join(found_specific)
            warnings.append(
                f"  第 {bb['line']} 行（{step}）：bash 區塊含 {cmds}，缺 PowerShell 對應"
            )

    return warnings


def run_check(files: list[Path], repo_root: Path) -> bool:
    """執行檢查並輸出結果。回傳 True 表示有警告。"""
    all_warnings: dict[str, list[str]] = {}
    for f in files:
        ws = check_skill_file(f)
        if ws:
            try:
                rel = str(f.relative_to(repo_root))
            except ValueError:
                rel = str(f)
            all_warnings[rel] = ws

    if not all_warnings:
        return False

    print()
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"{YELLOW}  技能跨平台檢查：發現缺少 Windows 支援{NC}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print()

    for filepath, ws in all_warnings.items():
        print(f"  {filepath}")
        for w in ws:
            print(w)
        print()

    print(f"  {DIM}修正方式：為每個 bash 區塊補上對應的 PowerShell 版本{NC}")
    print(f"  {DIM}參考規格：ai-core/reference/cross-platform.yaml{NC}")
    print(f"  {DIM}完整指引：ai-core/skills/README.md Step 2{NC}")
    print()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TeacherOS Skill 跨平台相容性檢查",
    )
    parser.add_argument(
        "--range",
        help="Git commit range（例：abc1234..def5678）",
    )
    parser.add_argument(
        "files", nargs="*",
        help="要檢查的技能 .md 檔案路徑",
    )
    args = parser.parse_args()

    repo_root = get_repo_root()

    if args.files:
        files = [Path(f) for f in args.files if Path(f).is_file()]
    elif args.range:
        files = get_skill_files_from_range(repo_root, args.range)
    else:
        files = get_skill_files_from_orig_head(repo_root)

    if not files:
        return

    run_check(files, repo_root)


if __name__ == "__main__":
    main()
