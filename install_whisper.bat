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
echo [1/6] 升級 pip...
python -m pip install --upgrade pip

REM 安裝 Whisper
echo.
echo [2/6] 安裝 OpenAI Whisper...
pip install openai-whisper

REM 檢查 NVIDIA GPU
echo.
echo [3/6] 檢查 NVIDIA GPU...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo [資訊] 未偵測到 NVIDIA GPU，將安裝 CPU 版本
    echo [安裝] 安裝 PyTorch CPU 版本...
    pip install torch torchvision torchaudio
) else (
    echo [偵測] 找到 NVIDIA GPU，安裝 CUDA 版本以獲得最佳性能
    nvidia-smi --query-gpu=name --format=csv,noheader,nounits
    
    REM 檢查並安裝 CUDA 版本的 PyTorch
    python -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>nul
    if errorlevel 1 (
        echo [安裝] 安裝 PyTorch CUDA 版本以支援 GPU 加速...
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ) else (
        python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
        if errorlevel 1 (
            echo [升級] 升級到 PyTorch CUDA 版本...
            pip uninstall torch torchvision torchaudio -y
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        ) else (
            echo [確認] PyTorch CUDA 版本已安裝
        )
    )
)

REM 安裝其他必要套件
echo.
echo [4/6] 安裝影片處理套件...
pip install opencv-python Pillow moviepy numpy

REM 安裝音訊處理套件
echo.
echo [5/6] 安裝音訊處理套件...
pip install pydub librosa

REM 安裝 GUI 相關套件
echo.
echo [6/6] 安裝 GUI 和其他套件...
pip install pygame pathlib

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
echo - GPU 加速已啟用，可能會看到 Triton 警告但不影響功能
echo - 處理長影片時請耐心等待
echo.
pause