@echo off
chcp 65001 >nul
cd /d "C:\Users\User\.claude\Mem0Evomem"

echo ============================================================
echo BGE-M3 語法檢查測試
echo ============================================================
echo.

python syntax_test.py

echo.
echo ============================================================
pause
