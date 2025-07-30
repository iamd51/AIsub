# 🎵 AI 字幕生成工具集

一套完整的 AI 字幕生成和處理工具，支援多種模式和高精度的日文字幕處理。

## 🌟 主要功能

### 🎯 多種字幕生成方式
- **Whisper 自動生成** - 使用 OpenAI Whisper 高精度語音識別
- **Gemini AI 生成** - 基於歌詞文本智能分配時間軸
- **互動式編輯** - 邊聽音樂邊手動調整時間軸

### 🔥 核心特色
- ✅ **雙操作模式** - 生成字幕或僅燒錄現有字幕
- ✅ **多輸入支援** - 影片檔案、音訊檔案 (WAV 更精確)
- ✅ **完美日文支援** - 自動下載日文字體，正確顯示日文字幕
- ✅ **高品質輸出** - 保持原始影片品質的字幕燒錄
- ✅ **模型管理** - 支援新舊 Whisper 模型格式
- ✅ **圖形化介面** - 簡單易用的 GUI 操作

## 🚀 快速開始

### 1. 安裝依賴
```bash
# 自動安裝 (推薦)
雙擊 install_whisper.bat

# 或手動安裝
pip install -r requirements.txt
pip install openai-whisper
```

### 2. 啟動程式
```bash
# Whisper 字幕生成器 (推薦)
雙擊 start_whisper_gui.bat
# 或
python whisper_subtitle_gui.py

# 互動式字幕編輯器
python subtitle_editor.py

# Gemini 字幕生成器
python subtitle_generator.py
```

## 📱 工具介紹

### 🎤 Whisper 字幕生成器 (`whisper_subtitle_gui.py`)
**最推薦的工具** - 使用 OpenAI Whisper 進行高精度語音識別

**特色：**
- 支援 WAV 音訊檔案輸入 (更高精度)
- 雙操作模式：生成+燒錄 / 僅燒錄現有字幕
- 自動模型管理和下載
- 即時處理日誌顯示

**使用場景：**
- 自動生成字幕 (推薦用於日文歌曲)
- 燒錄現有 SRT 字幕到影片

### 🎵 互動式字幕編輯器 (`subtitle_editor.py`)
**最精確的工具** - 邊聽音樂邊手動調整時間軸

**特色：**
- 即時音訊播放
- 視覺化時間軸編輯
- 精確到 0.1 秒的控制
- 支援載入現有字幕進行微調

**使用場景：**
- 需要極高精度的時間軸
- 微調 AI 生成的字幕
- 專業字幕製作

### 🤖 Gemini 字幕生成器 (`subtitle_generator.py`)
**智能分析工具** - 基於歌詞文本和 AI 分析

**特色：**
- 使用 Gemini 2.0 Flash 模型
- 基於歌詞內容智能分配時間
- 支援音訊能量分析
- 分段處理長影片

**使用場景：**
- 已有歌詞文本
- 需要快速生成初版字幕

## 📋 詳細使用說明

### Whisper 模式 (推薦)

#### 模式 1: 生成字幕 + 燒錄影片
1. 選擇「生成字幕 + 燒錄影片」模式
2. 選擇影片檔案或勾選「使用 WAV 音訊檔案」
3. 選擇 Whisper 模型 (推薦 medium)
4. 設定語言 (日文選 `ja`)
5. 調整字幕樣式
6. 點擊「一鍵完成」

#### 模式 2: 僅燒錄現有字幕 ⭐
1. 選擇「僅燒錄現有字幕到影片」模式
2. 選擇影片檔案
3. 選擇現有的 SRT 字幕檔案
4. 設定輸出路徑
5. 點擊「僅燒錄字幕」

### 模型管理

#### Whisper 模型格式
- **新版格式**: `medium.pt`, `large.pt`
- **舊版格式**: `ggml-medium.bin`, `ggml-large.bin`
- 兩種格式都完全支援

#### 模型位置
- **預設位置**: `C:\Users\[用戶名]\.cache\whisper`
- **自訂位置**: 透過環境變數 `WHISPER_CACHE_DIR` 設定
- **管理工具**: 
  - 程式內建模型檢查功能
  - `move_whisper_models.bat` 一鍵移動工具
  - `find_whisper_models.py` 搜尋所有模型

## 🛠️ 進階功能

### 音訊處理優化
- 使用 WAV 檔案可獲得比影片檔案更高的識別精度
- 支援 48kHz 高品質音訊處理
- 自動音訊能量分析

### 字幕樣式自訂
- 字體大小調整
- 位置和邊距設定
- 自動日文字體下載
- 高品質文字渲染

### 批次處理
- 分段處理長影片 (>3分鐘自動分段)
- 智能時間軸合併
- 進度追蹤和錯誤處理

## 📁 專案結構

```
├── whisper_subtitle_gui.py      # 主要工具 - Whisper 字幕生成器
├── subtitle_editor.py           # 互動式字幕編輯器
├── subtitle_generator.py        # Gemini 字幕生成器
├── video_processor.py           # 影片處理核心
├── advanced_subtitle_generator.py # 進階字幕生成
├── start_whisper_gui.bat        # 啟動腳本
├── install_whisper.bat          # 安裝腳本
├── move_whisper_models.bat      # 模型移動工具
├── find_whisper_models.py       # 模型搜尋工具
├── config.json                  # 設定檔模板
├── requirements.txt             # Python 依賴
└── WHISPER_README.md           # Whisper 工具詳細說明
```

## 🔧 系統需求

- **Python 3.8+**
- **Windows 10/11** (主要測試平台)
- **記憶體**: 4GB+ (large 模型需要 8GB+)
- **硬碟空間**: 2GB+ (用於模型檔案)
- **網路連線**: 首次下載模型時需要

## 📦 依賴套件

- `openai-whisper` - 語音識別核心
- `google-generativeai` - Gemini AI 支援
- `opencv-python` - 影片處理
- `moviepy` - 影片編輯
- `Pillow` - 圖像處理 (日文字體支援)
- `pygame` - 音訊播放 (編輯器)
- `librosa` - 音訊分析
- `tkinter` - GUI 介面

## 🐛 常見問題

### Q: 找不到 Whisper 程式
A: 執行 `install_whisper.bat` 重新安裝

### Q: 字幕不準確
A: 嘗試使用更大的模型 (medium → large) 或使用 WAV 音訊檔案

### Q: 日文字幕顯示為問號
A: 程式會自動下載日文字體，請確保網路連線正常

### Q: 想要自訂模型存放位置
A: 三種方法：
1. 程式內勾選「自訂模型位置」
2. 執行 `move_whisper_models.bat` 一鍵移動
3. 手動設定環境變數 `WHISPER_CACHE_DIR`

### Q: 我的模型是 ggml-medium.bin 格式
A: 這是舊版 Whisper 模型格式，程式完全支援

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 🙏 致謝

- [OpenAI Whisper](https://github.com/openai/whisper) - 語音識別技術
- [Google Gemini](https://ai.google.dev/) - AI 文本分析
- [MoviePy](https://github.com/Zulko/moviepy) - 影片處理

---

⭐ 如果這個專案對你有幫助，請給個 Star！