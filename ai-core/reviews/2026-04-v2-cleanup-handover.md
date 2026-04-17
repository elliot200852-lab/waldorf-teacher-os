---
aliases:
  - "Git Reset Handover"
title: TeacherOS Repo Deep Review & Git Reset — Handover
date: 2026-04-13
author: David + Claude Code
status: Phase 1-3 已完成，Phase 4 Git Reset 待排程
phase: Phase 3 GWS 解耦完成，Phase 4 Full Git Reset 待教師備份確認
---

# TeacherOS Repo Deep Review & Git Reset

## 目標

1. 清除歷史中的機密檔案（OAuth secrets、API keys）
2. 縮減 `.git` 目錄大小（627MB → 目標 50-80MB）
3. 清理工作目錄中錯放、冗餘、不應追蹤的檔案
4. 修復跨平台相容性問題（macOS/Windows 硬編碼路徑）
5. 將 GWS 從系統層級整合移除，改由教師自行在個人環境設定
6. 建立「一師一分支」架構，教師登入以 GitHub username 為主鍵

---

## 第一步：工作目錄清理（執行前準備）

### 1A. 機密檔案脫離追蹤

```bash
git rm --cached setup/gws-client-secret.json
```
檔案保留在本機，只是從 Git 追蹤中移除。

### 1B. 垃圾檔案清除

```bash
# .pyc 快取
git rm __pycache__/research_pipeline_v2.cpython-314.pyc
git rm setup/scripts/__pycache__/skill-platform-check.cpython-314.pyc

# .bak 備份
git rm "bases/my-pages-wiki/wiki/_overview-個人文件與對外文件.md.bak"
git rm "bases/my-pages-wiki/wiki/_overview-學校行政與活動.md.bak"
git rm "workspaces/Working_Member/Teacher_劉佳芳/projects/自動化寫會議紀錄/data/raw_notes/sample_meeting_1.txt.bak"

# error.log
git rm "workspaces/Working_Member/Teacher_林雅婷/projects/教學大綱及已完成工作本/error.log"

# 根目錄孤立檔案
git rm git-history.skill
git rm subject-lesson-45.skill
git rm root_files.txt

# 空檔案（未追蹤，直接刪除本機）
rm -f download.html

# Git History PDF（不需保留在 repo）
git rm "Git History/git-history_2026-03-29_v1.pdf"
```

### 1C. graphify 完整移除

graphify 工具不再使用，整個移除：

```bash
# 移除被追蹤的 graphify-out 目錄
git rm -r graphify-out/

# 移除 .claude 中的 graphify skill 入口
git rm -r .claude/skills/graphify/

# 移除 .agents 中的 graphify 定義（如存在）
git rm -rf .agents/skills/graphify/ 2>/dev/null
```

確認後也從 CLAUDE.md 中移除 graphify 相關段落。

### 1D. 歸位：根目錄資料夾

```bash
# 林詩閔的衝突指南歸位
mkdir -p "workspaces/Working_Member/Teacher_林詩閔/reference"
git mv "git-conflict-guide-林詩閔.html" "workspaces/Working_Member/Teacher_林詩閔/reference/"

# Git History（保留 .md，PDF 已在 1B 刪除）
mkdir -p "workspaces/Working_Member/Codeowner_David/reference/git-history"
git mv "Git History/git-history.md" "workspaces/Working_Member/Codeowner_David/reference/git-history/"
git mv "Git History/Gemini-AI-對系統架構師歷程的觀察與建議.md" "workspaces/Working_Member/Codeowner_David/reference/git-history/"
git mv "Git History/_pdf-config.md" "workspaces/Working_Member/Codeowner_David/reference/git-history/"
rmdir "Git History"

# David 個人文稿
git mv David-personal-asset-base "workspaces/Working_Member/Codeowner_David/personal-asset-base"

# 工程師交接文件
git mv Engineer_Reference "workspaces/Working_Member/Codeowner_David/reference/engineer-handoff"

# 網站展示
git mv 網站展示 "workspaces/Working_Member/Codeowner_David/showcase"
```

### 1E. 更新 .gitignore

在 `.gitignore` 末尾新增：

```gitignore
# GWS client secret
**/gws-client-secret.json

# 工具輸出
graphify-out/

# 備份與日誌
*.bak
*.log

# 孤立技能定義
*.skill

# Workspace 中的二進位文件（用 Google Drive 管理）
workspaces/**/*.docx
workspaces/**/*.xlsx
workspaces/**/*.pptx
```

