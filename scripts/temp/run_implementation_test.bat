@echo off
chcp 65001 >nul
echo ============================================================
echo BGE-M3 Embedder 實作驗證
echo ============================================================
echo.

python scripts\verify_bge_m3_implementation.py

echo.
pause
