@echo off
chcp 65001 >nul
title Whisper 字幕生成器

echo ================================
echo    Whisper 字幕生成器啟動中...
echo ================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python
    pause
    exit /b 1
)

REM 檢查是否安裝了必要的套件
echo [檢查] 正在檢查必要套件...

python -c "import whisper" >nul 2>&1
if errorlevel 1 (
    echo [安裝] 正在安裝 OpenAI Whisper...
    pip install openai-whisper
    if errorlevel 1 (
        echo [錯誤] Whisper 安裝失敗
        pause
        exit /b 1
    )
)

python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 tkinter，請重新安裝 Python 並確保包含 tkinter
    pause
    exit /b 1
)

REM 檢查其他必要套件
python -c "import PIL, cv2, numpy" >nul 2>&1
if errorlevel 1 (
    echo [安裝] 正在安裝其他必要套件...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [警告] 部分套件安裝失敗，但程式可能仍可運行
    )
)

echo [啟動] 正在啟動 Whisper 字幕生成器...
echo.

REM 啟動程式
python whisper_subtitle_gui.py

if errorlevel 1 (
    echo.
    echo [錯誤] 程式執行失敗
    echo 請檢查錯誤訊息並確保所有依賴套件已正確安裝
    pause
)