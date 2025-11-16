@echo off
chcp 65001 >nul
cd /d "C:\Users\User\.claude\Mem0Evomem"

echo ============================================================
echo BGE-M3 驗證測試
echo ============================================================
echo.

python simple_test.py

echo.
echo ============================================================
echo 結果已儲存到 test_result.txt
echo ============================================================
echo.

if exist test_result.txt (
    echo.
    echo === 測試結果 ===
    type test_result.txt
    echo.
)

pause
