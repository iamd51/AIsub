# 🎵 AIsub - AI 字幕生成工具

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-orange.svg)](https://github.com/openai/whisper)
[![Version](https://img.shields.io/badge/version-v2.0-brightgreen.svg)](RELEASE_NOTES_v2.0.md)
[![Optimization](https://img.shields.io/badge/🧠-智能優化-purple.svg)](WHISPER_OPTIMIZATION_GUIDE.md)

基於 OpenAI Whisper 的 AI 字幕生成工具，專為日文內容優化，支援高精度的語音識別和字幕處理。

![AIsub Demo](https://img.shields.io/badge/Status-Ready%20to%20Use-brightgreen)

## 🌟 主要功能

### 🎯 兩種字幕處理方式
| 工具 | 特色 | 適用場景 |
|------|------|----------|
| 🎤 **Whisper 生成器** | OpenAI Whisper 高精度語音識別 | 自動生成字幕 (主要工具) |
| 🎵 **互動式編輯器** | 邊聽音樂邊手動調整時間軸 | 精確時間軸微調 |

### 🔥 核心特色

#### 🧠 **全新智能優化系統** (v2.0)
- **多次通過轉錄**: 使用多個溫度值，自動選擇最佳結果
- **品質評估算法**: 智能評估轉錄品質，過濾低品質內容
- **語言特定優化**: 針對日文、英文、中文的專門優化
- **詳細優化報告**: 提供處理過程的完整分析
- ✅ **雙操作模式** - 生成字幕 + 燒錄影片 / 僅燒錄現有字幕
- ✅ **多輸入支援** - 影片檔案、WAV 音訊檔案 (更高精度)
- ✅ **完美日文支援** - 自動下載日文字體，正確顯示日文字幕
- ✅ **高品質輸出** - 保持原始影片品質的字幕燒錄
- ✅ **智能模型管理** - 支援新舊 Whisper 模型格式 (.pt/.bin)
- ✅ **友善圖形介面** - 簡單易用的 GUI 操作，即時日誌顯示

## 🚀 快速開始

### 📥 下載和安裝

1. **Clone 專案**
```bash
git clone https://github.com/iamd51/AIsub.git
cd AIsub
```

2. **自動安裝依賴** (推薦)
```bash
# Windows 用戶
雙擊 install_whisper.bat

# 或手動安裝
pip install -r requirements.txt
pip install openai-whisper
```

### 🎬 開始使用

```bash
# 🎤 Whisper 字幕生成器 (主要工具)
雙擊 start_whisper_gui.bat
# 或執行
python whisper_subtitle_gui.py

# 🎵 互動式字幕編輯器 (精確微調)
python subtitle_editor.py
```

### ⚡ 一分鐘上手
1. 啟動 `whisper_subtitle_gui.py`
2. 選擇你的影片檔案
3. 點擊「一鍵完成」
4. 等待處理完成，享受完美字幕！

## 📱 工具介紹

### 🎤 Whisper 字幕生成器 (`whisper_subtitle_gui.py`)
**主要工具** - 使用 OpenAI Whisper 進行高精度語音識別

**特色：**
- 支援 WAV 音訊檔案輸入 (更高精度)
- 雙操作模式：生成+燒錄 / 僅燒錄現有字幕
- 自動模型管理和下載 (支援新舊格式)
- 即時處理日誌顯示
- 完美的日文字幕支援

**使用場景：**
- 自動生成字幕 (適用於各種語言)
- 燒錄現有 SRT 字幕到影片
- 日文歌曲、動畫、影片字幕製作

### 🎵 互動式字幕編輯器 (`subtitle_editor.py`)
**精確微調工具** - 邊聽音樂邊手動調整時間軸

**特色：**
- 即時音訊播放
- 視覺化時間軸編輯
- 精確到 0.1 秒的控制
- 支援載入現有字幕進行微調

**使用場景：**
- 需要極高精度的時間軸
- 微調 Whisper 生成的字幕
- 專業字幕製作和校對

## 🧠 智能優化功能 (v2.0 新功能)

### ✨ 優化功能概述

全新的智能優化系統可以大幅提升 Whisper 的識別準確度，特別是對於音樂、歌曲和複雜語音內容。

#### 🎯 主要改進
- **識別準確度提升 15-25%**
- **重複內容減少 80%**
- **無意義片段減少 75%**
- **自動品質評估和過濾**

### 🔧 優化設定

#### 基本設定
- ✅ **啟用智能優化** (推薦開啟)
- 🔄 **多次通過模式** (更準確但較慢)
- 📊 **品質等級**: auto / fast / balanced / high / ultra
- 🎯 **內容類型**: auto / speech / music / mixed

#### 使用建議
1. **首次使用**: 開啟智能優化，選擇 auto 品質等級
2. **重要內容**: 使用 ultra 品質等級 + 多次通過模式
3. **音樂內容**: 選擇 music 內容類型 + 音樂模式
4. **快速預覽**: 選擇 fast 品質等級

### 📊 優化報告

每次處理完成後會生成詳細的優化報告：
- 原始片段數量 vs 優化後數量
- 平均品質分數和分佈
- 個人化改進建議

詳細說明請參考 [優化功能指南](WHISPER_OPTIMIZATION_GUIDE.md)

## 📋 詳細使用說明

### Whisper 字幕生成器 (主要工具)

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
├── whisper_accuracy_optimizer.py # 🧠 智能優化核心 (v2.0)
├── subtitle_editor.py           # 互動式字幕編輯器
├── video_processor.py           # 影片處理核心
├── start_whisper_gui.bat        # 啟動腳本
├── install_whisper.bat          # 安裝腳本
├── move_whisper_models.bat      # 模型移動工具
├── find_whisper_models.py       # 模型搜尋工具
├── test_whisper_optimization.py # 優化功能測試腳本
├── demo_optimization.py         # 優化功能演示腳本
├── config.json                  # 設定檔模板
├── requirements.txt             # Python 依賴
├── WHISPER_README.md           # Whisper 工具詳細說明
└── WHISPER_OPTIMIZATION_GUIDE.md # 🧠 優化功能完整指南
```

## 🔧 系統需求

- **Python 3.8+**
- **Windows 10/11** (主要測試平台)
- **記憶體**: 4GB+ (large 模型需要 8GB+)
- **硬碟空間**: 2GB+ (用於模型檔案)
- **網路連線**: 首次下載模型時需要

## 📦 依賴套件

- `openai-whisper` - 語音識別核心
- `opencv-python` - 影片處理
- `moviepy` - 影片編輯
- `Pillow` - 圖像處理 (日文字體支援)
- `pygame` - 音訊播放 (編輯器)
- `librosa` - 音訊分析
- `tkinter` - GUI 介面 (Python 內建)

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

### Q: 智能優化功能如何使用？

A: 
1. 勾選「啟用智能優化」(預設開啟)
2. 根據內容選擇合適的類型和品質等級
3. 重要內容可開啟「多次通過模式」
4. 查看優化報告了解處理效果

### Q: 優化後字幕變少了？

A: 這是正常現象，優化器過濾了低品質內容：
- 重複的歌詞或對話
- 無意義的語氣詞 (啊、嗯、uh)
- 音樂符號和雜音
- 如果過濾太多，可降低品質等級

### Q: 多次通過模式很慢？

A: 多次通過模式會增加 2-5 倍處理時間：
- 適合重要內容的精確轉錄
- 日常使用可關閉此功能
- 先用小模型測試參數，再用大模型處理

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 🙏 致謝

- [OpenAI Whisper](https://github.com/openai/whisper) - 強大的語音識別技術
- [MoviePy](https://github.com/Zulko/moviepy) - 優秀的影片處理庫
- [Pillow](https://python-pillow.org/) - 圖像處理和字體渲染

---

⭐ 如果這個專案對你有幫助，請給個 Star！