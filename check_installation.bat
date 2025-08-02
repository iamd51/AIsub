@echo off
chcp 65001 >nul
title Whisper 字幕生成器 - 安裝檢查

echo ========================================
echo    Whisper 字幕生成器 - 安裝檢查
echo ========================================
echo.

REM 設定環境變數以解決編碼問題
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python
    echo 請先從 https://python.org 下載並安裝 Python
    echo.
    pause
    exit /b 1
)

echo [資訊] 正在執行詳細檢查...
echo.

REM 執行 Python 檢查腳本
python check_installation.py

REM 如果檢查腳本不存在，顯示基本資訊
if errorlevel 1 (
    echo.
    echo [錯誤] 檢查腳本執行失敗
    echo 請確保 check_installation.py 檔案存在
    pause
)