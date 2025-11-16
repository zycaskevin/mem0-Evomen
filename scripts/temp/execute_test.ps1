Set-Location "C:\Users\User\.claude\Mem0Evomem"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "Executing minimal_test.py..." -ForegroundColor Cyan
Write-Host ""

$output = python minimal_test.py 2>&1 | Out-String
$exitCode = $LASTEXITCODE

Write-Host $output

$output | Out-File -FilePath "test_result.txt" -Encoding UTF8

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "Test completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Test failed with exit code: $exitCode" -ForegroundColor Red
}

Write-Host ""
Write-Host "Output saved to: test_result.txt"
