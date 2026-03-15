# TeacherOS 快速啟動 — Windows 入口
# 檢查 Python 3，然後呼叫 quick-start.py

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

    # 嘗試 winget 安裝
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "  偵測到 winget，正在安裝 Python 3..." -ForegroundColor Cyan
        winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
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
Write-Host "  Python 3 已就緒：$( & $py --version 2>&1 )" -ForegroundColor Green
Write-Host ""

& $py "$ScriptDir\quick-start.py" @args
