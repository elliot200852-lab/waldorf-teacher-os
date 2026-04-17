#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — Pre-commit 身份驗證 + 路徑攔截（Python 版）
# 路徑：setup/scripts/pre-commit-check.py
# 由 setup/hooks/pre-commit 薄層 shell 呼叫
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 作用：在 git commit 的瞬間，確認：
#   1. 當前使用者有登記在 ai-core/acl.yaml 中
#   2. 準備提交的檔案都在該使用者的 allowed_paths 範圍內
#   3. 任何 protected_always 的核心路徑修改都會被攔截
#
# 如有權限問題，請聯絡 David 更新 ai-core/acl.yaml。
#
# exit code: 0 = 通過, 1 = 攔截

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

# ── ANSI 顏色 ─────────────────────────────────────────

RED = "\033[0;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[0;32m"
NC = "\033[0m"


# ── 工具函式 ──────────────────────────────────────────

def git(*args: str) -> str:
    """執行 git 指令，回傳 stdout（去尾換行）。"""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:
        return ""


def matches(file_path: str, pattern: str) -> bool:
    """判斷檔案路徑是否符合 ACL pattern。"""
    if pattern == "*":
        return True
    # 目錄 prefix（pattern 以 / 結尾）
    if pattern.endswith("/"):
        return file_path.startswith(pattern)
    # 含萬用字元
    if "*" in pattern:
        return fnmatch.fnmatch(file_path, pattern)
    # 完全相符，或作為目錄前綴
    return file_path == pattern or file_path.startswith(pattern.rstrip("/") + "/")


# ── ACL 解析 ─────────────────────────────────────────

def parse_acl(acl_path: Path):
    """
    解析 acl.yaml，回傳 (teachers, protected_always, shared_writable)。
    teachers: { email: { is_admin, allowed_paths, name } }
    使用純 regex，不依賴 PyYAML。
    """
    content = acl_path.read_text(encoding="utf-8")
    teachers: dict = {}

    def register(email, gh_username, entry):
        teachers[email] = entry
        if gh_username:
            noreply = f"{gh_username}@users.noreply.github.com"
            teachers[noreply] = entry

    # ── 解析 admin 區塊 ──
    admin_m = re.search(r"admin:\s*\n(.*?)(?=\n\S|\Z)", content, re.DOTALL)
    if admin_m:
        admin_block = admin_m.group(0)
        emails = re.findall(r"email:\s*([^\s#\n]+)", admin_block)
        gh_users = re.findall(r"github_username:\s*([^\s#\n]+)", admin_block)
        for i, email in enumerate(emails):
            gh = gh_users[i].strip() if i < len(gh_users) else None
            entry = {"is_admin": True, "allowed_paths": ["*"], "name": "Admin"}
            register(email.strip(), gh, entry)

    # ── 解析 teachers 清單 ──
    for m in re.finditer(
        r"-\s+name:\s+(.+?)\n(?:.*?\n)*?\s+email:\s+([^\s#\n]+)"
        r"(?:.*?\n)*?\s+allowed_paths:\s*\n((?:\s+-[^\n]+\n)*)",
        content,
        re.DOTALL,
    ):
        name = m.group(1).strip()
        email = m.group(2).strip()
        paths_raw = m.group(3)
        paths = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", paths_raw)
        ]
        block_text = m.group(0)
        gh_m = re.search(r"github_username:\s*([^\s#\n]+)", block_text)
        gh = gh_m.group(1).strip() if gh_m else None
        if email not in teachers:
            entry = {"is_admin": False, "allowed_paths": paths, "name": name}
            register(email, gh, entry)

    # ── 解析 protected_always ──
    protected: list[str] = []
    pa_m = re.search(r"protected_always:\s*\n((?:\s+-[^\n]+\n)*)", content)
    if pa_m:
        protected = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", pa_m.group(1))
        ]

    # ── 解析 shared_writable ──
    shared: list[str] = []
    sw_m = re.search(r"shared_writable:\s*\n((?:\s+-[^\n]+\n)*)", content)
    if sw_m:
        shared = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", sw_m.group(1))
        ]

    return teachers, protected, shared


# ── HOME.md 品質護欄 ─────────────────────────────────

