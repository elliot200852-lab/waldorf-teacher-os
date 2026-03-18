---
name: teach-animation
description: 用 Revideo（Motion Canvas fork）快速生成教學動畫。概念解說、時間線、流程圖、標題動畫。輕量快速，與 Remotion 影片製作互補。
triggers:
  - 教學動畫
  - 做動畫
  - 做一段動畫
  - 概念動畫
  - 解說動畫
  - 概念視覺化
  - timeline 動畫
  - 流程圖動畫
  - animate
  - teach animation
  - 做一段教學影片給學生看
  - 視覺化這個概念
requires_args: false
---

# skill: teach-animation — 教學動畫生成（Revideo）

用 Revideo（Motion Canvas fork，支援 headless CLI 渲染）快速生成教學動畫。
適用場景：概念解說、歷史時間線、流程圖、因果關係圖、課堂標題動畫。

> **與 video skill 的分工：**
> - `video`（Remotion）= 完整影片製作工作室。有 Studio 預覽、HMR 修改循環、React 元件架構。適合農場紀錄片、學期回顧等複雜作品。
> - `teach-animation`（Revideo）= 快速動畫生成器。TypeScript generator function + `yield*`，輕量流程。適合概念視覺化、課堂素材。
>
> **簡單判斷：** 需要預覽循環與複雜剪輯 → video。需要快速生成概念動畫 → teach-animation。
> **不觸發的詞：** 「做影片」「製作影片」「video」→ 歸 video skill。

## 前置需求

- Node.js >= 16
- FFmpeg

確認安裝：

**macOS / Linux：**
```bash
command -v node && command -v ffmpeg
```

**Windows（PowerShell）：**
```powershell
Get-Command node; Get-Command ffmpeg
```

若 FFmpeg 未安裝：

**macOS：**
```bash
brew install ffmpeg
```

**Windows（PowerShell）：**
```powershell
winget install Gyan.FFmpeg
# 或
choco install ffmpeg
```

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：`git rev-parse --show-toplevel`。

## 執行步驟

### Step 1 — 解析請求

從教師輸入中解析：

- **影片類型**：concept（概念解說動畫）/ material（課堂素材影片）/ custom（自訂）
- **主題與內容**：要視覺化的概念、流程、時間線、文字
- **語言**：預設繁體中文，英文素材保留英文
- **時長偏好**：若未指定，概念動畫 30-90 秒，素材影片 15-45 秒

### Step 2 — 確認或初始化專案

Revideo 工作目錄位於 Repo 外部（不進 Git）。

**macOS / Linux：**
```bash
REVIDEO_DIR="$HOME/revideo-workspace"

if [ ! -d "$REVIDEO_DIR" ]; then
  mkdir -p "$REVIDEO_DIR"
  cd "$REVIDEO_DIR"
  npm init @revideo@latest -- --default
  cd revideo-project
  npm install
fi
```

**Windows（PowerShell）：**
```powershell
$REVIDEO_DIR = "$env:USERPROFILE\revideo-workspace"

if (-not (Test-Path $REVIDEO_DIR)) {
  New-Item -ItemType Directory -Force -Path $REVIDEO_DIR
  Set-Location $REVIDEO_DIR
  npm init @revideo@latest -- --default
  Set-Location revideo-project
  npm install
}
```

若專案已存在，直接進入 Step 3。

### Step 3 — 生成場景檔案

在 `src/scenes/` 下建立新的 `.tsx` 場景檔案。命名規則：`{日期}-{主題簡稱}.tsx`

**必須遵守的程式碼規範：**

```tsx
// 所有 import 來自 @revideo，不是 @motion-canvas
import {Txt, Rect, Circle, Line, Img, makeScene2D} from '@revideo/2d';
import {
  all, chain, sequence, waitFor, createRef, createSignal,
  easeInOutCubic, easeOutBack, useScene
} from '@revideo/core';

export default makeScene2D(function* (view) {
  // animation logic here
});
```

**華德福動畫設計原則：**

1. **節奏感**：動畫的出現與消失要有呼吸節奏，避免突然出現/消失。每個元素至少 0.3 秒過渡
2. **色彩**：使用溫暖、自然的色調。避免螢光色和過度飽和。推薦色板：
   - 背景：`#1a1a2e`（深藍黑）或 `#faf3e0`（暖白）
   - 主色：`#e07a5f`（暖橘）、`#3d5a80`（藍灰）、`#81b29a`（草綠）
   - 強調：`#f2cc8f`（暖黃）、`#e76f51`（亮橘）
3. **文字**：中文使用 `fontFamily: 'Noto Sans TC'`，英文可用系統預設。字級不小於 36px
4. **空間**：留白充足，不要把畫面塞滿。一個畫面最多 3-4 個視覺元素
5. **流向**：資訊從左到右、從上到下，符合閱讀直覺

**常用動畫模式：**

```tsx
// fade in
yield* element().opacity(1, 0.5);

// slide in from left
element().position.x(-800);
yield* element().position.x(0, 0.8, easeOutBack);

// parallel animations
yield* all(
  title().opacity(1, 0.5),
  title().position.y(-50, 0.5),
);

// sequential animations
yield* chain(
  step1(),
  waitFor(0.3),
  step2(),
);

// staggered sequence (0.2s interval)
yield* sequence(0.2,
  item1().opacity(1, 0.4),
  item2().opacity(1, 0.4),
  item3().opacity(1, 0.4),
);
```

