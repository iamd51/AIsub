@echo off
chcp 65001 >nul
title GPU 支援檢查工具

echo ========================================
echo        GPU 支援檢查工具
echo ========================================
echo.

REM 檢查 NVIDIA GPU
echo [1/4] 檢查 NVIDIA GPU...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ❌ 找不到 NVIDIA GPU 或驅動程式
    echo 💡 請確認：
    echo    - 已安裝 NVIDIA 顯示卡
    echo    - 已安裝最新的 NVIDIA 驅動程式
    echo.
) else (
    echo ✅ NVIDIA GPU 已偵測到
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    echo.
)

REM 檢查 Python
echo [2/4] 檢查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 找不到 Python
    echo 💡 請先安裝 Python: https://python.org
    pause
    exit /b 1
) else (
    python --version
    echo ✅ Python 已安裝
    echo.
)

REM 檢查 PyTorch
echo [3/4] 檢查 PyTorch CUDA 支援...
python -c "import torch; print('PyTorch 版本:', torch.__version__); print('CUDA 可用:', torch.cuda.is_available()); print('CUDA 版本:', torch.version.cuda if hasattr(torch.version, 'cuda') else 'N/A')" 2>nul
if errorlevel 1 (
    echo ❌ PyTorch 未安裝或有問題
    echo 💡 執行以下命令安裝 CUDA 版本：
    echo    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    echo.
) else (
    echo ✅ PyTorch 檢查完成
    echo.
)

REM 檢查 Whisper
echo [4/4] 檢查 Whisper...
python -c "import whisper; print('Whisper 版本:', whisper.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ Whisper 未安裝
    echo 💡 執行以下命令安裝：
    echo    pip install openai-whisper
    echo.
) else (
    echo ✅ Whisper 已安裝
    echo.
)

echo ========================================
echo            檢查完成
echo ========================================
echo.
echo 💡 如果所有項目都顯示 ✅，表示 GPU 加速已準備就緒
echo 💡 如果有 ❌ 項目，請按照提示進行修復
echo 💡 執行 install_whisper.bat 可以自動安裝所需套件
echo.
pause