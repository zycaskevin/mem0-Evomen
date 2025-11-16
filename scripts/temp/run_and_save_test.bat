@echo off
chcp 65001 >nul
cd /d "C:\Users\User\.claude\Mem0Evomem"

echo ============================================================
echo BGE-M3 驗證測試（輸出到文件）
echo ============================================================
echo.
echo 正在執行測試...
echo.

python step_by_step_test.py > test_output.txt 2>&1

echo 測試完成！結果已儲存到 test_output.txt
echo.
type test_output.txt
echo.
echo ============================================================
pause
