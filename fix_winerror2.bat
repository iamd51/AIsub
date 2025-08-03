@echo off
chcp 65001 >nul
echo ========================================
echo     修復 [WinError 2] 問題
echo     解決 FFmpeg 缺失導致的錯誤
echo ========================================
echo.

echo 🔍 檢查問題...
python fix_ffmpeg_issue.py

echo.
echo ✅ 修復完成！
echo.
echo 📋 接下來可以:
echo   1. 執行 start_whisper_gui.bat 啟動程式
echo   2. 或直接執行 python whisper_subtitle_gui.py
echo.
pause