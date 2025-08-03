#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速修復 FFmpeg 問題
專門解決 [WinError 2] 系統找不到指定的檔案 錯誤
"""

import os
import sys
import subprocess
from pathlib import Path

def check_ffmpeg():
    """檢查 FFmpeg 是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def setup_local_ffmpeg():
    """設定本地 FFmpeg 環境"""
    script_dir = Path(__file__).parent
    ffmpeg_exe = script_dir / "ffmpeg.exe"
    
    if ffmpeg_exe.exists():
        # 設定環境變數
        current_path = os.environ.get('PATH', '')
        if str(script_dir) not in current_path:
            os.environ['PATH'] = str(script_dir) + os.pathsep + current_path
        
        os.environ['FFMPEG_BINARY'] = str(ffmpeg_exe)
        print(f"✅ 設定本地 FFmpeg: {ffmpeg_exe}")
        return True
    
    return False

def download_ffmpeg_portable():
    """下載便攜版 FFmpeg"""
    print("📥 下載便攜版 FFmpeg...")
    
    try:
        import urllib.request
        import zipfile
        
        # 使用較小的 FFmpeg 版本
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
        
        script_dir = Path(__file__).parent
        zip_path = script_dir / "ffmpeg_temp.zip"
        
        print("⬇️ 下載中...")
        urllib.request.urlretrieve(url, zip_path)
        
        print("📦 解壓縮中...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 只解壓縮 ffmpeg.exe
            for member in zip_ref.namelist():
                if member.endswith('ffmpeg.exe'):
                    # 提取到當前目錄
                    with zip_ref.open(member) as source, open(script_dir / "ffmpeg.exe", "wb") as target:
                        target.write(source.read())
                    break
        
        # 清理
        zip_path.unlink()
        
        print("✅ FFmpeg 下載完成")
        return True
        
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return False

def main():
    """主函數"""
    print("🔧 快速修復 FFmpeg 問題")
    print("=" * 40)
    
    # 檢查 FFmpeg
    if check_ffmpeg():
        print("✅ FFmpeg 已可用")
        return True
    
    print("❌ FFmpeg 不可用")
    
    # 嘗試設定本地 FFmpeg
    if setup_local_ffmpeg():
        if check_ffmpeg():
            print("✅ 本地 FFmpeg 設定成功")
            return True
    
    # 下載 FFmpeg
    if sys.platform.startswith('win'):
        print("📥 嘗試下載 FFmpeg...")
        if download_ffmpeg_portable():
            if setup_local_ffmpeg():
                print("✅ FFmpeg 安裝並設定完成")
                return True
    
    print("❌ 無法修復 FFmpeg 問題")
    print("💡 手動解決方案:")
    print("1. 下載 FFmpeg: https://ffmpeg.org/download.html")
    print("2. 將 ffmpeg.exe 複製到程式目錄")
    print("3. 或安裝到系統 PATH")
    
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\n按 Enter 鍵退出...")