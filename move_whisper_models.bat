@echo off
chcp 65001 >nul
title Whisper 模型移動工具

echo ========================================
echo        Whisper 模型移動工具
echo ========================================
echo.

set "DEFAULT_DIR=%USERPROFILE%\.cache\whisper"
echo 預設模型位置: %DEFAULT_DIR%
echo.

REM 檢查預設位置是否存在
if not exist "%DEFAULT_DIR%" (
    echo [資訊] 預設模型目錄不存在，可能尚未下載任何模型
    echo.
    goto :ask_new_location
)

REM 列出現有模型
echo [檢查] 現有模型檔案:
echo 新格式 (.pt):
dir /b "%DEFAULT_DIR%\*.pt" 2>nul
if errorlevel 1 (
    echo   (無 .pt 模型檔案)
) else (
    for %%f in ("%DEFAULT_DIR%\*.pt") do (
        set "size=0"
        for /f "tokens=3" %%a in ('dir "%%f" /-c ^| find "%%~nxf"') do set "size=%%a"
        call :show_size "%%~nxf" !size!
    )
)

echo 舊格式 (.bin):
dir /b "%DEFAULT_DIR%\ggml-*.bin" 2>nul
if errorlevel 1 (
    echo   (無 .bin 模型檔案)
) else (
    for %%f in ("%DEFAULT_DIR%\ggml-*.bin") do (
        set "size=0"
        for /f "tokens=3" %%a in ('dir "%%f" /-c ^| find "%%~nxf"') do set "size=%%a"
        call :show_size "%%~nxf" !size!
    )
)
echo.

:ask_new_location
set /p "NEW_DIR=請輸入模型存放位置 (例如: D:\whisper_models): "

if "%NEW_DIR%"=="" (
    echo [錯誤] 未輸入路徑
    pause
    exit /b 1
)

REM 建立新目錄
if not exist "%NEW_DIR%" (
    echo [建立] 建立新目錄: %NEW_DIR%
    mkdir "%NEW_DIR%" 2>nul
    if errorlevel 1 (
        echo [錯誤] 無法建立目錄
        pause
        exit /b 1
    )
)

REM 移動模型檔案
set "moved=0"

if exist "%DEFAULT_DIR%\*.pt" (
    echo [移動] 正在移動 .pt 模型檔案...
    move "%DEFAULT_DIR%\*.pt" "%NEW_DIR%\" >nul 2>&1
    if not errorlevel 1 set "moved=1"
)

if exist "%DEFAULT_DIR%\ggml-*.bin" (
    echo [移動] 正在移動 .bin 模型檔案...
    move "%DEFAULT_DIR%\ggml-*.bin" "%NEW_DIR%\" >nul 2>&1
    if not errorlevel 1 set "moved=1"
)

if "%moved%"=="1" (
    echo [完成] 模型檔案已移動到: %NEW_DIR%
) else (
    echo [資訊] 沒有模型檔案需要移動
)

echo.
echo [設定] 正在設定環境變數...

REM 設定環境變數
reg add "HKCU\Environment" /v "WHISPER_CACHE_DIR" /t REG_SZ /d "%NEW_DIR%" /f >nul 2>&1
if errorlevel 1 (
    echo [警告] 環境變數設定失敗，請手動設定
    echo 變數名稱: WHISPER_CACHE_DIR
    echo 變數值: %NEW_DIR%
) else (
    echo [完成] 環境變數已設定
)

echo.
echo ========================================
echo              設定完成！
echo ========================================
echo.
echo 新的模型位置: %NEW_DIR%
echo 環境變數: WHISPER_CACHE_DIR = %NEW_DIR%
echo.
echo 注意事項:
echo 1. 請重新啟動所有使用 Whisper 的程式
echo 2. 新下載的模型會自動儲存到新位置
echo 3. 可以安全刪除舊的預設目錄
echo.
pause
goto :eof

:show_size
set "file=%~1"
set "bytes=%~2"
set /a "mb=%bytes% / 1048576"
echo   • %file% (%mb% MB)
goto :eof