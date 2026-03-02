# TeacherOS — Workspace 個人工作區說明

> 本文件供 AI 與教師閱讀。AI 在 session_start 時若識別為 teacher 角色，
> 需確認該教師是否有 workspace，並啟用路徑覆寫路由邏輯。

---

## 什麼是 Workspace？

Workspace 是每位試用教師的**專屬沙盒**。

你可以在自己的 workspace 內：
- 建立個人版的框架覆寫（優先於系統標準版生效）
- 新增私人腳本、模板、哲學設定
- 自由堆疊你自己的備課結構
- 不影響任何其他老師的工作，也不影響 David 的系統核心

你在自己 workspace 內的 100% 操作都是被授權的，不需要擔心誤改他人資料。

---

## Workspace 的路徑覆寫邏輯

AI 在 teacher 角色的工作階段中，查找任何設定或模板檔案時，
**優先**從你的 workspace 尋找，找不到才退回系統標準版。

**範例：**
```
AI 需要  projects/_di-framework/project.yaml
         ↓
先找     workspaces/teacher-lin/_di-framework/project.yaml
         → 存在？使用你的個人覆寫版本
         → 不存在？使用系統標準版（Repo 根目錄）
```

這表示你可以只覆寫「你想改的那一部分」，其他部分自動沿用系統標準。

---

## 如何建立你的 Workspace？

1. 複製 `workspaces/_template/` 資料夾
2. 改名為你的識別 ID（建議與 acl.yaml 中的 `workspace` 欄位一致）
3. 開始在裡面建立你想要的結構

```
workspaces/
  _template/          ← 範本（複製這個）
  teacher-lin/        ← 林老師的 workspace（範例）
    README.md         ← 說明這個 workspace 是誰的
    philosophy.yaml   ← 個人教學哲學覆寫（選用）
    _di-framework/    ← 覆寫 DI 框架設定（選用）
    scripts/          ← 個人腳本（選用）
    templates/        ← 個人內容模板（選用）
```

---

## 重要說明

| 項目 | 說明 |
|------|------|
| 可見性 | 所有 workspace 在同一 Repo 中，其他老師可讀取你的 workspace，但無法修改 |
| 權限 | 你只能修改自己的 workspace 路徑（由 acl.yaml 的 `allowed_paths` 管控） |
| 核心系統 | `ai-core/`、`setup/hooks/`、`.github/` 等核心路徑永遠受保護 |
| Cherry-pick | David 若看見你的 workspace 中有好的設計，可能將其提升為全校標準 |

---

*維護者：David。最後更新：2026-03-02*
