# FFmpeg 問題修復指南

## 問題描述
在全新安裝的電腦上運行 AISUB 時出現以下錯誤：
```
❌ 單次轉錄失敗: [WinError 2] 系統找不到指定的檔案。
FileNotFoundError: [WinError 2] 系統找不到指定的檔案。
```

## 問題原因
這個錯誤是因為 **FFmpeg 缺失** 導致的。Whisper 需要 FFmpeg 來處理音訊檔案，但 Windows 系統預設不包含 FFmpeg。

## 解決方案

### 🚀 方法一：自動修復（推薦）
1. **執行自動修復腳本**：
   ```bash
   python fix_ffmpeg_issue.py
   ```
   或雙擊：
   ```
   fix_winerror2.bat
   ```

2. **腳本會自動**：
   - 檢查 FFmpeg 狀態
   - 下載便攜版 FFmpeg
   - 設定環境變數
   - 測試功能

### ⚡ 方法二：快速修復
```bash
python quick_fix_ffmpeg.py
```

### 🔧 方法三：手動安裝
1. **下載 FFmpeg**：
   - 訪問：https://www.gyan.dev/ffmpeg/builds/
   - 下載 "release essentials" 版本

2. **安裝步驟**：
   - 解壓縮下載的檔案
   - 找到 `ffmpeg.exe`（在 bin 資料夾中）
   - 將 `ffmpeg.exe` 複製到 AISUB 程式目錄

3. **驗證安裝**：
   ```bash
   ffmpeg -version
   ```

## 檢查安裝狀態

### 執行完整檢查
```bash
python check_installation.py
```
或雙擊：
```
check_installation.bat
```

檢查結果會顯示：
- ✅ FFmpeg 已安裝並可用
- ❌ FFmpeg 未找到

## 常見問題

### Q: 為什麼需要 FFmpeg？
A: Whisper 使用 FFmpeg 來：
- 載入和轉換音訊檔案
- 處理不同的音訊格式
- 提取影片中的音訊軌道

### Q: 下載很慢怎麼辦？
A: 可以手動下載：
1. 從 https://ffmpeg.org/download.html 下載
2. 解壓縮後將 `ffmpeg.exe` 複製到程式目錄
3. 重新啟動程式

### Q: 修復後還是出錯？
A: 檢查以下項目：
1. 確認 `ffmpeg.exe` 在程式目錄中
2. 重新啟動命令提示字元
3. 執行 `python check_installation.py` 確認狀態

## 技術細節

### 環境變數設定
修復腳本會自動設定：
```
PATH = 程式目錄 + 原有PATH
FFMPEG_BINARY = 程式目錄\ffmpeg.exe
```

### 檔案位置
- FFmpeg 執行檔：`程式目錄\ffmpeg.exe`
- 修復腳本：`fix_ffmpeg_issue.py`
- 檢查腳本：`check_installation.py`

## 驗證修復效果

修復完成後，重新運行 AISUB：
```bash
python whisper_subtitle_gui.py
```

應該看到：
- ✅ FFmpeg 檢查通過
- ✅ 模型載入成功
- 🚀 開始轉錄...

## 預防措施

為避免類似問題，建議：
1. 使用 `check_installation.bat` 定期檢查環境
2. 保留 `ffmpeg.exe` 在程式目錄中
3. 更新系統時重新檢查 FFmpeg 狀態

---

**修復完成後，AISUB 應該可以正常處理音訊和影片檔案！** 🎉