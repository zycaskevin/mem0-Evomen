Set-Location "C:\Users\User\.claude\Mem0Evomem"

if (Test-Path "test_result.txt") {
    Write-Host "Test result file found!" -ForegroundColor Green
    Write-Host ""
    Write-Host "="*60
    Get-Content "test_result.txt"
    Write-Host "="*60
} else {
    Write-Host "Test result file not found yet. Test may still be running..." -ForegroundColor Yellow
}
