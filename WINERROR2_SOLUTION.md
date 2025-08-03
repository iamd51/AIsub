# [WinError 2] 完整解決方案

## 問題描述
在全新安裝的電腦上運行 AISUB 時出現：
```
❌ 單次轉錄失敗: [WinError 2] 系統找不到指定的檔案。
FileNotFoundError: [WinError 2] 系統找不到指定的檔案。
```

## 根本原因
**FFmpeg 缺失或無法被 Whisper 正確調用**

Whisper 在處理音訊時會調用 FFmpeg 來：
- 載入音訊檔案
- 轉換音訊格式
- 提取音訊數據

當系統找不到 FFmpeg 時，就會出現 `[WinError 2]` 錯誤。

## 🚀 快速解決方案

### 方法一：自動診斷和修復（推薦）
```bash
# 執行深度診斷
python diagnose_winerror2.py
# 或雙擊
diagnose_winerror2.bat
```

### 方法二：快速修復
```bash
# 快速檢查和修復
python quick_fix_ffmpeg.py

# 完整修復
python fix_ffmpeg_issue.py
# 或雙擊
fix_winerror2.bat
```

### 方法三：檢查安裝狀態
```bash
# 完整環境檢查
python check_installation.py
# 或雙擊
check_installation.bat
```

## 🔧 手動解決步驟

### 步驟 1：下載 FFmpeg
1. 訪問：https://www.gyan.dev/ffmpeg/builds/
2. 下載 "release essentials" 版本
3. 解壓縮到任意位置

### 步驟 2：安裝 FFmpeg
**選項 A：複製到程式目錄（推薦）**
```
1. 找到解壓縮後的 bin/ffmpeg.exe
2. 複製 ffmpeg.exe 到 AISUB 程式目錄
3. 重新啟動程式
```

**選項 B：添加到系統 PATH**
```
1. 將 FFmpeg 的 bin 目錄添加到系統 PATH
2. 重新啟動命令提示字元
3. 執行 ffmpeg -version 驗證
```

### 步驟 3：驗證安裝
```bash
# 檢查 FFmpeg
ffmpeg -version

# 檢查完整環境
python check_installation.py
```

## 🧪 測試和驗證

### 基本測試
```bash
# 測試 FFmpeg
ffmpeg -version

# 測試 Whisper 環境
python test_whisper_env.py
```

### 完整測試
```bash
# 啟動 GUI 進行實際測試
python whisper_subtitle_gui.py
```

## 🔍 深度診斷

如果基本解決方案無效，使用深度診斷：

```bash
python diagnose_winerror2.py
```

診斷工具會檢查：
- ✅ FFmpeg 基本功能
- ✅ FFmpeg 音訊處理
- ✅ Whisper 音訊載入
- ✅ 環境變數設定
- ✅ 檔案權限
- ✅ 路徑問題

## 📋 常見問題

### Q: 為什麼會出現這個錯誤？
A: Whisper 依賴 FFmpeg 處理音訊，Windows 系統預設不包含 FFmpeg。

### Q: 我已經安裝了 FFmpeg，為什麼還是出錯？
A: 可能的原因：
- FFmpeg 不在系統 PATH 中
- 權限問題
- 路徑包含特殊字符
- 環境變數設定錯誤

### Q: 下載很慢怎麼辦？
A: 可以手動下載：
1. 從官網下載 FFmpeg
2. 解壓縮後複製 ffmpeg.exe 到程式目錄
3. 重新啟動程式

### Q: 修復後還是出錯？
A: 嘗試以下步驟：
1. 以管理員身分執行程式
2. 檢查防毒軟體是否阻擋 FFmpeg
3. 重新安裝 Python 和 Whisper
4. 執行深度診斷工具

## 🛠️ 技術細節

### 環境變數設定
程式會自動設定：
```
PATH = 程式目錄 + 原有PATH
FFMPEG_BINARY = 程式目錄\ffmpeg.exe
FFPROBE_BINARY = 程式目錄\ffprobe.exe
```

### 檔案結構
```
AISUB/
├── whisper_subtitle_gui.py      # 主程式
├── ffmpeg.exe                   # FFmpeg 執行檔
├── diagnose_winerror2.py        # 診斷工具
├── fix_ffmpeg_issue.py          # 修復工具
├── check_installation.py        # 環境檢查
└── test_whisper_env.py          # 測試腳本（自動生成）
```

## ✅ 成功指標

修復成功後，你應該看到：
```
✅ FFmpeg 檢查通過
✅ 模型 large 載入成功 (設備: cuda)
🚀 開始轉錄...
```

而不是：
```
❌ 單次轉錄失敗: [WinError 2] 系統找不到指定的檔案。
```

## 🎯 預防措施

1. **保留 FFmpeg**：將 `ffmpeg.exe` 保留在程式目錄中
2. **定期檢查**：使用 `check_installation.py` 定期檢查環境
3. **備份設定**：保存工作的環境配置
4. **更新注意**：系統更新後重新檢查 FFmpeg 狀態

---

**按照以上步驟，[WinError 2] 問題應該可以完全解決！** 🎉

如果問題仍然存在，請執行 `diagnose_winerror2.py` 獲取詳細診斷資訊。