### Step 4 — 更新專案設定

更新 `src/project.ts` 指向新場景：

```tsx
import {makeProject} from '@revideo/core';
import newScene from './scenes/{scene-filename}?scene';

export default makeProject({
  scenes: [newScene],
});
```

### Step 5 — 預覽（可選）

若教師希望預覽再渲染：

**macOS / Linux / Windows（通用）：**
```bash
cd "$REVIDEO_DIR/revideo-project" && npm start
```

瀏覽器開啟後可檢視動畫。確認無誤後進入 Step 6。

若教師信任 AI 產出或趕時間，可跳過預覽直接渲染。

### Step 6 — 渲染

確認或更新 `src/render.ts`：

```tsx
import {renderVideo} from '@revideo/renderer';

async function render() {
  console.log('Rendering video...');
  const file = await renderVideo({
    projectFile: './src/project.ts',
    settings: {logProgress: true},
  });
  console.log(`Rendered video to ${file}`);
}

render();
```

執行渲染：

**macOS / Linux / Windows（通用）：**
```bash
cd "$REVIDEO_DIR/revideo-project" && npm run render
```

> Windows 中 `$REVIDEO_DIR` 替換為 `$env:USERPROFILE\revideo-workspace`。

輸出檔案預設在 `./output/` 資料夾。

### Step 7 — 交付

將輸出的 .mp4 複製到教師桌面或指定位置：

**macOS / Linux：**
```bash
cp ./output/*.mp4 ~/Desktop/
```

**Windows（PowerShell）：**
```powershell
Copy-Item .\output\*.mp4 "$env:USERPROFILE\Desktop\"
```

告知教師：檔案位置、解析度、時長、檔案大小。

若教師要上傳 Google Drive，使用 gws CLI 或銜接 drive 技能。

## 影片類型模板

### 概念解說動畫（concept）

適用：歷史時間線、抽象概念視覺化、因果關係圖、比較分析

典型結構：
1. 標題進場（1-2 秒）
2. 核心概念逐步展開（主體）
3. 關係/連結線出現（強調邏輯）
4. 總結畫面（2-3 秒）
5. 淡出

### 課堂素材影片（material）

適用：課堂開場標題、活動轉場、重點提示卡、每日金句

典型結構：
1. 背景色/圖案淡入
2. 主文字動畫進場
3. 副文字或裝飾元素
4. 停留展示（3-5 秒）
5. 淡出或轉場

## 參數化影片（差異化教學用）

Revideo 支援透過 variables 傳入動態內容，適合批次生成：

```tsx
// read variables in scene
const studentName = useScene().variables.get('name', 'student')();
const topic = useScene().variables.get('topic', 'today topic')();
```

```tsx
// pass variables at render time
await renderVideo({
  projectFile: './src/project.ts',
  variables: {name: 'Student A', topic: 'Post-war Taiwan'},
  settings: {logProgress: true},
});
```

這對差異化教學特別有用——同一模板可以為不同學生生成個人化版本。

## 注意事項

- Revideo 的 import 路徑是 `@revideo/2d` 和 `@revideo/core`，**不是** `@motion-canvas`
- 中文字型需確認系統已安裝 Noto Sans TC 或其他中文字型
- 本機渲染速度通常快於即時（1 分鐘影片渲染不到 1 分鐘）
- 所有 Motion Canvas 的教學和範例都適用，只需替換 import 路徑
- 影片預設解析度 1920x1080，30fps，可在 project.meta 中調整
- 如果需要加入背景音樂或語音，使用 `<Audio>` 元件並將檔案放在 `/public` 資料夾
- 不處理影片剪輯或轉檔——那是 FFmpeg 的工作

## 除錯

- `npm run render` 失敗 → 先跑 `npm start` 在瀏覽器確認動畫正確，再嘗試 headless 渲染
- 中文不顯示 → 確認字型安裝：
  - macOS / Linux：`fc-list | grep -i noto`
  - Windows：`Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' | Select-String 'Noto'`
- FFmpeg 相關錯誤 → 確認 FFmpeg 已安裝（見前置需求）
- 渲染卡住 → 檢查場景是否有無限迴圈或缺少 `yield*`

## 跨平台對照表

| Step | 有終端指令？ | macOS / Linux | Windows（PowerShell） | 狀態 |
|------|-----------|--------------|---------------------|------|
| 前置需求（FFmpeg 確認） | 有 | `command -v ffmpeg` | `Get-Command ffmpeg` | OK |
| 前置需求（FFmpeg 安裝） | 有 | `brew install ffmpeg` | `winget install Gyan.FFmpeg` | OK |
| Step 2（專案初始化） | 有 | `mkdir -p` + `cd` | `New-Item -ItemType Directory -Force` + `Set-Location` | OK |
| Step 3（場景檔寫入） | 無 | AI Write tool | AI Write tool | OK |
| Step 4（設定更新） | 無 | AI Edit tool | AI Edit tool | OK |
| Step 5（預覽） | 有 | `npm start` | `npm start` | OK（通用） |
| Step 6（渲染） | 有 | `npm run render` | `npm run render` | OK（通用） |
| Step 7（交付複製） | 有 | `cp` | `Copy-Item` | OK |
| 除錯（字型檢查） | 有 | `fc-list \| grep noto` | `Get-ItemProperty ... \| Select-String` | OK |
