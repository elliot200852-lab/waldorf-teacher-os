---
name: ref
description: 主動載入指定的Reference知識模組（教學哲學/英文/歷史/學生發展）。在課程設計或深度討論時主動觸發。
triggers:
  - 載入教學哲學
  - 看英文背景
  - ref
  - 載入背景知識
  - 人智學
requires_args: false
args_format: "[模組] (pedagogy/english/history/student/all) — 可選"
---

# skill: ref — Reference 知識模組載入

主動載入指定的 Reference 知識模組，並輸出摘要確認。
用於需要特定知識背景支援時（教學哲學、科目理念、學生發展）。

## 參數

模組關鍵字：`pedagogy` / `english` / `history` / `student` / `all`

若未提供，列出可用模組並詢問：
「請問要載入哪個 Reference 模組？（pedagogy / english / history / student / all）」

## 根目錄

`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`

## 模組對照表

| 關鍵字 | 路徑 | 包含內容 |
|--------|------|----------|
| `pedagogy` | `ai-core/reference/pedagogy-framework.yaml` | 人智學四體論、七年週期、七至九年級發展樣態、頭心手三元 |
| `english` | `ai-core/reference/subject-english.yaml` | 英文科哲學、語言即塑造力量、教師核心任務與角色 |
| `history` | `ai-core/reference/subject-history.yaml` | 歷史課意識演化邏輯、課程對應、台灣主體史觀 |
| `student` | `ai-core/reference/student-development.yaml` | 外骨骼 vs 內骨骼、學科作為隱藏鷹架、班級經營與修復式正義 |

## 執行步驟

### Step 1 — 讀取對應檔案

依參數讀取對應 reference 檔：

- `pedagogy` → `ai-core/reference/pedagogy-framework.yaml`
- `english` → `ai-core/reference/subject-english.yaml`
- `history` → `ai-core/reference/subject-history.yaml`
- `student` → `ai-core/reference/student-development.yaml`
- `all` → 以上全部（全部讀取完成後才輸出確認，合併為一次輸出）

### Step 2 — 輸出載入確認

讀取完成後，輸出：

---

**Reference 已載入：[模組名稱]**

**摘要**（從 `_summary` 欄位直接引用，若無則從內容中提取 2–3 句核心）

**本模組與目前工作的關聯**（1 句，簡述可以如何使用這個背景）

---

準備就緒。可以繼續工作。

### Step 3 — 等待指令

輸出確認後直接等待指令，不主動展開內容，不追問「你要做什麼」。

## 注意事項

- 讀取完成後不貼出完整 YAML 原文，只輸出摘要確認
- 若模組路徑不存在，回應：「[模組] 的 reference 檔案尚未建立，請聯絡 David。」
- `all` 模式下，四個模組全部讀取完成後才輸出確認
