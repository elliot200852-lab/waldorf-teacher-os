---
aliases:
  - "架構回顧"
---

# TeacherOS 架構審查報告
**日期：** 2026-03-04
**審查者：** AI（Claude）
**審查範圍：** 三層拆分後的完整架構一致性

---

## 一、本次重構總結

將原本「一個巨大 teacheros.yaml 兼任系統路由 + 教育哲學 + 教師身份」拆成三層：

| 層級 | 檔案 | 職責 | 誰讀 |
|------|------|------|------|
| 系統路由 | `ai-core/teacheros.yaml` | 載入順序、workspace 機制、session 協議、多 AI Agent 協調 | 所有 AI |
| 共用根基 | `ai-core/teacheros-foundation.yaml` | 華德福哲學、發展心理、課程原則、AI 使命、reference 觸發 | 所有 AI |
| 個人身份 | `{workspace}/teacheros-personal.yaml` | 教師個人信念、科目、偏好 | 該教師的 AI |

**同步更新的檔案：** AI_HANDOFF.md、skills/load.md、acl.yaml

---

## 二、一致性檢查結果

### PASS（已通過）

1. **載入順序三處一致** — teacheros.yaml `loading_sequence`、AI_HANDOFF.md 第一步、skills/load.md 讀取順序，三處完全對齊。

2. **ACL 保護清單** — `protected_always` 已加入 `teacheros-foundation.yaml` 和 `ai-core/reference/`，教師無法修改共用根基。

3. **Foundation 內容完整** — 十個章節涵蓋華德福哲學全貌，`_design_principles` 加厚版能驅動日常備課，`_load_when` 含通用觸發「任何課程設計」。

4. **Template 引導升級** — `_template/teacheros-personal.yaml` 已重寫為六段式引導，清楚告知教師「foundation 已處理什麼，你只需填什麼」。

5. **David 個人檔案瘦身** — 從約 350 行縮減至約 100 行，去除所有重複哲學內容，只保留個人信念與偏好。

6. **Reference 指向正確** — foundation 中四個 `reference_pointer` 都指向正確的 `ai-core/reference/` 路徑。

7. **DI 框架不受影響** — `_di-framework/project.yaml` 本來就是完整 inline 內容，每次必載，未受拆分影響。

### FAIL / 需要 David 處理

以下是我偵測到的漏洞與不一致，按優先級排列：

---

## 三、漏洞與行動清單

### P0 — 必須立即修正（會導致 AI 讀錯資料）

#### 3.1 三個 Skill 仍引用舊的身份讀取模式

**問題：** 以下 skill 仍寫著「管理者讀 `ai-core/teacheros.yaml`，教師讀 `{workspace}/teacheros-personal.yaml`」。新架構中 `teacheros.yaml` 已不含身份資訊，所有人（包括 Codeowner）的身份都在 `{workspace}/teacheros-personal.yaml`。

**受影響檔案：**
- `ai-core/skills/parent-letter.md`（第 39-41 行）
- `ai-core/skills/sync-cowork.md`（第 73-76 行）
- `ai-core/skills/pull-request.md`（第 38 行）

**修正方式：** 將「管理者：ai-core/teacheros.yaml / 教師：personal.yaml」統一改為「所有使用者：`{workspace}/teacheros-personal.yaml`（從 acl.yaml 取得 workspace 路徑）」。

#### 3.2 `workspaces/_template/philosophy.yaml` 已過時

**問題：** 此檔案標頭寫著「覆蓋 `ai-core/teacheros.yaml` 中對應的哲學欄位」。在新架構中，教師個人哲學已整合入 `teacheros-personal.yaml` 的 `subject_philosophies` 區塊，`philosophy.yaml` 完全多餘。

**修正方式：** 刪除 `workspaces/_template/philosophy.yaml`。若 David workspace 或其他 workspace 中有此檔案副本，也一併刪除。

---

### P1 — 應盡快處理（影響新教師體驗）

#### 3.3 `setup/add-teacher.sh` 需要驗證

**問題：** 此腳本會從 `_template/` 複製檔案到新教師 workspace。需確認：
- 是否會複製已過時的 `philosophy.yaml`（若是，刪除模板後此問題自動解決）
- 是否正確複製升級後的 `teacheros-personal.yaml`
- 是否正確處理 `workspace.yaml`

**修正方式：** David 手動跑一次 `add-teacher.sh` 模擬新教師加入，確認產出正確。

#### 3.4 只有 English 和 History 有 Reference 檔

**問題：** `ai-core/reference/` 目前只有 4 個檔案（pedagogy、student-development、subject-english、subject-history）。當教數學、藝術、科學等科目的教師加入時，沒有對應的 reference。