### 1F. 移除 CLAUDE.md 中的 graphify 段落

從全域 `~/.claude/CLAUDE.md` 中刪除：
```
# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.
```

---

## 第二步：跨平台修復

### 2A. GWS 硬編碼路徑

**`.claude/scripts/gws-auth-check.py`**
```python
# 第 12 行，改為：
import shutil
GWS = shutil.which("gws") or "/opt/homebrew/bin/gws"

# 第 72、81 行，錯誤訊息改為：
# gws auth login（不帶絕對路徑）
```

**`publish/batch-docreview.py`**
```python
# 第 18 行，改為：
import shutil
PANDOC = shutil.which("pandoc") or "/opt/homebrew/bin/pandoc"

# 第 19 行，從 environment.env 讀取 email
```

### 2B. publish/build.sh 短期修復

在腳本開頭加入平台偵測（仿 setup-check.sh）：
- Google Drive 路徑依 `uname` 分 macOS / Windows
- `/tmp` 改為 `${TMPDIR:-/tmp}`

完整 Python 遷移另開 session。

### 2C. 技能檔案跨平台標注

| 技能 | 問題 | 修復 |
|------|------|------|
| art-in-teaching.md | `open` 指令 | 加 PowerShell `Start-Process` |
| beautify.md | `open` 指令 | 加 PowerShell `Start-Process` |
| yt-subtitle.md | `brew install` | 加 `winget` / `npm` 替代 |

---

## 第三步：GWS 系統解耦（2026-04-14 完成）

### 為什麼移除

GWS（Google Workspace CLI）整合在 TeacherOS 中造成以下 onboarding 摩擦：

1. **Node.js 依賴**：教師需先安裝 Node.js 才能裝 gws，增加安裝步驟
2. **OAuth test user 管理**：每位教師需手動加入 Google Cloud Console 的測試用戶清單
3. **跨平台安裝問題**：Windows 的 npm 全域安裝常遇權限問題
4. **系統複雜度**：SessionStart hook、opening Step 2.5、quick-start Check 4.5 皆為 GWS 服務

TeacherOS 的核心價值是備課與教學設計，不是工具鏈管理。GWS 是強大的工具，但它的安裝與認證應由教師自行在個人環境處理。

### 已移除的檔案

| 檔案 | 原用途 |
|------|--------|
| `ai-core/skills/gws-setup.md` | 系統級 GWS 安裝技能（277 行） |
| `.claude/skills/gws-setup/SKILL.md` | Claude Code 入口 |
| `.claude/commands/gws-setup.md` | Claude Code command 入口 |
| `.claude/scripts/gws-auth-check.py` | SessionStart hook（89 行） |
| `ai-core/skills/gws-bridge.md` | Cowork VM GWS 橋接 |
| `setup/gws-client-secret.json` | OAuth client 憑證 |
| `setup/token.json` | 認證 token |
| `.agents/workflows/gws-auth.md` | Agent 層認證流程 |

### 已修改的檔案

| 檔案 | 修改內容 |
|------|----------|
| `.claude/settings.local.json` | 移除 SessionStart gws-auth-check hook |
| `ai-core/skills/opening.md` | 移除 Step 2.5（GWS 連線檢查）、Step 4 GWS 行 |
| `ai-core/AI_HANDOFF.md` | 移除 gws-setup 觸發行、GWS 架構說明改為「教師自行設定」 |
| `ai-core/skills-manifest.md` | 移除 gws-setup 列 |
| `setup/quick-start.py` | 移除 Check 4.5（GWS 安裝段落） |
| `setup/teacher-guide.md` | GWS 段落改為「選配，自行設定」 |
| `setup/environment.env.example` | 移除 GWS_SERVICES 區段 |
| `workspaces/_template/teacheros-personal.yaml` | 移除 google_accounts 模板區塊 |
| `setup/add-teacher.py` | 移除 google_accounts 自動填入 |
| `ai-core/reference/gws-cli-guide.md` | 加「教師自行設定」頂部說明 |
| `ai-core/skills/add-teacher.md` | 移除 GWS 連接段落 |
| `ai-core/skills/drive-transfer.md` | fallback 改為「自行安裝」 |

### 已保留不動

