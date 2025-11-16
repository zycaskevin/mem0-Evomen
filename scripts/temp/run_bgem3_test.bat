@echo off
chcp 65001 >nul
echo ============================================================
echo BGE-M3 API 測試腳本
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/2] 執行簡化測試...
python quick_test.py
if errorlevel 1 (
    echo.
    echo [WARN] 快速測試失敗，嘗試完整驗證...
    echo.
)

echo.
echo [2/2] 執行完整 BGE-M3 API 驗證...
python test_bgem3_simple.py

echo.
echo ============================================================
echo 測試完成
echo ============================================================
echo.
pause
