@echo off
chcp 65001 >nul
title 安裝 Whisper 和相關套件

echo ========================================
echo    Whisper 字幕生成器 - 套件安裝程式
echo ========================================
echo.

REM 檢查 Python
python --version
if errorlevel 1 (
    echo [錯誤] 找不到 Python
    echo 請先從 https://python.org 下載並安裝 Python
    pause
    exit /b 1
)

echo [資訊] Python 已安裝
echo.

REM 升級 pip
echo [1/4] 升級 pip...
python -m pip install --upgrade pip

REM 安裝 Whisper
echo.
echo [2/4] 安裝 OpenAI Whisper...
pip install openai-whisper

REM 安裝其他必要套件
echo.
echo [3/4] 安裝影片處理套件...
pip install opencv-python Pillow moviepy numpy

REM 安裝音訊處理套件
echo.
echo [4/4] 安裝音訊處理套件...
pip install pydub

echo.
echo ========================================
echo              安裝完成！
echo ========================================
echo.
echo 現在您可以：
echo 1. 雙擊 start_whisper_gui.bat 啟動圖形介面
echo 2. 或直接執行: python whisper_subtitle_gui.py
echo.
echo 注意事項：
echo - 首次使用時 Whisper 會下載模型檔案（約 100MB-1GB）
echo - 模型會儲存在: %USERPROFILE%\.cache\whisper
echo - 建議使用 medium 模型，平衡速度和準確度
echo - 使用 WAV 檔案比影片檔案更準確
echo - 處理長影片時請耐心等待
echo.
pause