#!/usr/bin/env python3
"""Codeowner Inbox — 抓 GitHub issues + PRs，依優先級分類顯示。

用途：David 身為 codeowner，老師都在各自 workspace 分支工作看不見，
需要一個集中視圖看誰有 PR 待 review / 誰開了 issue / 有無 security 警報。

輸出：結構化 markdown-like 表格，AI 讀完後再補「建議優先動作」。
"""
import json
import subprocess
import sys
from datetime import datetime, timezone

ADMIN_LOGIN = "elliot200852-lab"


def gh(*args: str) -> str:
    r = subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[gh error] {' '.join(args)}\n{r.stderr}", file=sys.stderr)
        return ""
    return r.stdout


def fetch_issues():
    raw = gh(
        "issue", "list", "--state", "open", "--limit", "100",
        "--json", "number,title,author,labels,assignees,createdAt,updatedAt,url",
    )
    return json.loads(raw) if raw.strip() else []


def fetch_prs():
    raw = gh(
        "pr", "list", "--state", "open", "--limit", "100",
        "--json",
        "number,title,author,labels,assignees,createdAt,updatedAt,url,"
        "reviewDecision,isDraft,headRefName,mergeable,statusCheckRollup",
    )
    return json.loads(raw) if raw.strip() else []


def days_ago(iso: str) -> int:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).days


def classify_issue(issue):
    labels = {l["name"] for l in issue.get("labels", [])}
    assignees = [a["login"] for a in issue.get("assignees", [])]
    if labels & {"identity-violation", "security"}:
        return "security"
    if ADMIN_LOGIN in assignees:
        return "mine"
    if not assignees:
        return "unclaimed"
    return "others"


def classify_pr(pr):
    if pr.get("isDraft"):
        return "draft"
    author = (pr.get("author") or {}).get("login", "")
    review = pr.get("reviewDecision") or ""
    checks = pr.get("statusCheckRollup") or []
    failing = any(
        (c.get("conclusion") or c.get("state") or "") in ("FAILURE", "ERROR", "CANCELLED")
        for c in checks
    )
    if review == "APPROVED":
        return "approved"
    if review == "CHANGES_REQUESTED":
        return "waiting"
    if failing:
        return "ci_failing"
    if author == ADMIN_LOGIN:
        return "mine_author"
    return "need_review"


PR_PRIORITY = [
    ("approved", "A. 已批准，可合併"),
    ("need_review", "B. 等我 review"),
    ("ci_failing", "C. CI 失敗"),
    ("waiting", "D. 已要求修改，等對方"),
    ("mine_author", "E. 我自己開的"),
    ("draft", "F. 草稿"),
]

ISS_PRIORITY = [
    ("mine", "A. 指派給我"),
    ("security", "B. 安全通報（需審視是否真警報）"),
    ("unclaimed", "C. 未認領"),
    ("others", "D. 已指派給他人"),
]


def render_pr_line(pr):
    author = (pr.get("author") or {}).get("login", "?")
    age = days_ago(pr["updatedAt"])
    labels = ",".join(l["name"] for l in pr.get("labels", []))
    label_str = f" [{labels}]" if labels else ""
    title = pr["title"]
    if len(title) > 70:
        title = title[:67] + "…"
    return (
        f"  #{pr['number']:<4} {title}{label_str}\n"
        f"        {author} · {pr['headRefName']} · {age}d · {pr['url']}"
    )


def render_iss_line(iss):
    author = (iss.get("author") or {}).get("login", "?")
    age = days_ago(iss["updatedAt"])
    labels = ",".join(l["name"] for l in iss.get("labels", []))
    label_str = f" [{labels}]" if labels else ""
    title = iss["title"]
    if len(title) > 70:
        title = title[:67] + "…"
    return (
        f"  #{iss['number']:<4} {title}{label_str}\n"
        f"        {author} · {age}d · {iss['url']}"
    )


def main():
    print("━" * 42)
    print(f"  Codeowner Inbox — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("━" * 42)

    prs = fetch_prs()
    issues = fetch_issues()

    # ── PRs ──
    print()
    print(f"## Pull Requests（{len(prs)} 筆開啟）")
    if not prs:
        print("  （無）")
    else:
        by_cat = {}
        for pr in prs:
            by_cat.setdefault(classify_pr(pr), []).append(pr)
        for cat, label in PR_PRIORITY:
            if cat not in by_cat:
                continue
            print(f"\n### {label}")
            for pr in sorted(by_cat[cat], key=lambda p: p["updatedAt"], reverse=True):
                print(render_pr_line(pr))

    # ── Issues ──
    print()
    print(f"## Issues（{len(issues)} 筆開啟）")
    if not issues:
        print("  （無）")
    else:
        by_cat = {}
        for iss in issues:
            by_cat.setdefault(classify_issue(iss), []).append(iss)
        for cat, label in ISS_PRIORITY:
            if cat not in by_cat:
                continue
            print(f"\n### {label}")
            for iss in sorted(by_cat[cat], key=lambda i: i["updatedAt"], reverse=True):
                print(render_iss_line(iss))

    print()
    print("━" * 42)
    # 簡短統計供 AI 判斷是否需要建議動作
    need_action_prs = sum(
        1 for pr in prs if classify_pr(pr) in ("approved", "need_review", "ci_failing")
    )
    need_action_iss = sum(
        1 for iss in issues if classify_issue(iss) in ("mine", "security")
    )
    print(f"  需要你動作：PR {need_action_prs} · Issue {need_action_iss}")
    print("━" * 42)


if __name__ == "__main__":
    main()