def _check_home_quality(staged_files: list[str], repo_root: Path) -> bool:
    """檢查 HOME.md 是否含有禁止字樣（如「自動收錄」）。
    讀取 git 暫存區的版本（非磁碟檔案），避免 untrack 後的誤判。
    回傳 True 表示應阻擋 commit。"""
    if "HOME.md" not in staged_files:
        return False

    # 讀暫存區版本（git show :HOME.md），若為刪除操作則無內容可查
    try:
        content = git("show", ":HOME.md")
    except Exception:
        return False

    if not content:
        return False  # 檔案正在被刪除，無需檢查

    if "自動收錄" in content:
        print()
        print(f"  {RED}[攔截] HOME.md 含有「自動收錄」字樣{NC}")
        print(f"  請移除所有含「自動收錄」的條目後再 commit。")
        print(f"  obsidian-sync 技能不應產生此字樣；若出現表示有 bug。")
        print()
        return True

    return False


# ── 大型二進位檔案攔截 ────────────────────────────────

WARN_SIZE = 3 * 1024 * 1024    # 3 MB → 警告
BLOCK_SIZE = 5 * 1024 * 1024   # 5 MB → 攔截

# 這些副檔名視為文字檔，不受大小攔截（.md 教案可能很長）
# 注意：.html 不列入豁免，因為可能嵌入 base64 圖片變得肥大；.pdf 也不豁免
TEXT_EXTENSIONS = {
    ".md", ".yaml", ".yml", ".json", ".txt", ".csv", ".tsv",
    ".py", ".js", ".ts", ".tsx", ".sh", ".ps1", ".bat",
    ".css", ".xml", ".env", ".gitignore",
}


def _check_large_files(staged_files: list[str], repo_root: Path) -> bool:
    """檢查暫存區中的大型二進位檔案。
    超過 5 MB 警告，超過 10 MB 攔截。
    回傳 True 表示應阻擋 commit。"""
    warnings = []
    blocked = []

    for f in staged_files:
        filepath = repo_root / f
        if not filepath.is_file():
            continue  # 已刪除的檔案跳過

        ext = filepath.suffix.lower()
        if ext in TEXT_EXTENSIONS:
            continue  # 文字檔不受限

        size = filepath.stat().st_size
        if size >= BLOCK_SIZE:
            blocked.append((f, size))
        elif size >= WARN_SIZE:
            warnings.append((f, size))

    if warnings:
        print()
        for f, size in warnings:
            print(f"  {YELLOW}[警告] 大型檔案 ({size/1024/1024:.1f} MB): {f}{NC}")
        print(f"  建議將大型二進位檔案放在 Google Drive，不進 git。")

    if blocked:
        print()
        print(f"  {RED}[攔截] 以下檔案超過 5 MB，不允許 commit：{NC}")
        for f, size in blocked:
            print(f"  {RED}  {size/1024/1024:.1f} MB: {f}{NC}")
        print()
        print(f"  請將大型檔案移至 Google Drive 或教師的 private/ 資料夾。")
        print(f"  如有疑問，請聯絡 David。")
        print()
        return True

    return False


# ── 地圖一致性警告 ────────────────────────────────────

def _check_map_consistency(staged_files: list[str]) -> None:
    """偵測 HOME.md 標頭異動或新目錄出現，警告地圖可能需更新。
    只是 advisory warning，不阻擋 commit。"""
    repo_root = Path(git("rev-parse", "--show-toplevel"))
    map_file = repo_root / "ai-core" / "reference" / "repo-structure-map.yaml"
    if not map_file.is_file():
        return  # 地圖不存在則跳過

    warnings = []

    # 1. HOME.md 的區段標題是否有異動
    if "HOME.md" in staged_files:
        try:
            old = git("show", "HEAD:HOME.md")
            new = (repo_root / "HOME.md").read_text(encoding="utf-8")
            old_headings = set(re.findall(r'^#{2,3} .+', old, re.MULTILINE))
            new_headings = set(re.findall(r'^#{2,3} .+', new, re.MULTILINE))
            added = new_headings - old_headings
            removed = old_headings - new_headings
            if added or removed:
                warnings.append("HOME.md 區段標題有異動，地圖的 sections 可能需更新")
        except Exception:
            pass

    # 2. 是否有新目錄 → 自動重建 tracked_directories
    # PyYAML 為選用依賴：缺失時跳過此檢查，不影響 ACL 驗證主流程
    try:
        import yaml
        data = yaml.safe_load(map_file.read_text(encoding="utf-8"))
        tracked = set(data.get("tracked_directories", []))
        has_new_dir = False
        for f in staged_files:
            parent = os.path.dirname(f)
            if parent and parent not in tracked:
                has_new_dir = True
                break
        if has_new_dir:
            # 自動重建 tracked_directories 並加入暫存區
            validate_script = repo_root / "setup" / "scripts" / "map-validate.py"
            if validate_script.is_file():
                import subprocess as _sp
                result = _sp.run(
                    [sys.executable, str(validate_script), "--rebuild-dirs"],
                    capture_output=True, text=True, cwd=str(repo_root)
                )
                if result.returncode == 0:
                    _sp.run(
                        ["git", "add", str(map_file)],
                        capture_output=True, text=True, cwd=str(repo_root)
                    )
                    warnings.append("偵測到新目錄，已自動重建 tracked_directories 並加入暫存")
                else:
                    warnings.append(f"新目錄偵測到但重建失敗：{result.stderr.strip()}")
    except Exception:
        pass  # PyYAML 缺失或其他錯誤 → 跳過

    if warnings:
        print()
        for w in warnings:
            print(f"  {YELLOW}[地圖提醒] {w}{NC}")


