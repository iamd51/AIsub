# v2.2: 修復 GUI 滾動問題和 FFmpeg 缺失錯誤

## 🔧 主要修復

### GUI 滾動功能修復
- 修復 GUI 無法往下滾動查看處理日誌的問題
- 重構滾動機制，使用 Canvas + Scrollbar 實現完整滾動
- 加強滑鼠滾輪支援，遞歸綁定到所有子元件
- 增加日誌區域高度從 6 行到 12 行
- 優化視窗大小從 1000x800 到 1000x900
- 添加滾動區域自動更新機制

### FFmpeg 缺失問題解決
- 解決全新安裝電腦出現的 [WinError 2] 錯誤
- 創建自動 FFmpeg 下載和安裝工具
- GUI 啟動時自動檢查 FFmpeg 狀態
- 提供一鍵修復批次檔案
- 更新安裝檢查腳本，加入 FFmpeg 檢測

### UI 介面優化
- 修復重複的語言選擇下拉選單
- 統一語言選項順序和內容
- 改善元件佈局和間距

## 📁 新增檔案
- fix_ffmpeg_issue.py - 完整 FFmpeg 自動安裝工具
- quick_fix_ffmpeg.py - 快速 FFmpeg 檢查修復
- fix_winerror2.bat - Windows 一鍵修復批次檔案
- test_language_detection.py - 語言自動偵測功能測試
- test_gui_scroll.py - GUI 滾動功能測試
- FFMPEG_FIX_GUIDE.md - FFmpeg 問題完整解決指南
- GUI_SCROLL_FIX_SUMMARY.md - GUI 滾動修復技術總結
- UPDATE_NOTES_v2.2.md - 詳細更新說明

## 🔄 修改檔案
- whisper_subtitle_gui.py - 重構滾動機制，加入 FFmpeg 檢查
- check_installation.py - 新增 FFmpeg 檢查功能
- WHISPER_README.md - 更新版本資訊和故障排除

## ✅ 功能驗證
- 確認語言自動偵測功能正常 (支援 100 種語言)
- WAV 檔案載入時會自動偵測語言
- 所有測試腳本驗證通過

## 🎯 使用者體驗改善
- 解決了兩個最常見的使用問題
- 提供完整的自動修復解決方案
- 改善新用戶的安裝和使用體驗