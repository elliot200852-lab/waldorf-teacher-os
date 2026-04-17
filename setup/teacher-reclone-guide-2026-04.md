---
aliases:
  - "TeacherOS v2.0 重新上線指南"
  - "Reclone Guide 2026-04"
tags:
  - type/onboarding
  - season/spring
version: 2026-04
audience: 慈心華德福全體合作老師（13 人）
---

# TeacherOS v2.0 重新上線指南

## 寫在最前面：為什麼要做這一次？

這份文件是給已經在使用 TeacherOS 的老師。2026 年 4 月17日，我們把整個系統做了一次大整理：

- 歷史中的機密檔案（一些 Google 帳號的授權碼）被徹底清掉
- 每位老師現在有自己專屬的「工作分支」，不會互相覆蓋
- 資料夾結構變乾淨了，未來 onboarding 新老師會更快

**代價**：你電腦上舊的 TeacherOS 資料夾現在沒辦法再更新了。我們需要請你：

1. **刪除舊的資料夾**
2. **重新下載一份乾淨的**
3. **切換到你專屬的分支**
4. 做幾個設定確認

整個流程大概 20-30 分鐘。跟著做，不會有事。

> **備份 David 這邊已經統一做好了，你放心刪舊資料夾。**
> 你**不需要**自己另外做備份。

> **如果你跟著做到一半卡住，不要硬撐。**
> 把看到的畫面截圖拍下來以及把這整個說明檔餵給 AI，等回覆。
> 硬著頭皮往下，可能會把事情弄得更複雜。

---

## 你會用到的工具與名詞（先看過一次）

### 1. 「終端機」是什麼

終端機（Terminal / PowerShell）是一個黑底白字的視窗，你可以在裡面「打指令叫電腦做事」。

- **Windows 老師**：這個視窗叫做「PowerShell」
- **Mac 老師**：這個視窗叫做「終端機」（Terminal）

這份指南會告訴你**什麼時候該打開它**、**要貼什麼指令進去**。

### 1.5 如果你平常在 Google Antigravity IDE 裡工作

很多老師日常是在 **Google Antigravity IDE**（Gemini 的程式編輯器）裡跟 AI 協作。好消息是：

- **日常備課工作**：大多數指令你都**不需要自己下**，跟 AI 說「收工」「存檔」「載入 9c 英文」，AI 會自己處理。
- **需要自己動手的時候只有兩種**：
  1. **這次的重新上線**（Part A 或 Part B 的一次性設定）
  2. **每次工作前確認分支**（Part C1，三秒鐘的事）

這兩種情況，你**不用特別離開 Antigravity**——Antigravity 本身就內建一個終端機，打開方式：