- `ai-core/reference/gws-cli-guide.md` — AI runtime 指令參考，保留
- 所有 GWS 使用類技能（drive、send-email、calendar、sheets、docs-edit）— 保留
- 教師既有的 `teacheros-personal.yaml` 中 `google_accounts` 區塊 — 不碰
- David 個人的 `google_accounts` 設定 — 不碰

### 登入流程簡化

| 項目 | 舊流程 | 新流程 |
|------|--------|--------|
| 身份主鍵 | USER_EMAIL（environment.env） | GitHub username |
| 驗證機制 | email → acl.yaml → workspace → GWS check | GitHub username → acl.yaml → branch checkout |
| GWS 狀態 | opening Step 2.5 每次靜默檢查 | 不檢查，教師自行負責 |
| 報告 | 開機摘要含 GWS 行 | 開機摘要無 GWS 行 |

---

## 第四步：Full Git Reset（待排程）

### 為什麼改用 reset

原計畫使用 `git-filter-repo` 清洗歷史（見原始 Phase 3），但改用 full Git reset：

1. **結果相同**：兩種方式教師都需要重新 clone
2. **reset 更簡單**：不需處理 filter-repo 的 ref 重寫副作用
3. **更可預測**：新 repo 從乾淨工作樹開始，無隱藏風險
4. **徹底清除**：歷史中的機密不留任何痕跡，不需擔心 GitHub 90 天 object 暫存

### 執行步驟

```bash
# 1. 完整備份
cp -a /Users/Dave/Desktop/WaldorfTeacherOS-Repo \
      /Users/Dave/Desktop/WaldorfTeacherOS-Repo-BACKUP-$(date +%Y%m%d)

# 2. 清理 worktree
git worktree list
git worktree prune

# 3. 刪除過時本機分支
git branch -D claude/elastic-chaplygin 2>/dev/null
git branch -D claude/silly-williams 2>/dev/null
git branch -D claude/trusting-greider 2>/dev/null
git branch -D test/claude-teacher-simulation 2>/dev/null

# 4. 匯出乾淨工作樹（排除 .git）
mkdir ../WaldorfTeacherOS-Fresh
rsync -av --exclude='.git' . ../WaldorfTeacherOS-Fresh/

# 5. 初始化新 repo
cd ../WaldorfTeacherOS-Fresh
git init
git add -A
git commit -m "TeacherOS v2.0：乾淨起點（歷史已清洗）"

# 6. 推送到 GitHub（force push 覆蓋）
git remote add origin https://github.com/elliot200852-lab/waldorf-teacher-os.git
git push origin main --force

# 7. 驗證
du -sh .git  # 應大幅縮小
git log --oneline  # 應只有一筆 commit
```

### 驗證清單

- [ ] `.git` 大小 < 100MB
- [ ] 歷史中無 `*client_secret*`、`*gws-client-secret*`
- [ ] 歷史中無 > 5MB 的 blob
- [ ] 所有工作目錄檔案完整

---

## 第五步：憑證輪替（reset 後立即執行）

| 憑證 | 位置 | 動作 |
|------|------|------|
| OAuth client secret (teacheros-488909) | GCP Console | 重新產生（GWS 已從 repo 移除，此憑證僅供 David 個人使用） |
| OAuth client (project 80158452579) | GCP Console | 確認是否仍使用，停用或重新產生 |
| OAuth client (Teacher 林詩閔, project 211052561189) | GCP Console | 通知教師重新產生 |

environment.env 中的 LINE_CHANNEL_ACCESS_TOKEN 和 TCMB_API_KEY 從未被 commit，無需輪替。

---

## 第六步：一師一分支架構

### 分支命名

```
main                           -- 受保護，僅 David 可 merge
workspace/Teacher_林詩閔       -- 教師個人工作分支
workspace/Teacher_劉佳芳
workspace/Teacher_郭耀新
workspace/Teacher_林雅婷
workspace/Teacher_莊宜瑾
workspace/Teacher_張銘分
workspace/Teacher_張仁謙
workspace/Teacher_陳佩珊
workspace/Teacher_姜善迪
workspace/Teacher_李佳穎
workspace/Teacher_謝岷樺
workspace/Teacher_陳啟華
workspace/Teacher_王琬婷
workspace/Codeowner_David      -- David 選用
```

### 建立分支