# ── 主流程 ────────────────────────────────────────────

def main() -> int:
    repo_root = Path(git("rev-parse", "--show-toplevel"))
    env_file = repo_root / "setup" / "environment.env"
    acl_file = repo_root / "ai-core" / "acl.yaml"

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  TeacherOS Pre-commit 身份與權限檢查")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # ── Step 1：雙重讀取身份 ──────────────────────────

    env_email = ""
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^USER_EMAIL=(.+)$", line.strip())
            if m:
                env_email = m.group(1).strip()
                break

    git_email = git("config", "user.email")

    # 以 environment.env 為主，git config 為備
    current_email = env_email or git_email

    if not current_email:
        print(f"{RED}[錯誤] 無法識別使用者身份。{NC}")
        print("請確認 setup/environment.env 中的 USER_EMAIL 欄位已填入。")
        print()
        return 1

    # 若兩者都有值但不一致，顯示警告
    if env_email and git_email and env_email != git_email:
        print(f"{YELLOW}[警告] 身份資訊不一致，以 environment.env 為準：{NC}")
        print(f"  environment.env  USER_EMAIL : {env_email}")
        print(f"  git config user.email       : {git_email}")
        print()

    print(f"  識別身份：{current_email}")

    # ── 分支偵測：非 main 分支警告 ──────────────────
    current_branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if current_branch and current_branch != "main":
        print()
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print(f"{YELLOW}  [警告] 你目前在分支「{current_branch}」，不是 main。{NC}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print()
        print("  TeacherOS 的所有工作應在 main 分支上進行。")
        print("  在分支上的 commit 可能導致同步問題。")
        print()
        print("  請切回 main 後再 commit：")
        print(f"    git checkout main")
        print(f"    git pull origin main")
        print()

        # 管理員可在分支工作（顯示警告但不攔截）
        # 先快速查 ACL 判斷是否為管理員
        _acl_file = repo_root / "ai-core" / "acl.yaml"
        _is_admin = False
        if _acl_file.is_file():
            _acl_text = _acl_file.read_text(encoding="utf-8")
            _admin_m = re.search(r"admin:\s*\n(.*?)(?=\n\S|\Z)", _acl_text, re.DOTALL)
            if _admin_m:
                _admin_emails = re.findall(r"email:\s*([^\s#\n]+)", _admin_m.group(0))
                _admin_ghs = re.findall(r"github_username:\s*([^\s#\n]+)", _admin_m.group(0))
                _all_admin = {e.strip() for e in _admin_emails}
                for gh in _admin_ghs:
                    _all_admin.add(f"{gh.strip()}@users.noreply.github.com")
                _is_admin = current_email in _all_admin

        if _is_admin:
            print(f"  {GREEN}管理員身份，允許在分支上操作。{NC}")
            print()
        else:
            print(f"  {RED}非管理員不允許在分支上 commit，已攔截。{NC}")
            print()
            return 1

    # ── Step 2：確認 ACL 與暫存檔案 ──────────────────

    if not acl_file.is_file():
        print(f"{YELLOW}[警告] 找不到 ai-core/acl.yaml，跳過權限檢查。{NC}")
        print("請聯絡 David 確認系統設定。")
        print()
        return 0

    staged_output = git("diff", "--cached", "--name-only")
    if not staged_output:
        print("  暫存區為空，無需檢查。")
        print()
        return 0

    staged_files = [f for f in staged_output.splitlines() if f.strip()]

    # ── Step 3：解析 ACL 並比對路徑 ──────────────────

    try:
        teachers, protected, shared = parse_acl(acl_file)
    except Exception as e:
        print(f"{YELLOW}[警告] ACL 檢查時發生錯誤，跳過路徑比對：{NC} {e}")
        print("請聯絡 David 確認 ai-core/acl.yaml 格式正確。")
        print()
        return 0

    # 現代 GitHub noreply 格式：{id}+{username}@users.noreply.github.com
    # 系統只註冊舊格式 {username}@users.noreply.github.com，需先映射再查
    if current_email not in teachers and "@users.noreply.github.com" in current_email:
        m_nr = re.match(r"\d+\+(.+)@users\.noreply\.github\.com$", current_email)
        if m_nr:
            alt_email = f"{m_nr.group(1)}@users.noreply.github.com"
            if alt_email in teachers:
                current_email = alt_email

    # 未知使用者
    if current_email not in teachers:
        print(f"{RED}[拒絕] 此帳號未登記於 acl.yaml：{NC} {current_email}")
        print("請聯絡 David，請他將你加入 ai-core/acl.yaml 後再操作。")
        print()
        return 1

    user = teachers[current_email]

    # 管理員通過（仍需通過品質護欄）
    if user["is_admin"]:
        print(f"  {GREEN}管理員身份確認，全域授權通過。{NC}")

        # 管理員也受品質護欄約束
        if _check_home_quality(staged_files, repo_root):
            return 1
        if _check_large_files(staged_files, repo_root):
            return 1

        # 地圖一致性警告
        _check_map_consistency(staged_files)

        print()
        return 0

    # ── Step 4：逐檔比對權限 ─────────────────────────

    blocked: list[tuple[str, str]] = []  # (type, filepath)
    for f in staged_files:
        is_protected = any(matches(f, p) for p in protected)
        is_allowed = (
            any(matches(f, p) for p in user["allowed_paths"])
            or any(matches(f, p) for p in shared)
        )
        if is_protected:
            blocked.append(("PROTECTED", f))
        elif not is_allowed:
            blocked.append(("BLOCKED", f))

    # 全部通過
    if not blocked:
        name = user["name"]
        print(f"  {GREEN}身份確認：{name}，所有修改在授權範圍內，通過。{NC}")

        # ── 品質護欄（阻擋 commit） ──────────────────
        if _check_home_quality(staged_files, repo_root):
            return 1
        if _check_large_files(staged_files, repo_root):
            return 1

        # ── 地圖一致性警告（不阻擋 commit） ──────────
        _check_map_consistency(staged_files)

        print()
        return 0

    # ── 有攔截 ───────────────────────────────────────

    print()
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"{RED}  [拒絕提交] 發現超出授權的檔案修改{NC}")
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print()

    for block_type, filepath in blocked:
        if block_type == "BLOCKED":
            print(f"  {RED}✗ 無操作權限：{NC} {filepath}")
        elif block_type == "PROTECTED":
            print(f"  {RED}✗ 受保護的核心路徑：{NC} {filepath}")

    print()
    print("你的授權範圍請查閱：ai-core/acl.yaml")
    print("如需擴充權限，請聯絡 David 更新 acl.yaml（需要 GitHub PR 審核）。")
    print()
    print("如有疑問，請聯絡 David（elliot200852@gmail.com）更新你的權限設定。")
    print()
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "TeacherOS Pre-commit 身份驗證與路徑權限檢查。\n"
            "由 setup/hooks/pre-commit 薄層 shell 呼叫，\n"
            "檢查 git 暫存區中的檔案是否在使用者的 ACL 授權範圍內。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "流程：\n"
            "  Step 1  從 environment.env + git config 讀取使用者身份\n"
            "  Step 2  確認 ai-core/acl.yaml 存在，取得暫存檔案清單\n"
            "  Step 3  解析 ACL（admin / teachers / protected_always / shared_writable）\n"
            "  Step 4  逐檔比對權限，輸出結果\n"
            "\n"
            "Exit codes:\n"
            "  0  通過（允許提交）\n"
            "  1  攔截（拒絕提交）\n"
            "\n"
            "如有權限問題，請聯絡 David 更新 ai-core/acl.yaml。"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
    sys.exit(main())
