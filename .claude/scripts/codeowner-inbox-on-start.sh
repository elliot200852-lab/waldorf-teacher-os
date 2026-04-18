#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — SessionStart Hook：codeowner inbox 自動觸發
# 路徑：.claude/scripts/codeowner-inbox-on-start.sh
# 觸發者：Claude Code SessionStart（settings.json）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 設計：
#   - 只有 codeowner（admin）開機時執行 inbox.py，列出 GitHub 待辦
#   - 一般教師 silent exit，無任何副作用
#   - 輸出注入到 SessionStart 的 hook output，AI 在開機報告中呈現
#
# 失敗策略：任何子步驟失敗都 exit 0（不阻塞開機），最多在輸出加註提示。

set +e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[ -z "$REPO_ROOT" ] && exit 0

ENV_FILE="$REPO_ROOT/setup/environment.env"
ACL_FILE="$REPO_ROOT/ai-core/acl.yaml"
INBOX_SCRIPT="$REPO_ROOT/workspaces/Working_Member/Codeowner_David/scripts/inbox.py"

# ── 1. 讀取本機使用者 email ──────────────────────────
[ ! -f "$ENV_FILE" ] && exit 0

USER_EMAIL=$(grep '^USER_EMAIL=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d ' ')
[ -z "$USER_EMAIL" ] && exit 0

# ── 2. 比對 acl.yaml 的 admin email ─────────────────
[ ! -f "$ACL_FILE" ] && exit 0

ADMIN_EMAIL=$(python3 - <<PYEOF 2>/dev/null
import re
from pathlib import Path
acl = Path("$ACL_FILE").read_text(encoding="utf-8")
m = re.search(r"admin:\s*\n(.*?)(?=\n\S|\Z)", acl, re.DOTALL)
if m:
    emails = re.findall(r"email:\s*([^\s#\n]+)", m.group(0))
    if emails:
        print(emails[0].strip())
PYEOF
)

# 不是 admin → silent exit（其他教師不受影響）
[ "$USER_EMAIL" != "$ADMIN_EMAIL" ] && exit 0

# ── 3. codeowner 路徑：執行 inbox ───────────────────

# gh CLI 不可用 → 提示但不阻塞
if ! command -v gh >/dev/null 2>&1; then
    echo "[Codeowner Inbox] gh CLI 未安裝，跳過 inbox 觸發。"
    exit 0
fi

[ ! -f "$INBOX_SCRIPT" ] && exit 0

# 執行 inbox.py，輸出進入 SessionStart hook output
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Codeowner Inbox（開機自動載入）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 "$INBOX_SCRIPT" 2>&1 || {
    echo ""
    echo "  （inbox.py 執行失敗，跳過。手動檢查可執行 /inbox 技能。）"
}

exit 0
