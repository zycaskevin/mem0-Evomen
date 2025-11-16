# BGE-M3 測試執行腳本
Set-Location "C:\Users\User\.claude\Mem0Evomem"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "BGE-M3 導入測試" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 執行導入測試
python test_import.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "導入測試成功，開始完整驗證" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""

    # 執行完整驗證
    python scripts\verify_bge_m3_implementation.py
} else {
    Write-Host ""
    Write-Host "[ERROR] 導入測試失敗" -ForegroundColor Red
}

Write-Host ""
Write-Host "按任意鍵繼續..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