```bash
for teacher in Teacher_林詩閔 Teacher_劉佳芳 Teacher_郭耀新 Teacher_林雅婷 Teacher_莊宜瑾 Teacher_張銘分 Teacher_張仁謙 Teacher_陳佩珊 Teacher_姜善迪 Teacher_李佳穎 Teacher_謝岷樺 Teacher_陳啟華 Teacher_王琬婷; do
  git branch "workspace/$teacher" main
  git push origin "workspace/$teacher"
done
```

### GitHub Branch Protection（main）

- 禁止直接 push（除 David）
- 需要 PR + CODEOWNER 審核
- 不允許 bypass

### 需修改的系統檔案

| 檔案 | 修改內容 |
|------|----------|
| `ai-core/acl.yaml` | 每位教師加 `branch: workspace/Teacher_X` 欄位 |
| `ai-core/skills/opening.md` | Step 0/1.5 加分支檢查，teacher 以 GitHub username 識別 → 自動 checkout |
| `ai-core/skills/wrap-up.md` | push 目標改為教師分支 |
| `setup/scripts/pre-push-check.py` | 阻擋 teacher push 到 main |

### 教師通知範本

```
本週五進行系統維護，維護後你的舊資料夾將無法使用。
請在週四前確認所有工作已存檔（說「收工」即可）。

維護完成後請執行：
1. 刪除舊的 WaldorfTeacherOS-Repo 資料夾
2. 重新下載：git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git
3. 執行設定：bash setup/start.sh（Mac）或 .\setup\start.ps1（Windows）
4. 重新設定 environment.env（從 environment.env.example 複製）

如果你之前有使用 Google Workspace 功能（Drive 上傳、Calendar、Email），
你需要自行重新設定 gws CLI。請聯繫 David 取得說明。
```

---

## 架構決策記錄

### 決策 1：GWS 從系統解耦

**決定**：TeacherOS 不再統一管理 GWS 的安裝與認證。教師自行在個人 Claude Code 全域設定中配置。

**原因**：GWS 整合增加了 onboarding 複雜度（Node.js 依賴、OAuth test user 管理、跨平台安裝問題），但核心備課功能不依賴 GWS。系統應聚焦教學設計，不管工具鏈。

**影響**：GWS 使用類技能（drive、email、calendar 等）保留，但 fallback 從「說設定 gws」改為「請自行安裝」。AI runtime 指令參考（gws-cli-guide.md）保留。

### 決策 2：GitHub username 取代 email 作為主鍵

**決定**：登入身份識別以 GitHub username 為主鍵，email 為輔助。

**原因**：Email 有多種格式（noreply、school、personal），且不是 Git 操作的實際身份機制。GitHub username 是唯一的、與 repo 訪問權限直接綁定的身份標識。

**影響**：acl.yaml 將以 github_username 為 lookup key，opening Step 1.5 優先從 `.git/config` 或 `gh api user` 取得 username。

### 決策 3：Full Git reset 取代 filter-repo

**決定**：用新 repo init（乾淨工作樹 + 單一 commit）取代 git-filter-repo 歷史清洗。

**原因**：兩者最終結果相同（教師需重新 clone），但 reset 更簡單、更可預測，不會產生 filter-repo 的 ref 重寫副作用。歷史紀錄已另存於 Git History 文件中。

---

## 執行追蹤

| 步驟 | 狀態 | 完成日期 | 備註 |
|------|------|----------|------|
| 第一步：工作目錄清理 | 已完成 | 2026-04-14 | Phase 1A-1F，50 檔變更 |
| 第二步：跨平台修復 | 已完成 | 2026-04-14 | Phase 2A-2B，2C 已具備跨平台標注 |
| Commit + push 準備工作 | 已完成 | 2026-04-14 | 兩次 commit 均已 push |
| 第三步：GWS 系統解耦 | 已完成 | 2026-04-14 | 7 檔刪除、12 檔修改 |
| 第四步：Full Git Reset | 待排程 | — | 需確認所有教師已備份 |
| 第五步：憑證輪替 | 待排程 | — | reset 後立即 |
| 第六步：一師一分支 | 待排程 | — | reset 後 |
| 通知教師 | 待排程 | — | 分支建立後 |

---

## 風險與應對

1. **Full Git reset 後所有教師必須重新 clone** → 提前通知，週四前必須存檔
2. **教師有未 push 的工作** → 提前通知，wrap-up 存檔
3. **GWS 移除後已在使用 GWS 的教師需自行重新設定** → 在 reset 前通知，提供簡要步驟
4. **教師重新 clone 後設定遺失** → start.sh/ps1 會重新設定一切（GWS 除外）
