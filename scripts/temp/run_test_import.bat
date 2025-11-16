@echo off
chcp 65001 >nul
cd /d "C:\Users\User\.claude\Mem0Evomem"
echo ============================================================
echo BGE-M3 導入測試
echo ============================================================
echo.

python test_import.py

echo.
echo ============================================================
echo.
pause
