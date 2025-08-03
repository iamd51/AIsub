@echo off
chcp 65001 >nul
echo ========================================
echo     [WinError 2] 深度診斷工具
echo     專門解決 Whisper 音訊處理問題
echo ========================================
echo.

echo 🔍 開始診斷...
python diagnose_winerror2.py

echo.
echo 📋 如果問題仍然存在，請嘗試:
echo   1. 以管理員身分執行此程式
echo   2. 檢查防毒軟體是否阻擋 FFmpeg
echo   3. 重新安裝 Python 和相關套件
echo.
pause