**修正方式：**
- 短期：在 `teacheros-foundation.yaml` 的 `subject_reference_index` 加入其他常見科目的 `_design_principles`（即使沒有完整 reference 檔，操作性摘要也能指導 AI）
- 中期：為新增科目撰寫完整 reference 檔案

#### 3.5 其他 Skill 的讀取步驟需全面掃描

**問題：** 除了 3.1 提到的三個 skill，其他 skill（如 `session-end.md`、`syllabus.md`、`lesson.md`、`ref.md` 等）可能也有引用舊模式的情況。

**修正方式：** 在所有 `ai-core/skills/*.md` 中搜尋「管理者」「Codeowner」關鍵字，統一更新為新的三層載入模式。

---

### P2 — 建議優化（提升系統健壯性）

#### 3.6 Foundation 中 DI 只有路徑指向，缺乏操作性摘要

**問題：** `teacheros-foundation.yaml` 第八章「差異化教學」只說了「見 _di-framework/project.yaml」，沒有像 pedagogy 和 student-development 那樣提供 `_design_principles`。DI 框架是每次必載的，所以影響不大，但如果 AI 在載入 DI framework 之前就開始設計課程，可能會漏掉雙軸要求。

**修正方式：** 在 foundation 的 `differentiated_instruction` 區塊加入一段操作性摘要，至少包含：「雙軸強制：學習優勢軸（視覺/聽覺/讀寫/動覺，每份設計至少涵蓋 2-3 種）+ 能力動機矩陣（A/B/C/D 四象限）。每份教學產出必須標示 DI 覆蓋情況。」

#### 3.7 `INSTRUCTIONS.template.md` 可能需要同步更新

**問題：** Cowork 模式使用的 `INSTRUCTIONS.template.md` 中的身份區塊編譯邏輯可能需要反映新架構。

**修正方式：** 檢查 `INSTRUCTIONS.template.md` 的 `COMPILE:IDENTITY` 區塊，確認編譯來源指向 `teacheros-personal.yaml` 而非舊的 `teacheros.yaml`。

#### 3.8 `workspace.yaml` 與 `teacheros-personal.yaml` 有重複欄位

**問題：** `workspace.yaml` 的 `teacher_identity` 區塊（name、teacher_id、role、email）與 `teacheros-personal.yaml` 的 `teacher_identity` 區塊完全重複。AI 不確定以哪個為準。

**修正方式：** 將 `workspace.yaml` 定位為純粹的「工作空間狀態追蹤」，移除 `teacher_identity` 區塊，只保留 `workspace_status`、`created_date`、`purpose`、`classes`。身份資訊統一由 `teacheros-personal.yaml` 提供。

---

## 四、給 David 的行動建議（按優先順序）

### 立即（今天）

1. **修正三個 Skill 的身份讀取路徑**（parent-letter、sync-cowork、pull-request）— 10 分鐘
2. **刪除 `workspaces/_template/philosophy.yaml`** — 1 分鐘

### 本週

3. **全面掃描所有 `ai-core/skills/*.md`**，統一載入模式為新三層架構
4. **跑一次 `add-teacher.sh` 模擬測試**，確認新教師 onboarding 流程正常
5. **在 foundation 的 DI 區塊加入操作性摘要**

### 系統持續發展

6. **為新科目撰寫 reference 檔案**（優先：數學、自然科學、藝術）
7. **清理 `workspace.yaml` 重複欄位**
8. **檢查 INSTRUCTIONS.template.md 編譯邏輯**
9. **建立「新教師第一次使用」測試腳本**——模擬完整流程：clone → add-teacher → 填寫 personal → load → 備課 → session-end

---

## 五、架構健康度評分

| 維度 | 評分 | 說明 |
|------|------|------|
| 職責分離 | 9/10 | 三層拆分清晰，每個檔案有明確的單一職責 |
| 載入順序一致性 | 9/10 | 三處文件已對齊，但 skill 層尚有殘留 |
| 教師隔離 | 10/10 | ACL + workspace + protected_always 構成三道防線 |
| 新教師引導 | 7/10 | Template 已升級，但需要實際測試 + 清理過時檔案 |
| Reference 覆蓋面 | 6/10 | 目前只覆蓋英文和歷史兩科 |
| Skill 系統一致性 | 6/10 | load.md 已更新，其他 skill 尚未同步 |
| 操作性摘要品質 | 9/10 | _design_principles 足以驅動日常備課設計 |

**總體：系統核心架構已完成升級，健壯且清晰。主要待修項集中在「周邊系統同步」（skill 層、模板清理、新科目覆蓋）。**

---

*審查完成：2026-03-04*
