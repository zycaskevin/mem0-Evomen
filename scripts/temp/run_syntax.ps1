Set-Location "C:\Users\User\.claude\Mem0Evomem"

Write-Host "Executing syntax_test.py..." -ForegroundColor Cyan
python syntax_test.py
Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor $(if($LASTEXITCODE -eq 0){"Green"}else{"Red"})
