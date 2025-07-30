@echo off
chcp 65001 >nul
title GitHub 專案設定

echo ========================================
echo        GitHub 專案推送工具
echo ========================================
echo.

REM 檢查 Git 是否安裝
git --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Git
    echo 請先安裝 Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [檢查] Git 已安裝
echo.

REM 初始化 Git 倉庫
if not exist ".git" (
    echo [初始化] 建立 Git 倉庫...
    git init
    echo.
)

REM 設定 Git 使用者資訊 (如果尚未設定)
git config user.name >nul 2>&1
if errorlevel 1 (
    set /p "USERNAME=請輸入你的 GitHub 用戶名: "
    set /p "EMAIL=請輸入你的 GitHub 郵箱: "
    git config user.name "!USERNAME!"
    git config user.email "!EMAIL!"
    echo [設定] Git 使用者資訊已設定
    echo.
)

REM 添加檔案到 Git
echo [添加] 正在添加檔案到 Git...
git add .
echo.

REM 提交變更
echo [提交] 正在提交變更...
git commit -m "Initial commit: AI Subtitle Generator Tools

Features:
- Whisper subtitle generator with GUI
- Interactive subtitle editor
- Gemini AI subtitle generator
- Video processor with Japanese font support
- Model management tools
- Batch processing capabilities"

if errorlevel 1 (
    echo [資訊] 沒有新的變更需要提交
)
echo.

REM 詢問 GitHub 倉庫 URL
echo [設定] 請在 GitHub 上建立新的倉庫，然後輸入倉庫 URL
echo 例如: https://github.com/yourusername/ai-subtitle-generator.git
echo.
set /p "REPO_URL=GitHub 倉庫 URL: "

if "%REPO_URL%"=="" (
    echo [錯誤] 未輸入倉庫 URL
    pause
    exit /b 1
)

REM 添加遠端倉庫
echo [設定] 正在添加遠端倉庫...
git remote remove origin >nul 2>&1
git remote add origin "%REPO_URL%"
echo.

REM 推送到 GitHub
echo [推送] 正在推送到 GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo [��誤] 推送失敗
    echo.
    echo 可能的原因:
    echo 1. 網路連線問題
    echo 2. GitHub 認證問題
    echo 3. 倉庫 URL 錯誤
    echo.
    echo 解決方法:
    echo 1. 檢查網路連線
    echo 2. 設定 GitHub Personal Access Token
    echo 3. 確認倉庫 URL 正確
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo            推送成功！
echo ========================================
echo.
echo 你的專案已成功推送到 GitHub:
echo %REPO_URL%
echo.
echo 接下來你可以:
echo 1. 在 GitHub 上編輯 README.md 添加更多說明
echo 2. 設定 GitHub Pages (如果需要)
echo 3. 邀請其他人協作
echo 4. 建立 Release 版本
echo.
pause