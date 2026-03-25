#!/usr/bin/env python3
"""
TeacherOS Agent Sync Check
驗證多 AI agent 系統的完整性與一致性。

Usage:
    python3 ai-core/sync_check.py              # 僅檢查，輸出報告
    python3 ai-core/sync_check.py --auto-fix   # 檢查並自動修正問題
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

# --- 顏色輸出 ---
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def ok(msg):
    return f"  {GREEN}PASS{RESET}  {msg}"


def fail(msg):
    return f"  {RED}FAIL{RESET}  {msg}"


def warn(msg):
    return f"  {YELLOW}WARN{RESET}  {msg}"


def header(msg):
    return f"\n{BOLD}{CYAN}{'=' * 50}{RESET}\n{BOLD}{CYAN}{msg}{RESET}\n{BOLD}{CYAN}{'=' * 50}{RESET}"


def find_repo_root():
    """從腳本位置往上找到 repo root（含 .git 的目錄）"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    # fallback: 假設腳本在 ai-core/ 下
    return Path(__file__).resolve().parent.parent


def load_spec(repo_root):
    spec_path = repo_root / "ai-core" / "agent-sync-spec.yaml"
    if not spec_path.exists():
        print(fail(f"找不到 sync spec: {spec_path}"))
        sys.exit(1)
    with open(spec_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_frontmatter(filepath):
    """解析 .md 檔案的 YAML frontmatter"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def check_system_files(repo_root, spec):
    """檢查 1: 核心系統檔案是否存在"""
    results = []
    results.append(header("1. 核心系統檔案"))

    passes = 0
    fails = 0
    for filepath in spec.get("system_files", []):
        full_path = repo_root / filepath
        if full_path.exists():
            results.append(ok(filepath))
            passes += 1
        else:
            results.append(fail(f"{filepath} — 檔案不存在"))
            fails += 1

    return results, passes, fails


def check_skill_frontmatter(repo_root, spec):
    """檢查 2: Skill frontmatter 完整性"""
    results = []
    results.append(header("2. Skill Frontmatter 驗證"))

    skills_conf = spec.get("skills", {})
    canonical = repo_root / skills_conf.get("canonical_path", "ai-core/skills")
    required_fields = skills_conf.get("required_frontmatter", [])
    expected_skills = skills_conf.get("expected_skills", [])

    passes = 0
    fails = 0
    warnings = 0

    for skill_name in expected_skills:
        skill_file = canonical / f"{skill_name}.md"
        if not skill_file.exists():
            results.append(fail(f"{skill_name}.md — 檔案不存在"))
            fails += 1
            continue

        fm = parse_frontmatter(skill_file)
        if fm is None:
            results.append(fail(f"{skill_name}.md — 沒有 YAML frontmatter"))
            fails += 1
            continue

        missing = [f for f in required_fields if f not in fm]
        if missing:
            results.append(warn(f"{skill_name}.md — 缺少欄位: {', '.join(missing)}"))
            warnings += 1
        else:
            results.append(ok(f"{skill_name}.md — frontmatter 完整"))
            passes += 1

    # 檢查是否有未列入 spec 的 skill 檔案
    actual_skills = {
        p.stem for p in canonical.glob("*.md") if p.stem != "README"
    }
    expected_set = set(expected_skills)
    unlisted = actual_skills - expected_set
    if unlisted:
        for s in sorted(unlisted):
            results.append(warn(f"{s}.md — 存在於目錄但未列入 agent-sync-spec.yaml"))
            warnings += 1

    missing_files = expected_set - actual_skills
    # already reported above as FAIL

    return results, passes, fails, warnings


def check_claude_commands(repo_root, spec):
    """檢查 3: Claude commands 路由同步"""
    results = []
    results.append(header("3. Claude Commands 路由同步"))

    skills_conf = spec.get("skills", {})
    commands_path = repo_root / skills_conf.get("claude_commands_path", ".claude/commands")
    canonical = repo_root / skills_conf.get("canonical_path", "ai-core/skills")
    expected_skills = skills_conf.get("expected_skills", [])
    must_contain = spec.get("claude_command_format", {}).get("must_contain", "ai-core/skills/")

    passes = 0
    fails = 0
    warnings = 0
    fixes = []

    if not commands_path.exists():
        results.append(fail(f"{commands_path.relative_to(repo_root)} 目錄不存在"))
        return results, 0, 1, 0, []

    actual_commands = {p.stem for p in commands_path.glob("*.md")}
    expected_set = set(expected_skills)

    # 檢查每個 command 是否正確指向 canonical path
    for cmd_file in sorted(commands_path.glob("*.md")):
        try:
            content = cmd_file.read_text(encoding="utf-8")
        except Exception:
            results.append(fail(f"{cmd_file.name} — 無法讀取"))
            fails += 1
            continue

        if must_contain in content:
            results.append(ok(f"{cmd_file.name} — 正確路由至 ai-core/skills/"))
            passes += 1
        else:
            results.append(warn(f"{cmd_file.name} — 未包含 canonical 路徑引用"))
            warnings += 1

    # 檢查遺漏的 commands
    missing_commands = expected_set - actual_commands
    for skill_name in sorted(missing_commands):
        results.append(fail(f"{skill_name}.md — canonical skill 存在但 Claude command 遺漏"))
        fails += 1
        fixes.append(skill_name)

    # 檢查多餘的 commands
    extra_commands = actual_commands - expected_set
    for cmd_name in sorted(extra_commands):
        # 可能是 sync-agents 等新加的，不算 fail
        if (canonical / f"{cmd_name}.md").exists():
            results.append(ok(f"{cmd_name}.md — 額外 command，canonical skill 存在"))
            passes += 1
        else:
            results.append(warn(f"{cmd_name}.md — command 存在但無對應 canonical skill"))
            warnings += 1

    return results, passes, fails, warnings, fixes


def check_reference_modules(repo_root, spec):
    """檢查 4: Reference 知識模組"""
    results = []
    results.append(header("4. Reference 知識模組"))

    ref_conf = spec.get("reference_modules", {})
    ref_path = repo_root / ref_conf.get("path", "ai-core/reference")
    expected = ref_conf.get("expected_files", [])

    passes = 0
    fails = 0

    for filename in expected:
        full_path = ref_path / filename
        if full_path.exists():
            results.append(ok(filename))
            passes += 1
        else:
            results.append(fail(f"{filename} — 不存在"))
            fails += 1

    return results, passes, fails


def check_handoff_references(repo_root):
    """檢查 5: AI_HANDOFF.md 中的路徑引用"""
    results = []
    results.append(header("5. AI_HANDOFF.md 路徑引用"))

    handoff_path = repo_root / "ai-core" / "AI_HANDOFF.md"
    if not handoff_path.exists():
        results.append(fail("AI_HANDOFF.md 不存在"))
        return results, 0, 1, 0

    content = handoff_path.read_text(encoding="utf-8")

    # 抓取所有看起來像是檔案路徑的引用
    # 匹配 backtick 內的路徑 或 明確的檔案引用
    path_patterns = re.findall(r"`((?:ai-core|projects|workspaces)/[^`]+)`", content)
    # 也匹配直接寫的 .yaml / .md 路徑
    path_patterns += re.findall(
        r"((?:ai-core|projects|workspaces)/\S+\.(?:yaml|md|yml))", content
    )
    # 去重
    path_patterns = sorted(set(path_patterns))

    passes = 0
    fails = 0
    warnings = 0

    for ref_path in path_patterns:
        # 跳過含變數的路徑模板（如 {workspace}）
        if "{" in ref_path or "*" in ref_path:
            results.append(ok(f"{ref_path} — 模板路徑，跳過"))
            passes += 1
            continue

        full = repo_root / ref_path
        if full.exists():
            results.append(ok(ref_path))
            passes += 1
        else:
            results.append(warn(f"{ref_path} — 引用路徑不存在"))
            warnings += 1

    if not path_patterns:
        results.append(warn("未偵測到任何路徑引用"))
        warnings += 1

    return results, passes, fails, warnings


def check_manifest_consistency(repo_root, spec):
    """檢查 6: skills-manifest.md 與實際檔案一致性"""
    results = []
    results.append(header("6. Skills Manifest 一致性"))

    manifest_path = repo_root / "ai-core" / "skills-manifest.md"
    if not manifest_path.exists():
        results.append(fail("skills-manifest.md 不存在"))
        return results, 0, 1, 0

    content = manifest_path.read_text(encoding="utf-8")

    # 從 manifest 表格中提取 skill 名稱
    # 匹配 | `skill_name` | 或 ai-core/skills/name.md
    manifest_skills = set(re.findall(r"ai-core/skills/(\w[\w-]*)\.md", content))

    # 實際 skills 目錄
    skills_conf = spec.get("skills", {})
    canonical = repo_root / skills_conf.get("canonical_path", "ai-core/skills")
    actual_skills = {
        p.stem for p in canonical.glob("*.md") if p.stem != "README"
    }

    passes = 0
    fails = 0
    warnings = 0

    # manifest 有但檔案不存在
    missing_files = manifest_skills - actual_skills
    for s in sorted(missing_files):
        results.append(fail(f"{s} — manifest 列出但檔案不存在"))
        fails += 1

    # 檔案存在但 manifest 沒列
    unlisted = actual_skills - manifest_skills
    for s in sorted(unlisted):
        results.append(warn(f"{s} — 檔案存在但 manifest 未列出"))
        warnings += 1

    # 一致的
    consistent = manifest_skills & actual_skills
    for s in sorted(consistent):
        passes += 1

    if consistent:
        results.append(ok(f"{len(consistent)} 個 skills 與 manifest 一致"))

    return results, passes, fails, warnings


def auto_fix_commands(repo_root, spec, missing_commands):
    """自動建立遺漏的 Claude commands"""
    skills_conf = spec.get("skills", {})
    commands_path = repo_root / skills_conf.get("claude_commands_path", ".claude/commands")
    canonical_path = skills_conf.get("canonical_path", "ai-core/skills")
    repo_root_str = str(repo_root)

    changelog = []
    commands_path.mkdir(parents=True, exist_ok=True)

    for skill_name in missing_commands:
        # 讀取 canonical skill 的 frontmatter
        skill_file = repo_root / canonical_path / f"{skill_name}.md"
        fm = parse_frontmatter(skill_file)
        description = fm.get("description", "") if fm else ""

        # 取第一行作為簡短描述
        short_desc = description.split("。")[0] if description else skill_name

        cmd_content = (
            f"# /{skill_name} — {short_desc}\n\n"
            f"> Claude Code 薄層入口 — 技能正本：`{canonical_path}/{skill_name}.md`\n\n"
            f"讀取並執行 `{repo_root_str}/{canonical_path}/{skill_name}.md`。\n"
        )

        cmd_file = commands_path / f"{skill_name}.md"
        cmd_file.write_text(cmd_content, encoding="utf-8")
        changelog.append(f"- 新增 Claude command: .claude/commands/{skill_name}.md")

    return changelog


def write_changelog(repo_root, entries):
    """寫入 changelog"""
    changelog_path = repo_root / "ai-core" / "sync-changelog.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_entry = f"\n## {timestamp}\n\n" + "\n".join(entries) + "\n"

    if changelog_path.exists():
        existing = changelog_path.read_text(encoding="utf-8")
        content = existing.rstrip() + "\n" + new_entry
    else:
        content = "# TeacherOS Sync Changelog\n" + new_entry

    changelog_path.write_text(content, encoding="utf-8")
    return changelog_path


def main():
    parser = argparse.ArgumentParser(description="TeacherOS Agent Sync Check")
    parser.add_argument(
        "--auto-fix", action="store_true", help="自動修正可修正的問題"
    )
    parser.add_argument(
        "--pre-commit", action="store_true", help="由 pre-commit hook 呼叫（僅檢查，不修正）"
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    spec = load_spec(repo_root)

    print(f"\n{BOLD}TeacherOS Agent Sync Check{RESET}")
    print(f"Repo: {repo_root}")
    print(f"Spec: ai-core/agent-sync-spec.yaml v{spec.get('version', '?')}")

    all_results = []
    total_pass = 0
    total_fail = 0
    total_warn = 0
    fix_actions = []

    # 1. System files
    results, p, f = check_system_files(repo_root, spec)
    all_results.extend(results)
    total_pass += p
    total_fail += f

    # 2. Skill frontmatter
    results, p, f, w = check_skill_frontmatter(repo_root, spec)
    all_results.extend(results)
    total_pass += p
    total_fail += f
    total_warn += w

    # 3. Claude commands
    results, p, f, w, missing_cmds = check_claude_commands(repo_root, spec)
    all_results.extend(results)
    total_pass += p
    total_fail += f
    total_warn += w

    # 4. Reference modules
    results, p, f = check_reference_modules(repo_root, spec)
    all_results.extend(results)
    total_pass += p
    total_fail += f

    # 5. Handoff references
    results, p, f, w = check_handoff_references(repo_root)
    all_results.extend(results)
    total_pass += p
    total_fail += f
    total_warn += w

    # 6. Manifest consistency
    results, p, f, w = check_manifest_consistency(repo_root, spec)
    all_results.extend(results)
    total_pass += p
    total_fail += f
    total_warn += w

    # 輸出所有結果
    for line in all_results:
        print(line)

    # 總結
    print(header("Summary"))
    print(f"  {GREEN}PASS: {total_pass}{RESET}")
    if total_warn > 0:
        print(f"  {YELLOW}WARN: {total_warn}{RESET}")
    if total_fail > 0:
        print(f"  {RED}FAIL: {total_fail}{RESET}")
    else:
        print(f"  {RED}FAIL: 0{RESET}")

    # Auto-fix
    if args.auto_fix and (missing_cmds or total_fail > 0):
        print(header("Auto-Fix"))
        changelog_entries = []

        if missing_cmds:
            entries = auto_fix_commands(repo_root, spec, missing_cmds)
            changelog_entries.extend(entries)
            for e in entries:
                print(f"  {GREEN}FIXED{RESET}  {e[2:]}")  # strip "- "

        if changelog_entries:
            cl_path = write_changelog(repo_root, changelog_entries)
            print(f"\n  Changelog: {cl_path.relative_to(repo_root)}")
        else:
            print(f"  {YELLOW}沒有可自動修正的項目{RESET}")

    elif args.auto_fix:
        print(f"\n  {GREEN}系統完全一致，不需要修正。{RESET}")

    # Exit code
    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