- **上方選單**：`View` → `Terminal`（中文版：檢視 → 終端機）
- **或用快捷鍵**：按 **Ctrl + `**（backtick，Esc 鍵正下方、數字 1 鍵左邊那顆）

打開後會在 Antigravity 視窗下方多出一個小面板，跟 Mac 終端機 / Windows PowerShell 一樣可以貼指令、按 Enter。**指南裡說「貼到終端機 / PowerShell」的地方，在 Antigravity 內建終端機裡操作完全一樣**。

> **提醒**：Antigravity 的內建終端機在 Mac 上實際跑的是 `bash` 或 `zsh`（跟 Mac 終端機一樣），在 Windows 上實際跑的是 `PowerShell` 或 `Git Bash`。所以：
> - **Mac 的 Antigravity 老師**：請照 **Part B（Mac）** 的指令做
> - **Windows 的 Antigravity 老師**：請照 **Part A（Windows）** 的指令做
>
> 看你**作業系統**決定走 Part A 還是 Part B，**不是看你用不用 Antigravity**。

### 1.6 遇到問題怎麼辦：先問 AI，不要先找 David

**這一節可能是整份指南最重要的一段。請認真看。**

David 一個人帶 13 位老師。如果每位老師卡住都直接傳訊息問他，David 沒辦法工作。**但你其實有一個 24 小時不下班、而且比 David 更快回你的助手：AI**。

你平常已經在跟 AI 協作備課。設定、除錯這種事，AI 處理得非常好——而且**越給它細節，它回答得越準**。

### 問 AI 的三個方法（按效果從好到差排序）

#### 方法 1：把「發生了什麼」整段貼給 AI

**不要只說「我卡住了」「它壞了」「我不懂」**。AI 不在你電腦前面，它看不到你的畫面。

**要這樣說**：

> 我在跑 Part A 的 A4，貼完 `git clone` 那行之後看到這個錯誤：
>
> ```
> [把終端機裡紅色或黃色的訊息整段複製貼上]
> ```
>
> 我該怎麼做？

**重點**：
- 終端機裡**整段畫面**複製貼上（Windows：滑鼠拖選 → 右鍵複製；Mac：滑鼠拖選 → `⌘+C`）
- 不要自己翻譯、不要摘要、不要只貼一句——**原文整段給 AI**
- 說清楚你**在做哪一步**（例如「Part A 的 A4」「Part C1 確認分支」）

#### 方法 2：把相關的檔案餵給 AI

有時候問題出在某個設定檔。例如「`environment.env` 好像沒填對」「`acl.yaml` 裡面找不到我」。這時候：

- **在 Antigravity 裡**：對話時輸入 `@` 符號，會跳出檔案選單，選那個檔案它就會被餵進對話裡
- **在其他 AI 工具裡（ChatGPT / Claude 網頁版）**：用「附加檔案」的按鈕上傳，或整個檔案內容複製貼上到對話框

然後說：「這是我的 `environment.env`，你看看哪裡填錯了？」

#### 方法 3：把這整份指南餵給 AI（萬能做法）

如果你卡在**某一步但說不清楚到底是哪一步**，或者畫面跟指南對不上，**最簡單的辦法是把整份指南餵給 AI，讓它當你的隨身家教**：

1. 在 Antigravity 裡：輸入 `@teacher-reclone-guide-2026-04.md`
2. 或者：把這個 md 檔整份複製貼到對話框
3. 然後說：「這是我正在跟的指南。我剛做到 A5，看到這個畫面：[貼畫面]。請用這份指南的邏輯回答我。」

**這個做法特別適合**：指南裡某個說法你看不懂、畫面跟指南寫的不一樣、忘記自己做到哪一步了。

### 真的試過 AI 還是沒解——才找 David

**條件**：你已經把畫面貼給 AI，AI 也回了建議，你照做之後還是不行。**這時候**才傳訊息給 David，並且請附上：

- 你做到哪一步（例：A5）
- 終端機完整畫面截圖
- AI 已經給過的建議（截圖或貼上）
- AI 的建議你試過之後發生了什麼

這樣 David 一看就懂狀況，不用再問你一輪。**對你來說也省時間**——省掉等 David 回覆的空窗。

### 2. 「指令」是什麼

指令就是一段文字，你**貼進終端機**，然後**按 Enter（回車鍵）**，電腦就會照著做。

每一段指令會用這種灰色方框呈現：

```
git status
```

**你要做的事**：把方框裡的文字完整複製（不要漏字），貼到終端機裡，按 Enter。

### ⚠️ 非常重要：多行指令要「一行一行」貼

如果你看到方框裡有**兩行以上**的指令，例如：

```
cd ~/Desktop
git clone https://github.com/...
```

**請這樣做**：

1. 只複製**第一行**（`cd ~/Desktop`），貼到終端機，**按 Enter**
2. 等它跑完（游標回到新的一行）
3. 再複製**第二行**（`git clone ...`），貼到終端機，**按 Enter**

**不要**把兩行一起複製、一起貼進去、只按一次 Enter——很多系統下這樣做，第二行會被吃掉不執行，你以為做完了但其實只做了一半。

**規則只有一條**：**一個方框內有幾行，你就按幾次 Enter**。

### 3. 關於符號的說明（不要怕它們）

終端機裡會看到一堆符號，你**不需要懂它們在做什麼**，只要**一字不漏地複製貼上**就好。但有幾個符號稍微了解一下比較安心：

| 符號 | 唸法 | 意思 |
|---|---|---|
| `/` | 斜線 | 資料夾的分隔。例：`桌面/TeacherOS` = 桌面底下的 TeacherOS 資料夾 |
| `\` | 反斜線 | Windows 用這個當分隔。例：`Desktop\TeacherOS` |
| `:` | 冒號 | Windows 的硬碟代號後會接冒號。例：`C:` 就是 C 槽 |
| `-` | 減號（橫線） | 指令的「選項」前面會有。例：`git branch -a` 的 `-a` 表示「全部」 |
| `~` | 波浪號 | 「你家的資料夾」的意思（Mac/Linux）。例：`~/Desktop` = 你的桌面 |
| `"..."` | 雙引號 | 把一段有空格或中文的字串包起來 |
| `$` 或 `>` | 提示符號 | 終端機等你打字的信號，你**不用打這個**，它本來就在那邊 |

**複製指令時，如果方框裡有註解（`#` 開頭的行），那是給你看的說明，不是你要打的東西。** 但註解連同指令一起複製貼上**不會壞事**，電腦會自動忽略註解。

