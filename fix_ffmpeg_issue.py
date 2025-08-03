#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修復 FFmpeg 缺失問題
解決 [WinError 2] 系統找不到指定的檔案 錯誤
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

def safe_print(text):
    """安全的列印函數"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', errors='ignore').decode('ascii')
        print(safe_text)

def check_ffmpeg():
    """檢查 FFmpeg 是否可用"""
    safe_print("🔍 檢查 FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            safe_print("✅ FFmpeg 已安裝並可用")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    safe_print("❌ FFmpeg 未找到或不可用")
    return False

def download_ffmpeg_windows():
    """下載並安裝 FFmpeg (Windows)"""
    safe_print("📥 正在下載 FFmpeg...")
    
    # FFmpeg 下載連結 (Windows 靜態版本)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    try:
        # 創建臨時目錄
        temp_dir = Path("temp_ffmpeg")
        temp_dir.mkdir(exist_ok=True)
        
        zip_path = temp_dir / "ffmpeg.zip"
        
        safe_print("⬇️ 下載中...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        safe_print("✅ 下載完成")
        
        # 解壓縮
        safe_print("📦 解壓縮中...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 找到 ffmpeg.exe
        ffmpeg_dirs = list(temp_dir.glob("ffmpeg-*"))
        if not ffmpeg_dirs:
            safe_print("❌ 解壓縮後找不到 FFmpeg 目錄")
            return False
        
        ffmpeg_dir = ffmpeg_dirs[0]
        ffmpeg_exe = ffmpeg_dir / "bin" / "ffmpeg.exe"
        
        if not ffmpeg_exe.exists():
            safe_print("❌ 找不到 ffmpeg.exe")
            return False
        
        # 複製到專案目錄
        project_dir = Path(__file__).parent
        target_path = project_dir / "ffmpeg.exe"
        
        shutil.copy2(ffmpeg_exe, target_path)
        safe_print(f"✅ FFmpeg 已安裝到: {target_path}")
        
        # 清理臨時檔案
        shutil.rmtree(temp_dir)
        safe_print("🧹 清理臨時檔案完成")
        
        return True
        
    except Exception as e:
        safe_print(f"❌ 下載失敗: {e}")
        return False

def add_ffmpeg_to_path():
    """將當前目錄添加到 PATH 環境變數"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 檢查是否已經在 PATH 中
    path_env = os.environ.get('PATH', '')
    if current_dir not in path_env:
        os.environ['PATH'] = current_dir + os.pathsep + path_env
        safe_print(f"✅ 已將 {current_dir} 添加到 PATH")
    else:
        safe_print("ℹ️ 目錄已在 PATH 中")

def create_ffmpeg_wrapper():
    """創建 FFmpeg 包裝腳本"""
    safe_print("📝 創建 FFmpeg 環境設定...")
    
    # 創建批次檔案來設定環境
    bat_content = f"""@echo off
REM FFmpeg 環境設定
set PATH=%~dp0;%PATH%
python "%~dp0whisper_subtitle_gui.py" %*
"""
    
    with open("start_with_ffmpeg.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    safe_print("✅ 已創建 start_with_ffmpeg.bat")

def test_whisper_with_ffmpeg():
    """測試 Whisper 是否能正常工作"""
    safe_print("🧪 測試 Whisper 功能...")
    
    try:
        import whisper
        safe_print("✅ Whisper 模組載入成功")
        
        # 嘗試載入最小模型
        safe_print("📥 測試模型載入...")
        model = whisper.load_model("tiny")
        safe_print("✅ 模型載入成功")
        
        return True
        
    except Exception as e:
        safe_print(f"❌ Whisper 測試失敗: {e}")
        return False

def fix_whisper_audio_loading():
    """修復 Whisper 音訊載入問題"""
    safe_print("🔧 修復 Whisper 音訊載入...")
    
    try:
        # 檢查是否有 ffmpeg.exe 在當前目錄
        current_dir = Path(__file__).parent
        ffmpeg_path = current_dir / "ffmpeg.exe"
        
        if ffmpeg_path.exists():
            # 設定環境變數指向本地 FFmpeg
            os.environ['FFMPEG_BINARY'] = str(ffmpeg_path)
            safe_print(f"✅ 設定 FFMPEG_BINARY: {ffmpeg_path}")
            
            # 也添加到 PATH
            add_ffmpeg_to_path()
            return True
        else:
            safe_print("❌ 找不到 ffmpeg.exe")
            return False
            
    except Exception as e:
        safe_print(f"❌ 修復失敗: {e}")
        return False

def main():
    """主函數"""
    safe_print("=" * 60)
    safe_print("    FFmpeg 問題修復工具")
    safe_print("    解決 [WinError 2] 系統找不到指定的檔案")
    safe_print("=" * 60)
    
    # 檢查作業系統
    if not sys.platform.startswith('win'):
        safe_print("❌ 此工具僅適用於 Windows 系統")
        safe_print("Linux/Mac 用戶請使用套件管理器安裝 FFmpeg:")
        safe_print("  Ubuntu/Debian: sudo apt install ffmpeg")
        safe_print("  macOS: brew install ffmpeg")
        return
    
    # 檢查 FFmpeg
    if check_ffmpeg():
        safe_print("✅ FFmpeg 已可用，無需修復")
        return
    
    safe_print("\n🔧 開始修復...")
    
    # 方法1: 檢查本地是否已有 ffmpeg.exe
    current_dir = Path(__file__).parent
    local_ffmpeg = current_dir / "ffmpeg.exe"
    
    if local_ffmpeg.exists():
        safe_print("✅ 找到本地 FFmpeg")
        if fix_whisper_audio_loading():
            safe_print("✅ 修復完成")
        else:
            safe_print("❌ 修復失敗")
        return
    
    # 方法2: 下載 FFmpeg
    safe_print("📥 嘗試下載 FFmpeg...")
    if download_ffmpeg_windows():
        safe_print("✅ FFmpeg 下載成功")
        
        # 設定環境
        if fix_whisper_audio_loading():
            safe_print("✅ 環境設定完成")
        
        # 創建啟動腳本
        create_ffmpeg_wrapper()
        
        # 測試功能
        if test_whisper_with_ffmpeg():
            safe_print("✅ 所有測試通過")
        
        safe_print("\n🎉 修復完成！")
        safe_print("📋 使用方法:")
        safe_print("  1. 直接運行: python whisper_subtitle_gui.py")
        safe_print("  2. 或使用: start_with_ffmpeg.bat")
        
    else:
        safe_print("❌ 自動下載失敗")
        safe_print("\n📋 手動解決方案:")
        safe_print("1. 下載 FFmpeg:")
        safe_print("   https://www.gyan.dev/ffmpeg/builds/")
        safe_print("2. 解壓縮後將 ffmpeg.exe 複製到程式目錄")
        safe_print("3. 或安裝到系統 PATH 中")
    
    safe_print("\n按任意鍵退出...")
    input()

if __name__ == "__main__":
    main()