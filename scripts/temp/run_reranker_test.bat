@echo off
chcp 65001 >nul
echo ============================================================
echo Reranker Interface 驗證測試
echo ============================================================
echo.

echo [INFO] 切換到 mem0-evomem 目錄...
cd /d "C:\Users\User\.claude\mem0-evomem"

if not exist "mem0" (
    echo [ERROR] 找不到 mem0 目錄
    echo [INFO] 當前目錄: %CD%
    echo [INFO] 請確認已經 Fork 並 Clone mem0 倉庫到 mem0-evomem 目錄
    echo.
    pause
    exit /b 1
)

echo [OK] 已在 mem0-evomem 目錄中
echo [OK] 當前目錄: %CD%
echo.

echo [INFO] 開始執行 Reranker Interface 驗證...
python "C:\Users\User\.claude\Mem0Evomem\scripts\verify_reranker_interface.py"

echo.
echo ============================================================
echo 測試完成
echo ============================================================
echo.
pause
