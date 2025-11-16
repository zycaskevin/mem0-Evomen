Set-Location "C:\Users\User\.claude\Mem0Evomem"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "Executing mock_test.py..." -ForegroundColor Cyan
Write-Host ""

$output = python mock_test.py 2>&1 | Out-String
$exitCode = $LASTEXITCODE

Write-Host $output

$output | Out-File -FilePath "mock_test_result.txt" -Encoding UTF8

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "Mock test completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Mock test failed with exit code: $exitCode" -ForegroundColor Red
}

Write-Host ""
Write-Host "Output saved to: mock_test_result.txt"
