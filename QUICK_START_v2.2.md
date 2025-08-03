# AISUB v2.2 快速開始指南

## 🚀 30秒快速開始

### 新用戶
```bash
# 1. 下載專案
git clone https://github.com/iamd51/AIsub.git
cd AIsub

# 2. 安裝依賴
install_whisper.bat

# 3. 檢查環境
check_installation.bat

# 4. 修復問題（如有）
fix_winerror2.bat

# 5. 啟動程式
start_whisper_gui.bat
```

### 現有用戶升級
```bash
# 1. 更新代碼
git pull origin main

# 2. 檢查環境
python check_installation.py

# 3. 修復 FFmpeg（如需要）
python fix_ffmpeg_issue.py

# 4. 啟動程式
python whisper_subtitle_gui.py
```

## ✅ v2.2 新功能確認

### 1. GUI 滾動測試
- 啟動程式後，嘗試滑鼠滾輪滾動
- 查看日誌區域是否可以完整顯示
- 確認滾動條正常工作

### 2. FFmpeg 狀態檢查
```bash
python quick_fix_ffmpeg.py
```
應該看到：`✅ FFmpeg 已可用`

### 3. 語言自動偵測測試
```bash
python test_language_detection.py
```
應該看到：`✅ 所有測試通過！`

## 🎯 使用 WAV 檔案

### 自動語言偵測流程
1. **載入 WAV 檔案** - 點擊「瀏覽」選擇檔案
2. **保持語言設定為 'auto'** - 預設已設定
3. **點擊「生成字幕」** - 開始處理
4. **Whisper 自動偵測語言** - 支援 100 種語言
5. **查看處理日誌** - 現在可以完整滾動查看

### 支援的語言
- 中文 (zh) - 繁體/簡體自動識別
- 日文 (ja) - 包含歌曲和對話
- 英文 (en) - 各種口音
- 韓文 (ko) - K-pop 和對話
- 其他 96 種語言...

## 🔧 常見問題快速解決

### 問題 1: [WinError 2] 錯誤
**解決**: 執行 `fix_winerror2.bat`

### 問題 2: GUI 無法滾動
**解決**: v2.2 已修復，重新啟動程式

### 問題 3: 語言偵測不準確
**解決**: 
- 確認語言設定為 'auto'
- 使用較大的模型 (medium/large)
- 確保音訊品質良好

### 問題 4: 處理速度慢
**解決**:
- 檢查 GPU 加速是否啟用
- 使用較小的模型 (small/base)
- 關閉多次通過模式

## 📋 推薦設定

### 最佳品質設定
- **模型**: medium 或 large
- **語言**: auto (自動偵測)
- **內容類型**: auto
- **品質等級**: high
- **GPU 加速**: 啟用

### 快速處理設定
- **模型**: small 或 base
- **語言**: auto
- **內容類型**: speech
- **品質等級**: balanced
- **GPU 加速**: 啟用

## 🎉 享受 v2.2 的改善

### 使用者體驗提升
- ✅ 流暢的 GUI 滾動
- ✅ 自動 FFmpeg 修復
- ✅ 完整的處理日誌查看
- ✅ 智能語言偵測
- ✅ 一鍵問題解決

### 技術改進
- ✅ 重構的滾動機制
- ✅ 自動環境檢測
- ✅ 多重備援修復
- ✅ 完整的測試覆蓋

---

**需要幫助？** 查看 `FFMPEG_FIX_GUIDE.md` 或 `UPDATE_NOTES_v2.2.md`  
**遇到問題？** 執行 `python check_installation.py` 進行診斷