### 4. 常見的英文按鍵翻譯

| 英文 | 中文 |
|---|---|
| Enter / Return | 回車鍵（大的那顆） |
| Space | 空白鍵 |
| Tab | 定位鍵（Caps Lock 上面那顆） |
| Ctrl | 控制鍵（Mac 的 Control） |
| Cmd / ⌘ | 蘋果鍵（Mac 獨有） |

---

## 你需要先準備的東西（花 2 分鐘核對）

| 項目 | 如何確認 |
|---|---|
| 你的 GitHub 帳號名稱 | 上 github.com 登入，右上角頭像看到的 `@xxxx` 就是 |
| 你的 email（註冊 GitHub 用的） | 同上，設定頁面看得到 |
| 你的「個人分支名稱」 | 見下表。還是不確定，**把下表貼給 AI 請它幫你對照**；不要猜 |

### 13 位老師的個人分支對照表

| 老師姓名 | 你的專屬分支名稱 |
|---|---|
| 林詩閔 | `workspace/Teacher_林詩閔` |
| 劉佳芳 | `workspace/Teacher_劉佳芳` |
| 郭耀新 | `workspace/Teacher_郭耀新` |
| 林雅婷 | `workspace/Teacher_林雅婷` |
| 莊宜瑾 | `workspace/Teacher_莊宜瑾` |
| 張銘分 | `workspace/Teacher_張銘分` |
| 張仁謙 | `workspace/Teacher_張仁謙` |
| 陳佩珊 | `workspace/Teacher_陳佩珊` |
| 姜善迪 | `workspace/Teacher_姜善迪` |
| 李佳穎 | `workspace/Teacher_李佳穎` |
| 謝岷樺 | `workspace/Teacher_謝岷樺` |
| 陳啟華 | `workspace/Teacher_陳啟華` |
| 王琬婷 | `workspace/Teacher_王琬婷` |

**請把你的那一行分支名稱記起來或打字到便利貼**，後面會用到。

---

# Part A：如果你是 Windows 老師

Mac 老師請直接跳到 **Part B**。

> **如果你平常在 Antigravity 裡工作**：這一次的重新設定，**建議先關掉 Antigravity，用外部 PowerShell 做**。因為我們要刪除並重建整個資料夾，Antigravity 若正開著那個資料夾，會斷掉連結造成混亂。等 Part A 做完，再用 Antigravity 重新打開新的 `WaldorfTeacherOS-Repo` 即可。

## A1. 打開「PowerShell」

**這個動作你現在就做。**

1. 按 **Windows 鍵**，左下角跳出搜尋列。
2. 輸入 `PowerShell`。
3. 看到「**Windows PowerShell**」這個藍色圖示，**對它按右鍵 → 以系統管理員身分執行**。
   - 跳出「是否允許這個 App 變更你的裝置」視窗 → 按**是**。
4. 一個藍底白字的視窗會打開。

最後一行會有游標在閃，開頭像這樣：

```
PS C:\Users\你的使用者名稱>
```

**這就是 PowerShell**。之後指南說「貼到 PowerShell」，就是指這個視窗。

## A2. 確認你有安裝 Git

**貼入 PowerShell**：

```powershell
git --version
```

- **看到 `git version 2.xx.x`** → 跳到 A3
- **看到 `'git' is not recognized...`** → 還沒安裝 Git，先做下面：

```powershell
winget install --id Git.Git -e --source winget
```

安裝完後，**關閉 PowerShell，重新以系統管理員身分打開**，再跑一次 `git --version` 確認。

## A3. 刪除舊的 `WaldorfTeacherOS-Repo` 資料夾

**貼入 PowerShell**：

```powershell
Remove-Item -Path "$HOME\Desktop\WaldorfTeacherOS-Repo" -Recurse -Force
```

這行做的事：把桌面上原本的 `WaldorfTeacherOS-Repo` 完全刪掉。

