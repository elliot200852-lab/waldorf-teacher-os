#!/usr/bin/env python3
"""
TeacherOS Agent Sync Check
驗證多 AI agent 系統的完整性與一致性。

Usage:
    python3 ai-core/sync_check.py              # 僅檢查，輸出報告
    python3 ai-core/sync_check.py --auto-fix   # 檢查並自動修正問題
    python3 ai-core/sync_check.py --pre-commit # Pre-commit 精簡模式（只檢查 FAIL，靜默通過）
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

    manifest_path = repo_root / "ai-core" / "skills" / "skills-manifest.md"
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

    # manifest 有但檔案不存在（排除非技能的 .md）
    non_skill_names = {"README", "skills-manifest"}
    missing_files = manifest_skills - actual_skills - non_skill_names
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


def check_trigger_conflicts(repo_root, spec):
    """檢查 7: 技能觸發詞衝突檢測"""
    results = []
    results.append(header("7. 觸發詞衝突檢測"))

    skills_conf = spec.get("skills", {})
    canonical = repo_root / skills_conf.get("canonical_path", "ai-core/skills")
    expected_skills = skills_conf.get("expected_skills", [])

    # 蒐集所有技能的觸發詞
    trigger_map = {}  # trigger_word -> [skill_name, ...]
    for skill_name in expected_skills:
        skill_file = canonical / f"{skill_name}.md"
        if not skill_file.exists():
            continue
        fm = parse_frontmatter(skill_file)
        if fm is None or "triggers" not in fm:
            continue
        triggers = fm["triggers"]
        if not isinstance(triggers, list):
            continue
        for t in triggers:
            t_normalized = str(t).strip().lower()
            if t_normalized not in trigger_map:
                trigger_map[t_normalized] = []
            trigger_map[t_normalized].append(skill_name)

    passes = 0
    fails = 0
    warnings = 0

    # 找出有衝突的觸發詞（同一個詞觸發多個技能）
    conflicts = {
        t: skills for t, skills in trigger_map.items() if len(skills) > 1
    }

    if conflicts:
        for trigger, skills in sorted(conflicts.items()):
            # 覆蓋層（type: subject-overlay）與其引擎衝突是預期的，降為 WARN
            overlay_conflict = False
            for s in skills:
                sf = canonical / f"{s}.md"
                sfm = parse_frontmatter(sf)
                if sfm and sfm.get("type") == "subject-overlay":
                    overlay_conflict = True
                    break

            skill_list = ", ".join(skills)
            if overlay_conflict:
                results.append(
                    warn(f"「{trigger}」→ [{skill_list}]（覆蓋層與引擎重疊，預期行為）")
                )
                warnings += 1
            else:
                results.append(
                    fail(f"「{trigger}」→ [{skill_list}]（觸發詞衝突）")
                )
                fails += 1
    else:
        results.append(ok("所有觸發詞無衝突"))
        passes += 1

    # 統計
    unique_triggers = len(trigger_map)
    results.append(ok(f"共掃描 {unique_triggers} 個觸發詞，{len(expected_skills)} 個技能"))
    passes += 1

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


def get_staged_files():
    """取得 git 暫存區的檔案列表"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=5
        )
        return [f for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        return []


def run_pre_commit(repo_root, spec):
    """Pre-commit 精簡模式：只檢查 FAIL，靜默通過，與暫存區相關的項目優先"""
    staged = get_staged_files()
    fails = []

    # 永遠跑：核心系統檔案存在性（極快）
    for filepath in spec.get("system_files", []):
        if not (repo_root / filepath).exists():
            fails.append(f"核心檔案不存在：{filepath}")

    # 永遠跑：Reference 模組存在性（極快）
    ref_conf = spec.get("reference_modules", {})
    ref_path = repo_root / ref_conf.get("path", "ai-core/reference")
    for filename in ref_conf.get("expected_files", []):
        if not (ref_path / filename).exists():
            fails.append(f"Reference 模組不存在：{filename}")

    # 判斷是否涉及技能系統檔案
    skill_related_patterns = [
        "ai-core/skills/", ".claude/commands/",
        "ai-core/skills-manifest.md", "ai-core/AI_HANDOFF.md",
        "ai-core/agent-sync-spec.yaml"
    ]
    touches_skills = any(
        any(f.startswith(pat) or f == pat for pat in skill_related_patterns)
        for f in staged
    )

    if touches_skills:
        skills_conf = spec.get("skills", {})
        canonical = repo_root / skills_conf.get("canonical_path", "ai-core/skills")
        commands_path = repo_root / skills_conf.get(
            "claude_commands_path", ".claude/commands"
        )
        expected_skills = skills_conf.get("expected_skills", [])
        required_fields = skills_conf.get("required_frontmatter", [])

        # Check 2: 被暫存的 skill .md 的 frontmatter
        for skill_name in expected_skills:
            skill_file = canonical / f"{skill_name}.md"
            if not skill_file.exists():
                fails.append(f"技能檔案不存在：ai-core/skills/{skill_name}.md")
                continue
            # 只對有被暫存的檔案做 frontmatter 檢查
            rel_path = f"ai-core/skills/{skill_name}.md"
            if rel_path in staged:
                fm = parse_frontmatter(skill_file)
                if fm is None:
                    fails.append(f"{skill_name}.md 沒有 YAML frontmatter")
                else:
                    missing = [f for f in required_fields if f not in fm]
                    if missing:
                        fails.append(
                            f"{skill_name}.md 缺少必要欄位：{', '.join(missing)}"
                        )

        # Check 3: expected skills 是否都有對應的 command
        if commands_path.exists():
            actual_commands = {p.stem for p in commands_path.glob("*.md")}
            missing_cmds = set(expected_skills) - actual_commands
            for cmd in sorted(missing_cmds):
                # 只在對應的 skill 檔案存在時才報 FAIL
                if (canonical / f"{cmd}.md").exists():
                    fails.append(
                        f"技能 {cmd} 缺少 Claude command 入口"
                    )

        # Check 6: manifest 列出但檔案不存在（嚴重不一致）
        manifest_path = repo_root / "ai-core" / "skills" / "skills-manifest.md"
        if manifest_path.exists():
            content = manifest_path.read_text(encoding="utf-8")
            manifest_skills = set(
                re.findall(r"ai-core/skills/(\w[\w-]*)\.md", content)
            )
            actual_skills = {
                p.stem for p in canonical.glob("*.md") if p.stem != "README"
            }
            # 排除非技能的 .md（README、manifest 本身）
            non_skill_names = {"README", "skills-manifest"}
            ghost_skills = manifest_skills - actual_skills - non_skill_names
            for s in sorted(ghost_skills):
                fails.append(f"manifest 列出 {s} 但檔案不存在（幽靈條目）")

        # Check 7: 觸發衝突（被暫存的 skill 有新觸發詞時檢查）
        trigger_map = {}
        for skill_name in expected_skills:
            skill_file = canonical / f"{skill_name}.md"
            if not skill_file.exists():
                continue
            fm = parse_frontmatter(skill_file)
            if fm is None or "triggers" not in fm:
                continue
            triggers = fm.get("triggers", [])
            if not isinstance(triggers, list):
                continue
            for t in triggers:
                t_norm = str(t).strip().lower()
                if t_norm not in trigger_map:
                    trigger_map[t_norm] = []
                trigger_map[t_norm].append(skill_name)

        for trigger, skills in sorted(trigger_map.items()):
            if len(skills) > 1:
                # 覆蓋層衝突是預期的，不攔截
                is_overlay = False
                for s in skills:
                    sfm = parse_frontmatter(canonical / f"{s}.md")
                    if sfm and sfm.get("type") == "subject-overlay":
                        is_overlay = True
                        break
                if not is_overlay:
                    skill_list = ", ".join(skills)
                    fails.append(
                        f"觸發詞衝突「{trigger}」→ [{skill_list}]"
                    )

    # 輸出
    if fails:
        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  [sync-check] 系統一致性檢查未通過")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        for item in fails:
            print(f"  {RED}FAIL{RESET}  {item}")
        print()
        print("請修正以上問題後再 commit。")
        print("緊急繞過：git commit --no-verify")
        print()
        return 1
    # 全部通過：靜默
    return 0


def main():
    parser = argparse.ArgumentParser(description="TeacherOS Agent Sync Check")
    parser.add_argument(
        "--auto-fix", action="store_true", help="自動修正可修正的問題"
    )
    parser.add_argument(
        "--pre-commit", action="store_true",
        help="Pre-commit 精簡模式（只檢查 FAIL，靜默通過）"
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    spec = load_spec(repo_root)

    # Pre-commit 模式：精簡快速
    if args.pre_commit:
        sys.exit(run_pre_commit(repo_root, spec))

    # 正常模式：完整報告
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

    # 7. Trigger conflicts
    results, p, f, w = check_trigger_conflicts(repo_root, spec)
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
