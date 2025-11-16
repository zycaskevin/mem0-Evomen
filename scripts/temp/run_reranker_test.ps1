# Reranker Interface 驗證測試 (PowerShell 版本)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Reranker Interface 驗證測試" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] 切換到 mem0-evomem 目錄..." -ForegroundColor Yellow
Set-Location "C:\Users\User\.claude\mem0-evomem"

if (-not (Test-Path "mem0")) {
    Write-Host "[ERROR] 找不到 mem0 目錄" -ForegroundColor Red
    Write-Host "[INFO] 當前目錄: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "[INFO] 請確認已經 Fork 並 Clone mem0 倉庫到 mem0-evomem 目錄" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "[OK] 已在 mem0-evomem 目錄中" -ForegroundColor Green
Write-Host "[OK] 當前目錄: $(Get-Location)" -ForegroundColor Green
Write-Host ""

Write-Host "[INFO] 開始執行 Reranker Interface 驗證..." -ForegroundColor Yellow
python "C:\Users\User\.claude\Mem0Evomem\scripts\verify_reranker_interface.py"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "測試完成" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
pause