> 放心：David 這邊已經保留一份完整備份，你的檔案不會消失。

**確認刪除成功**：

```powershell
Get-ChildItem "$HOME\Desktop" | Where-Object Name -like "*WaldorfTeacherOS*"
```

畫面如果**沒有任何東西列出來**，代表刪乾淨了。

## A4. 下載乾淨的新版 TeacherOS

**貼入 PowerShell**（**兩行，一行一行貼，各按一次 Enter**）：

```powershell
cd $HOME\Desktop
```

```powershell
git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git WaldorfTeacherOS-Repo
```

**畫面會跑很多行文字**。看到 `Resolving deltas: 100% ... done.` 就是成功。

**如果看到 `Authentication failed`**：

```powershell
gh auth login
```

按照提示（選 GitHub.com → HTTPS → Yes → Login with a web browser）登入完成後再跑 `git clone`。

## A5. 進入資料夾，切換到你的個人分支

**貼入 PowerShell**（**兩行，一行一行貼，各按一次 Enter。記得換成你自己的姓名**）：

```powershell
cd $HOME\Desktop\WaldorfTeacherOS-Repo
```

```powershell
git checkout workspace/Teacher_你的姓名
```

舉例，如果你是「王琬婷」老師，第二行就貼：

```powershell
git checkout workspace/Teacher_王琬婷
```

**確認你真的在自己的分支上**：

```powershell
git branch --show-current
```

應該印出 `workspace/Teacher_你的姓名`。如果不是，**停下來問 AI**（把 `git branch --show-current` 的完整輸出貼給它，說明你在 A5）。

## A6. 執行初始設定精靈

**貼入 PowerShell**：

```powershell
.\setup\start.ps1
```

> 如果看到紅字 `此系統上已停用指令碼執行...`，先貼這行解開限制：
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> 按 `Y` 同意，然後重新跑 `.\setup\start.ps1`。

這會跑過 9 個檢查項目（**不會問你問題**，全自動跑完）：

- Git、Repo、Pandoc 是否就緒
- 自動偵測你的 workspace 並建立 `setup/environment.env`
- 自動同步 Git 身份與 Email
- 安裝 Pre-commit / Pre-push hooks
- 確認你站在自己的個人分支上
- Claude Code Hook 設定

**你只要看著它跑完即可**。畫面上每一行開頭：
- `✓` 綠色＝過關
- `⚠` 黃色＝提醒（通常不影響使用）
- `✗` 紅色＝錯誤（請把畫面貼給 AI）

跑完看到 `技術安裝完成！` 就是成功。

> Google Drive / Email / Calendar 等 gws 功能**完全選用**，這個腳本不會問、不會強制安裝。之後想用再依 `ai-core/reference/gws-cli-guide.md` 自己建立。

## A7. 驗收：確認全部就緒

**貼入 PowerShell**（**三行，一行一行貼，各按一次 Enter**）：

```powershell
git branch --show-current
```

```powershell
Get-Content setup\environment.env -Head 5
```

```powershell
Test-Path .git\hooks\pre-commit
```

**應該看到**：
1. 你的分支名稱（`workspace/Teacher_xxx`）
2. `USER_NAME=` 開頭的幾行
3. `True`

全部 OK → **恭喜完成**。跳到 **Part C**。

---

# Part B：如果你是 Mac 老師

Windows 老師請翻回 **Part A**。

> **如果你平常在 Antigravity 裡工作**：這一次的重新設定，**建議先關掉 Antigravity，用外部 Mac 終端機做**。因為我們要刪除並重建整個資料夾，Antigravity 若正開著那個資料夾，會斷掉連結造成混亂。等 Part B 做完，再用 Antigravity 重新打開新的 `WaldorfTeacherOS-Repo` 即可。

## B1. 打開「終端機」

**這個動作你現在就做。**

1. 按住 **⌘（蘋果鍵）+ 空白鍵**，畫面中間會跳出 Spotlight 搜尋框。
2. 輸入 `Terminal` 或中文「終端機」。
3. 按 **Enter**。

你會看到一個白底黑字（或黑底白字）的視窗打開。裡面會有一行長這樣：

```
你的電腦名稱:~ 你的使用者名稱$
```

尾巴的 `$` 後面會有一個閃爍的游標——**這就是它在等你打字**。

**之後這份指南每一段說「把指令貼進終端機」，就是指這個視窗。**

