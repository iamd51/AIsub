# 🚀 快速開始指南

## 📋 系統需求

- Windows 10/11
- Python 3.8 或更新版本
- 網路連線 (用於下載模型和依賴)

## 📥 下載專案

1. 從 GitHub 下載專案 ZIP 檔案
2. 解壓縮到任意資料夾 (例如: `C:\AIsub`)
3. 確保資料夾包含所有必要檔案

## ⚡ 一鍵安裝

1. **雙擊 `install_whisper.bat`**
   - 自動安裝所有必要套件
   - 檢測 GPU 並安裝對應版本
   - 約需 5-10 分鐘

2. **等待安裝完成**
   - 看到 "安裝完成！" 訊息即可

## 🎯 啟動程式

1. **雙擊 `start_whisper_gui.bat`**
   - 自動啟動圖形介面
   - 首次啟動會下載 Whisper 模型

2. **開始使用**
   - 選擇影片檔案
   - 點擊 "一鍵完成"
   - 等待處理完成

## 🔧 故障排除

### 如果遇到問題：

1. **執行檢查工具**
   ```
   雙擊 check_installation.bat
   ```

2. **檢查 Python 安裝**
   ```
   python --version
   ```
   應該顯示 Python 3.8 或更新版本

3. **手動安裝依賴**
   ```
   pip install -r requirements.txt
   ```

### 常見問題：

**Q: 找不到 Python**
- 從 https://python.org 下載並安裝 Python
- 安裝時勾選 "Add Python to PATH"

**Q: 程式啟動失敗**
- 執行 `check_installation.bat` 檢查問題
- 確保所有檔案都已下載

**Q: 處理速度很慢**
- 檢查是否有 NVIDIA GPU
- 確保安裝了 CUDA 版本的 PyTorch

## 📁 檔案說明

### 核心檔案 (必須保留)
- `whisper_subtitle_gui.py` - 主程式
- `video_processor.py` - 影片處理
- `subtitle_editor.py` - 字幕編輯
- `install_whisper.bat` - 安裝腳本
- `start_whisper_gui.bat` - 啟動腳本
- `requirements.txt` - 依賴清單

### 配置檔案
- `whisper_config.json.template` - 配置模板
- `whisper_config.json` - 使用者設定 (自動生成)

### 文件檔案
- `README.md` - 詳細說明
- `WHISPER_README.md` - Whisper 使用說明
- `GPU_ACCELERATION.md` - GPU 加速說明

## 🎵 使用流程

1. **準備影片檔案**
   - 支援 MP4, AVI, MOV, MKV 等格式
   - 建議使用 WAV 音訊檔案獲得更好效果

2. **選擇設定**
   - 模型: medium (推薦) 或 large (更準確)
   - 語言: 日文 (ja), 英文 (en), 中文 (zh)
   - GPU 加速: 自動偵測

3. **開始處理**
   - 點擊 "一鍵完成" 
   - 等待處理完成
   - 輸出檔案會自動儲存

## 📞 支援

如果遇到問題：
1. 查看 [README.md](README.md) 詳細說明
2. 執行 `check_installation.bat` 診斷問題
3. 檢查 GitHub Issues 頁面

---

**提示**: 首次使用時會下載約 1GB 的 Whisper 模型，請確保網路連線穩定。