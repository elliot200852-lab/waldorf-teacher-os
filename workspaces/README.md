# TeacherOS — Workspace 個人工作區說明

> 本文件供 AI 與教師閱讀。AI 在 session_start 時若識別為 teacher 角色，
> 需確認該教師是否有 workspace，並啟用路徑覆寫路由邏輯。

---

## 什麼是 Workspace？

Workspace 是每位教師的**專屬工作空間**。

你可以在自己的 workspace 內：
- 存放個人教學哲學設定（teacheros-personal.yaml）
- 管理你的所有班級專案（projects/class-{code}/）
- 自由堆疊你自己的備課結構
- 不影響任何其他老師的工作，也不影響 David 的系統核心

你在自己 workspace 內的 100% 操作都是被授權的，不需要擔心誤改他人資料。

---

## Workspace 命名規則

所有活躍教師的工作空間位於 `workspaces/Working_Member/` 下，
命名格式為 `{角色}_{真實姓名}`：

| 角色 | 命名範例 | 說明 |
|------|----------|------|
| 系統管理員 | `Codeowner_David` | 擁有合併權限 |
| 一般教師 | `Teacher_林信宏` | 標準教師身份 |

特殊命名（不套規則）：`工作範例參考/`（系統提供的完整範例）

---

## Workspace 結構總覽

```
workspaces/
  _template/                        ← 範本（由 add-teacher.sh 自動複製）
  工作範例參考/                      ← 完整的 Block 1-4 產出範例（唯讀參考）
  Working_Member/                    ← 所有活躍教師的工作空間
    Codeowner_David/                 ← David 的工作空間
      teacheros-personal.yaml
      workspace.yaml
      projects/
        class-9c/
        class-9d/
    Teacher_林信宏/                   ← 林老師的工作空間（範例）
      teacheros-personal.yaml
      workspace.yaml
      projects/
        class-8a/
```

---

## 三層內容模型

TeacherOS 採用「共享參考 → 範本複製 → 老師創作」的三層架構：

| 層級 | 來源 | 權限 |
|------|------|------|
| 第 1 層：共享參考 | ai-core/、projects/_di-framework/ | 所有老師可讀，只有 David 修改 |
| 第 2 層：範本複製 | teacheros-personal.yaml、workspace.yaml | 複製到 workspace 後自由修改 |
| 第 3 層：老師創作 | Block 1-4 產出的課程內容 | 完全屬於教師個人 |

---

## 如何建立你的 Workspace？

**你不需要手動建立。** David（管理員）會執行：

```bash
bash setup/add-teacher.sh
```

腳本會自動完成：
1. 收集你的資訊（姓名、Email、班級、科目）
2. 在 `workspaces/Working_Member/Teacher_{你的姓名}/` 建立工作空間
3. 複製範本檔案
4. 更新 `ai-core/acl.yaml` 授權

你只需要 `git pull` 就能取得自己的 workspace。

---

## 重要說明

| 項目 | 說明 |
|------|------|
| 可見性 | 所有 workspace 在同一 Repo 中，其他老師可讀取你的 workspace，但無法修改 |
| 權限 | 你只能修改自己的 workspace 路徑（由 acl.yaml 的 `allowed_paths` 管控） |
| 核心系統 | `ai-core/`、`setup/hooks/`、`.github/` 等核心路徑永遠受保護 |
| Cherry-pick | David 若看見你的 workspace 中有好的設計，可能將其提升為全校標準 |

---

*維護者：David。最後更新：2026-03-03*
