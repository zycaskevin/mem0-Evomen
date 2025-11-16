@echo off
chcp 65001 >nul
echo ============================================================
echo Week 1 Day 5 完整測試流程
echo ============================================================
echo.

echo [步驟 1/2] 安裝 mem0 開發模式...
echo.
cd /d "C:\Users\User\.claude\mem0-evomem"

if not exist "setup.py" (
    echo [ERROR] 找不到 setup.py 文件
    echo [INFO] 當前目錄: %CD%
    echo [INFO] 請確認在正確的 mem0-evomem 目錄中
    pause
    exit /b 1
)

echo [INFO] 正在執行: pip install -e .
echo [INFO] 這會安裝 mem0 到 Python 環境（開發模式）
echo.

pip install -e .

if errorlevel 1 (
    echo.
    echo [ERROR] mem0 安裝失敗
    echo [INFO] 請檢查錯誤訊息
    pause
    exit /b 1
)

echo.
echo [OK] mem0 開發模式安裝成功！
echo.
echo ============================================================
echo.

echo [步驟 2/2] 執行 Reranker Interface 驗證...
echo.

python "C:\Users\User\.claude\Mem0Evomem\scripts\verify_reranker_interface.py"

echo.
echo ============================================================
echo Week 1 Day 5 測試完成
echo ============================================================
echo.
pause
