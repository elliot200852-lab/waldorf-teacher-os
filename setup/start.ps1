# TeacherOS 快速啟動 — Windows 入口
# 檢查 Python 3，然後呼叫 quick-start.py

# 確保 PowerShell 與子行程的 stdout 都用 UTF-8（避免中文亂碼）
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = "utf-8"
try { chcp 65001 | Out-Null } catch {}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 偵測 Python
$py = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $py = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $ver = & python --version 2>&1
    if ($ver -match "Python 3") {
        $py = "python"
    }
}

if (-not $py) {
    Write-Host ""
    Write-Host "  TeacherOS 需要 Python 3 才能執行。" -ForegroundColor Yellow
    Write-Host ""

    # 嘗試 winget 安裝（先詢問教師確認）
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $confirm = Read-Host "  偵測到你的電腦沒有 Python 3。是否要自動安裝？(Y/N)"
        if ($confirm -ne "Y" -and $confirm -ne "y") {
            Write-Host "  已取消。請手動安裝 Python 3：https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "  正在透過 winget 安裝 Python 3..." -ForegroundColor Cyan
        winget install Python.Python.3.13 --accept-package-agreements --accept-source-agreements
        # 重新載入 PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        if (Get-Command python3 -EA 0) { $py = "python3" }
        elseif (Get-Command python -EA 0) { $py = "python" }
    }

    if (-not $py) {
        Write-Host "  請手動安裝 Python 3：" -ForegroundColor Yellow
        Write-Host "    https://www.python.org/downloads/"
        Write-Host ""
        Write-Host "  安裝時請勾選 'Add Python to PATH'" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
$pyVer = & $py --version 2>&1
Write-Host "  Python 3 已就緒：$pyVer" -ForegroundColor Green
Write-Host ""

& $py "$ScriptDir\quick-start.py" @args