## B2. 刪除舊的 `WaldorfTeacherOS-Repo` 資料夾

**貼入終端機**：

```bash
rm -rf ~/Desktop/WaldorfTeacherOS-Repo
```

這行做的事：把桌面上原本那個 `WaldorfTeacherOS-Repo` 永久刪除（不會進垃圾桶）。

> 放心：David 這邊已經保留一份完整備份，你的檔案不會消失。
> `rm -rf` 是一個威力很大的指令，打錯路徑會把別的東西也刪掉。**請逐字對照這一行，不要自己改**。

**確認刪除成功**：

```bash
ls ~/Desktop | grep WaldorfTeacherOS
```

畫面如果**沒有任何東西列出來**，代表刪乾淨了。

## B3. 下載乾淨的新版 TeacherOS

**貼入終端機**（**兩行，一行一行貼，各按一次 Enter**）：

```bash
cd ~/Desktop
```

```bash
git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git WaldorfTeacherOS-Repo
```

這兩行做的事：
- 第一行 `cd ~/Desktop`：把終端機的「工作位置」切到桌面
- 第二行 `git clone ...`：從 GitHub 下載一份完整的 TeacherOS 到桌面，資料夾名字叫 `WaldorfTeacherOS-Repo`

**畫面會跑很多行文字**，可能花 30 秒到 2 分鐘。看到最後出現：

```
Resolving deltas: 100% (xxxx/xxxx), done.
```

就是成功了。

**如果看到 `Permission denied` 或 `Authentication failed`**：代表你的 GitHub 登入過期了。先執行：

```bash
gh auth login
```

按照提示操作（選 GitHub.com → HTTPS → Yes → Login with a web browser），完成後回來重新執行 `git clone` 那一行。

## B4. 進入資料夾，切換到你的個人分支

**貼入終端機**（**兩行，一行一行貼，各按一次 Enter。注意：把 `Teacher_你的姓名` 換成你自己的那一個，對照上面的分支表**）：

```bash
cd ~/Desktop/WaldorfTeacherOS-Repo
```

```bash
git checkout workspace/Teacher_你的姓名
```

舉例：如果你是「林雅婷」老師，第二行就貼：

```bash
git checkout workspace/Teacher_林雅婷
```

**你應該看到**：

```
Branch 'workspace/Teacher_林雅婷' set up to track 'origin/workspace/Teacher_林雅婷'.
Switched to a new branch 'workspace/Teacher_林雅婷'
```

**確認你真的在自己的分支上**：

```bash
git branch --show-current
```

這行會印出你現在所在的分支名稱，**應該就是 `workspace/Teacher_你的姓名`**。如果不是，**停下來問 AI**（把 `git branch --show-current` 的完整輸出貼給它，說明你在 B4）。

## B5. 執行初始設定精靈

**貼入終端機**：

```bash
bash setup/start.sh
```

這會跑過 9 個檢查項目（**不會問你問題**，全自動跑完）：

- Git、Repo、Homebrew、Pandoc 是否就緒
- 自動偵測你的 workspace 並建立 `setup/environment.env`
- 自動同步 Git 身份與 Email
- 安裝 Pre-commit / Pre-push hooks
- 確認你站在自己的個人分支上
- Claude Code Hook 設定

**你只要看著它跑完即可**。畫面上每一行開頭：
- `✓` 綠色＝過關
- `⚠` 黃色＝提醒（通常不影響使用）
- `✗` 紅色＝錯誤（請把畫面貼給 AI）

跑完看到 `技術安裝完成！` 就是成功。

> Google Drive / Email / Calendar 等 gws 功能**完全選用**，這個腳本不會問、不會強制安裝。之後想用再依 `ai-core/reference/gws-cli-guide.md` 自己建立。

## B6. 驗收：確認全部就緒

**貼入終端機**（**三行，一行一行貼，各按一次 Enter**）：

```bash
git branch --show-current
```

```bash
cat setup/environment.env | head -5
```

```bash
ls .git/hooks/pre-commit
```

**你應該看到**：
1. 你的分支名稱（`workspace/Teacher_xxx`）
2. `USER_NAME=`、`USER_EMAIL=` 等開頭的幾行
3. `.git/hooks/pre-commit` 這個路徑存在

都有 → **恭喜你，全部就緒**。繼續 **Part C**。

---

# Part C：日常工作的規矩（所有老師都要看）

