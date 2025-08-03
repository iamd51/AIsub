@echo off
chcp 65001 >nul
echo ========================================
echo     音樂字幕清理工具
echo     清理「作詞・作曲・編曲 初音ミク」等無關內容
echo ========================================
echo.

python clean_music_subtitles.py

pause