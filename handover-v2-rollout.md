---
aliases:
  - "TeacherOS v2.0 Rollout Handover"
title: TeacherOS v2.0 全體老師重新上線 — Handover
date: 2026-04-17
author: David + Claude Code
status: Phase 4-6 已完成；Reclone Guide 已草擬；待通知與追蹤
phase: 通知教師階段（handover-git-cleanup.md 第六步末尾）
related:
  - handover-git-cleanup.md
  - setup/teacher-reclone-guide-2026-04.md
---

# TeacherOS v2.0 全體老師重新上線 — Handover

## 脈絡

接續 `handover-git-cleanup.md` 定義的六步清洗流程。前三步（工作目錄清理、跨平台修復、GWS 解耦）早於 2026-04-14 完成。本次對話處理後三步。

## 已完成

| 步驟 | 完成日期 | 對應證據 |
|------|----------|----------|
| 第四步：Full Git Reset | 2026-04-14~15 | 目前 HEAD `93d9012 TeacherOS v2.0：乾淨起點（歷史已清洗）` |
| 第五步：憑證輪替 | 2026-04-17 | David 自述完成（未在 repo 留痕，屬 GCP Console 側） |
| 第六步：一師一分支 | 2026-04-17 | `git ls-remote` 確認 13 個 `workspace/Teacher_XXX` 分支均已建立並推送 origin |
| 教師通知文件草擬 | 2026-04-17 | `setup/teacher-reclone-guide-2026-04.md`（約 700 行） |

## Reclone Guide 核心設計決策（已定案，勿反轉）

1. **老師不做備份**：David 這邊已統一備份（`~/Desktop/WaldorfTeacherOS-Repo-BACKUP-20260417-1518` 與 `~/Desktop/BACKUP-before-reset`）。指南內提醒「你放心刪」。
2. **Windows 先、Mac 後**：Part A = Windows，Part B = Mac（13 位老師中 Windows 使用者較多）。
3. **AI-first 支援模式**：教老師遇到問題**先把畫面貼給 AI / 餵整份指南給 AI**，不要第一時間傳訊息給 David。David 一對十三人，必須把自己當最後防線。詳見 guide 的 §1.6。
4. **Antigravity 原生支援**：多數老師在 Google Antigravity IDE 協作。C1 確認分支用 Antigravity 內建終端機（View → Terminal / Ctrl+`）；但 Part A/B 一次性重設定因涉及刪除與重建資料夾，建議先關掉 Antigravity、用外部 PowerShell/終端機。
5. **多行指令一行一行貼**：每個多行方框都拆成個別 code block，並明寫「N 行，一行一行貼，各按一次 Enter」，防止老師整塊貼上造成第二行被吃掉。

## 待執行

| 項目 | 負責 | 備註 |
|------|------|------|
| David 自讀一遍 guide | David | 依實際情境微調語氣 |
| 視需要請 1-2 位老師試跑 | David | 例如劉佳芳或林雅婷，找出語焉不詳處 |
| 決定發送管道 | David | LINE 群 / Email / 個別訊息 |
| 確定維護窗口時間 | David | 例：週五下班前所有老師完成 |
| 發送指南 | David | 可在訊息內夾帶指南連結或 PDF |
| 逐師追蹤完成狀況 | David | 建議做一張 13 人進度表 |
| 全員完成後關閉本 handover | David | 刪除此檔並 commit「收工」 |

## 風險與應對

1. **老師卡在 `gh auth login`** → Guide 內已有 fallback 指令；若老師從未裝過 `gh`，AI 可引導裝 GitHub CLI。
2. **老師 Git 身份 (`git config user.email`) 不在 `acl.yaml`** → Pre-push 會擋下，出現紅字 `author email 不在授權清單`。解法：請老師對 AI 貼錯誤訊息，AI 會教他們跑 `git config --global user.email <對應 email>`。
3. **老師誤在 `main` 分支 commit** → Pre-push hook 會阻擋。Guide Q1 已處理。
4. **Antigravity 開著舊資料夾被刪** → Guide Part A/B 開頭已警告先關 Antigravity。
5. **老師的 Google Workspace (gws) 連不上** → Guide Q2 指向 `ai-core/reference/gws-cli-guide.md`，AI 可引導重新設定。OAuth client 若需 David 在 GCP 開權限，才升級給 David。

## 下一個 session 從這裡接手

若切新對話或換 AI Agent：

1. 讀 `handover-git-cleanup.md`（母文件，六步清洗全貌）
2. 讀**本檔**（當前狀態）
3. 讀 `setup/teacher-reclone-guide-2026-04.md`（正式教師文件）
4. 依「待執行」表格接續工作

完成所有項目後，**刪除本檔**並 commit。`handover-git-cleanup.md` 是母文件，不刪。

---

*本檔屬於「active handover」——放在根目錄代表正在進行中的工作。工作結束即刪。*