這一段是**之後每天工作時**要遵守的原則。印出來貼在電腦旁都可以。

## C1. 每次開始工作前：確認你「站在自己的分支上」

**什麼是「分支」？**

想像 TeacherOS 是一個大資料櫃，`main` 是公版的樣板，每位老師有自己的「分支」，是你的個人抽屜。你的備課、學生紀錄、教學反思，全部存在你的分支裡。**如果你不小心在 `main` 上工作，就等於在公版上改東西，這會被系統擋下來**。

### 怎麼確認我站在對的分支上？

**頭幾次打開 TeacherOS 準備工作前，先打開一個終端機視窗**。打開的方法**看你平常在哪裡工作**：

| 你平常在哪裡工作 | 怎麼打開終端機 |
|---|---|
| **Google Antigravity IDE**（多數老師） | 上方選單 `View` → `Terminal`，或按 **Ctrl + `**（backtick） |
| **直接用 Mac** | `⌘ + 空白鍵` → 輸入 `Terminal` → Enter |
| **直接用 Windows** | Windows 鍵 → 輸入 `PowerShell` → Enter |

> 三種方法裡，**Antigravity 內建的終端機最方便**——不用切換視窗，貼完指令、看完結果就繼續跟 AI 對話。平常就用這個。

打開終端機後，**貼這行確認你在哪一個分支**：

```
git branch --show-current
```

- **看到 `workspace/Teacher_你的姓名`** → 好，你在對的地方。開工。
- **看到 `main` 或其他名字** → 先切回來：

  ```
  git checkout workspace/Teacher_你的姓名
  ```

  再確認一次 `git branch --show-current` 有沒有回來。

> 這件事**就像開車前要先看油表**。養成習慣，不會吃虧。三秒鐘的事，不要跳過。

## C2. 什麼才是「安全的 Commit」？

Commit = 存檔。但系統只允許你存**你自己 workspace 裡的檔案**。不要動別人的資料夾。

實際上，你**不需要自己下 commit 指令**。跟 AI 說「**收工**」或「**存檔**」，AI 會幫你做以下檢查：

1. ✅ 你有沒有不小心改到別人的檔案？
2. ✅ 你的變更有沒有合理對應到你今天的工作？
3. ✅ 你現在是不是在自己的分支上？

三個都通過，才會真的存檔並推送到 GitHub。

**如果 AI 沒有這樣檢查，而是直接下 `git add -A` 或 `git commit`——請你立刻叫它停下來，要它說明為什麼不走上面三步檢查**。可以直接對它說：「停，你沒做安全檢查。先跑 `git status`、確認分支、確認只有我 workspace 內的檔案，再 commit。」AI 照做就繼續；如果它還是堅持，把這段對話貼給另一個 AI（開新對話）問意見。

### 安全 Commit 的三個絕對原則

1. **不准 `git add .` 或 `git add -A`**
   這兩個指令會把所有變動全丟進去，包含可能是暫存垃圾、別人的檔案、機密檔案。

2. **只 add 你的 workspace 內的東西**
   你的 workspace 路徑是 `workspaces/Working_Member/Teacher_你的姓名/`。AI 只會碰這個路徑裡的檔案。

3. **每次 commit 前看一下 `git status`**
   看得懂不重要，重要的是**如果看到你不認識的檔案在 `Changes to be committed` 底下，停下來，把整段 `git status` 輸出貼給 AI 問它「這些是什麼？該不該 commit？」**

## C3. 什麼情況下請停下來問 AI

以下任何一種情況，**不要自己硬解，也不要硬著頭皮讓 AI 繼續執行。先停下來把狀況整段貼給 AI**（方式見前面「1.6 遇到問題怎麼辦」那一節）：

- 看到紅色的錯誤訊息，裡面出現 `conflict`、`reject`、`permission denied`
- 跑 `git branch --show-current` 看到奇怪的名字（不是 `main`，也不是你的 `workspace/Teacher_xxx`）
- AI 想要推送到 `main` 分支（不可以）
- AI 建議你用 `--force` 或 `--no-verify`（通常都不對）
- 終端機跑很久沒反應，而且你已經按過 Enter 好幾次了
- 跟著這份指南做到一半，卡住或畫面跟指南說的對不上

**正確做法**：

1. **不要自己亂試**——一個錯誤試錯試出來的後果，通常比停 10 分鐘還嚴重
2. **把終端機畫面完整貼給 AI**，加上「我在 Part X 的 Xn 這一步，看到這個」
3. **如果可以**，把這份 `teacher-reclone-guide-2026-04.md` 一起餵給 AI 當脈絡
4. 照 AI 的建議一步一步做，**做完一步就貼結果給它確認，再做下一步**
5. 試過 AI 的方法 2-3 次還是解不開，**才傳訊息給 David**，附上前面所有的對話與截圖

---

# Part D：常見問題排除

### Q1. 我不小心在 `main` 上做了改動怎麼辦？

**停下來，不要再動**。打開 AI，把下面兩行**一行一行**跑過，把輸出整段貼給 AI，請它教你怎麼救：

```
git status
```

```
git branch --show-current
```

說給 AI 的方式：「我在做 TeacherOS reclone guide 的工作時，不小心改到 `main` 分支。這是 git status 和 branch 的輸出：[貼畫面]。請教我怎麼把改動搬回我的 `workspace/Teacher_xxx` 分支，不要推送到 main。」

AI 處理不了再找 David。

### Q2. 我的 Google Drive / Email / Calendar 以前可以用，現在連不上？

這次整理把 Google Workspace 工具（`gws`）從系統中移除了。**現在每位老師的 gws 都是獨立的**——你需要用自己的 Google 帳號建立自己的 OAuth 專案，跟 David 沒有關係（David 不會也不能看到你的 Drive / Email / Calendar）。

**先問 AI**：「我之前用 TeacherOS 上傳 Drive / 寄 Email / 寫 Calendar，現在不行了。請根據 `teacher-reclone-guide-2026-04.md` 和 repo 裡的 `ai-core/reference/gws-cli-guide.md`，教我重新設定我自己的 gws（包含建立我自己的 GCP 專案、OAuth 憑證、`gws auth setup`、`gws auth login`）。」——把這份指南和 `gws-cli-guide.md` 一起餵給 AI。

AI 會引導你完成全部步驟。如果卡在 GCP Console 介面看不懂、或是某個權限按鈕找不到，**繼續問 AI 並把畫面截圖貼給它**——這是你個人的 Google 帳號，David 沒有控制權，無法代你操作。

如果你之前**沒在用這些功能**（只用 TeacherOS 的備課、課程設計、學生紀錄），**不受影響**，略過這題。

### Q3. 舊的 Google Drive for Desktop 同步會不會衝突？

不會。Google Drive 同步的是雲端硬碟，跟你桌面上的 Git 資料夾沒有連動。兩邊各做各的。

### Q4. 我擔心我電腦裡有些東西沒上傳到 GitHub，刪掉就找不回來了？

David 這邊在系統整理前已經做過一次完整備份，所有有推送到 GitHub 的內容都在新的 repo 裡。

如果你很確定自己有**從未 commit 過**的重要檔案（例如自己存在資料夾裡但沒讓 AI 存檔的草稿），**先不要刪**。打開 AI，說：「我懷疑我的舊 TeacherOS 資料夾裡有沒 commit 的檔案。請幫我檢查 `~/Desktop/WaldorfTeacherOS-Repo` 裡有沒有未追蹤（untracked）或未 commit（uncommitted）的變更。」AI 會幫你跑 `git status` 並判讀結果。

確認沒東西遺漏再刪。真的找到重要但沒 commit 的檔案，先複製到桌面其他地方，再往下進行。

---

## 最後提醒

這份指南是**一次性**的。做完 Part A 或 Part B、讀完 Part C 之後，你就**不需要再看它**了。之後日常工作只要照 **Part C 的三條原則**做，就會一路順暢。

**遇到問題的處理順序**：

1. **先把狀況整段貼給 AI**——終端機畫面、錯誤訊息、你做到哪一步，全部給它
2. **必要時把這份指南也餵給 AI** 當脈絡（`@teacher-reclone-guide-2026-04.md`）
3. **照 AI 的建議一步一步試**，每一步都把結果回報給它
4. **AI 試過幾輪還是無解，才傳訊息給 David**，附上所有對話紀錄與截圖

**不要硬撐**、**不要亂試**、**不要用 `--force`**、**不要直接先找 David**（他忙不過來，AI 比較快也比較有耐心）。

祝你順利回到備課的正事上。

---

*版本：2026-04-17｜對應 TeacherOS v2.0 乾淨起點（commit 93d9012）*
*維護：David（elliot200852@gmail.com）*
