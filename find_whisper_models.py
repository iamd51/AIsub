#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
from pathlib import Path

def find_whisper_models():
    """尋找系統中所有的 Whisper 模型"""
    print("🔍 搜尋 Whisper 模型檔案...")
    print("=" * 50)
    
    # 常見的搜尋位置
    search_paths = [
        os.path.expanduser("~/.cache/whisper"),
        os.path.expanduser("~/whisper_models"),
        os.path.expanduser("~/Downloads"),
        ".",  # 當前目錄
        "C:/whisper_models",
        "D:/whisper_models",
    ]
    
    # 檢查環境變數
    whisper_cache = os.environ.get('WHISPER_CACHE_DIR')
    if whisper_cache:
        search_paths.append(whisper_cache)
    
    found_models = []
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            print(f"\n📁 搜尋位置: {search_path}")
            
            # 搜尋新格式模型 (.pt)
            pt_files = glob.glob(os.path.join(search_path, "*.pt"))
            for pt_file in pt_files:
                if any(model in os.path.basename(pt_file).lower() 
                      for model in ['tiny', 'base', 'small', 'medium', 'large']):
                    size_mb = os.path.getsize(pt_file) / (1024 * 1024)
                    print(f"  ✅ {os.path.basename(pt_file)} ({size_mb:.1f} MB) [新格式]")
                    found_models.append((pt_file, 'new'))
            
            # 搜尋舊格式模型 (.bin)
            bin_files = glob.glob(os.path.join(search_path, "ggml-*.bin"))
            for bin_file in bin_files:
                size_mb = os.path.getsize(bin_file) / (1024 * 1024)
                print(f"  ✅ {os.path.basename(bin_file)} ({size_mb:.1f} MB) [舊格式]")
                found_models.append((bin_file, 'old'))
            
            # 搜尋其他可能的模型檔案
            other_bins = glob.glob(os.path.join(search_path, "*whisper*.bin"))
            for bin_file in other_bins:
                if not os.path.basename(bin_file).startswith('ggml-'):
                    size_mb = os.path.getsize(bin_file) / (1024 * 1024)
                    print(f"  ⚠️  {os.path.basename(bin_file)} ({size_mb:.1f} MB) [可能的模型]")
                    found_models.append((bin_file, 'unknown'))
    
    print("\n" + "=" * 50)
    print(f"📊 總共找到 {len(found_models)} 個模型檔案")
    
    if found_models:
        print("\n🎯 建議操作:")
        
        # 檢查是否有舊格式模型
        old_models = [m for m in found_models if m[1] == 'old']
        if old_models:
            print("1. 你有舊格式的模型檔案，這些都可以正常使用")
            print("2. 如果想統一管理，可以:")
            print("   - 將所有模型移動到同一個資料夾")
            print("   - 設定環境變數 WHISPER_CACHE_DIR 指向該資料夾")
        
        # 檢查是否有多個位置的模型
        locations = set(os.path.dirname(m[0]) for m in found_models)
        if len(locations) > 1:
            print("3. 模型分散在多個位置，建議整合到一個資料夾")
            print("4. 可以使用 move_whisper_models.bat 工具協助移動")
    
    else:
        print("❌ 沒有找到 Whisper 模型檔案")
        print("💡 建議:")
        print("1. 執行 Whisper 程式會自動下載模型")
        print("2. 或手動下載模型到指定位置")
    
    return found_models

if __name__ == "__main__":
    find_whisper_models()
    input("\n按 Enter 鍵結束...")