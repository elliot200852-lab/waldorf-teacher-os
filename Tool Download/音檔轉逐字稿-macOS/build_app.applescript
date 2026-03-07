-- 音檔轉逐字稿 macOS App
-- 自動偵測專案資料夾位置（不寫死路徑）

on open droppedItems
    -- 取得 App 所在的資料夾作為專案目錄
    set appPath to POSIX path of (path to me)
    -- App 在專案資料夾內，取得上層目錄
    set projectDir to do shell script "dirname " & quoted form of appPath

    set filePaths to ""
    repeat with anItem in droppedItems
        set filePaths to filePaths & " " & quoted form of POSIX path of anItem
    end repeat

    tell application "Terminal"
        activate
        do script "cd " & quoted form of projectDir & " && source venv/bin/activate && python3 transcribe.py" & filePaths & " 2>&1; echo ''; echo '  轉錄完成！按 Enter 關閉此視窗...'; read; exit"
    end tell
end open

on run
    -- 取得 App 所在的資料夾作為專案目錄
    set appPath to POSIX path of (path to me)
    set projectDir to do shell script "dirname " & quoted form of appPath

    set audioFiles to choose file with prompt "選擇要轉錄的音檔：" of type {"public.audio", "com.apple.m4a-audio", "public.mp3"} with multiple selections allowed

    set filePaths to ""
    repeat with anItem in audioFiles
        set filePaths to filePaths & " " & quoted form of POSIX path of anItem
    end repeat

    tell application "Terminal"
        activate
        do script "cd " & quoted form of projectDir & " && source venv/bin/activate && python3 transcribe.py" & filePaths & " 2>&1; echo ''; echo '  轉錄完成！按 Enter 關閉此視窗...'; read; exit"
    end tell
end run
