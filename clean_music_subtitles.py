#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音樂字幕清理工具
專門清理包含「作詞・作曲・編曲 初音ミク」等無關內容的字幕檔案
"""

import os
import re
import sys
from pathlib import Path

def clean_srt_content(srt_content):
    """清理SRT字幕內容"""
    
    # 音樂元數據過濾模式
    music_metadata_patterns = [
        r"作詞[・･]?作曲[・･]?編曲.*",
        r"作詞.*作曲.*編曲.*",
        r"初音ミク.*",
        r"VOCALOID.*",
        r"ボーカロイド.*",
        r"Composer:.*",
        r"Lyricist:.*", 
        r"Arranger:.*",
        r"Music by.*",
        r"Lyrics by.*",
    ]
    
    # 分割成字幕塊
    subtitle_blocks = re.split(r'\n\s*\n', srt_content.strip())
    cleaned_blocks = []
    
    for block in subtitle_blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 3:  # 不完整的字幕塊
            continue
            
        # 提取序號、時間軸和文字
        try:
            number = lines[0]
            timestamp = lines[1]
            text_lines = lines[2:]
            text = '\n'.join(text_lines)
            
            # 清理文字內容
            original_text = text
            
            # 1. 移除音樂元數據
            for pattern in music_metadata_patterns:
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)
            
            # 2. 移除過多的重複字符
            text = re.sub(r"(.)\1{4,}", r"\1", text)
            
            # 3. 移除只包含符號的內容
            text = re.sub(r'^[♪♫♬♩・･\-_=\s]+$', '', text, flags=re.MULTILINE)
            
            # 4. 檢查重複詞彙
            words = text.split()
            if len(words) > 3:
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                max_repeat = max(word_counts.values()) if word_counts else 0
                
                # 如果有詞彙重複超過3次，可能是錯誤識別
                if max_repeat > 3:
                    print(f"⚠️ 發現重複內容: {original_text[:50]}...")
                    continue
            
            # 5. 檢查無意義內容
            meaningless_keywords = [
                "作詞", "作曲", "編曲", "初音ミク", "ボーカロイド", "VOCALOID"
            ]
            
            is_meaningless = any(keyword in text for keyword in meaningless_keywords)
            if is_meaningless and (len(text.strip()) < 50 or text.count("作詞") > 1):
                print(f"⚠️ 跳過無意義內容: {original_text[:30]}...")
                continue
            
            # 6. 清理空白和格式
            text = re.sub(r'\n+', '\n', text)  # 移除多餘換行
            text = text.strip()
            
            # 如果清理後還有內容，保留這個字幕塊
            if text:
                cleaned_block = f"{number}\n{timestamp}\n{text}"
                cleaned_blocks.append(cleaned_block)
            else:
                print(f"⚠️ 字幕塊已完全清理: {original_text[:30]}...")
                
        except Exception as e:
            print(f"❌ 處理字幕塊時出錯: {e}")
            continue
    
    # 重新編號
    final_blocks = []
    for i, block in enumerate(cleaned_blocks, 1):
        lines = block.split('\n')
        lines[0] = str(i)  # 重新編號
        final_blocks.append('\n'.join(lines))
    
    return '\n\n'.join(final_blocks)

def clean_subtitle_file(input_file, output_file=None):
    """清理字幕檔案"""
    
    if not os.path.exists(input_file):
        print(f"❌ 檔案不存在: {input_file}")
        return False
    
    # 如果沒有指定輸出檔案，自動生成
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"
    
    try:
        # 讀取原始檔案
        with open(input_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        print(f"📁 處理檔案: {input_file}")
        # 計算原始字幕塊數量
        pattern = r'\d+\n\d{2}:\d{2}:\d{2},\d{3}'
        original_blocks = len(re.findall(pattern, original_content))
        print(f"📊 原始字幕塊數量: {original_blocks}")
        
        # 清理內容
        cleaned_content = clean_srt_content(original_content)
        
        if not cleaned_content.strip():
            print("⚠️ 清理後沒有剩餘內容")
            return False
        
        # 寫入清理後的檔案
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        # 計算清理後字幕塊數量
        cleaned_blocks = len(re.findall(pattern, cleaned_content))
        print(f"✅ 清理完成: {output_file}")
        print(f"📊 清理後字幕塊數量: {cleaned_blocks}")
        
        return True
        
    except Exception as e:
        print(f"❌ 處理失敗: {e}")
        return False

def batch_clean_subtitles(directory):
    """批量清理目錄中的所有SRT檔案"""
    
    srt_files = list(Path(directory).glob("*.srt"))
    
    if not srt_files:
        print(f"❌ 在 {directory} 中找不到SRT檔案")
        return
    
    print(f"📁 找到 {len(srt_files)} 個SRT檔案")
    
    success_count = 0
    for srt_file in srt_files:
        if "_cleaned" in srt_file.name:
            print(f"⏭️ 跳過已清理的檔案: {srt_file.name}")
            continue
            
        if clean_subtitle_file(str(srt_file)):
            success_count += 1
        print("-" * 50)
    
    print(f"🎉 批量清理完成: {success_count}/{len(srt_files)} 個檔案成功處理")

def main():
    """主函數"""
    print("🧹 音樂字幕清理工具")
    print("=" * 60)
    print("專門清理包含「作詞・作曲・編曲 初音ミク」等無關內容的字幕")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # 命令列模式
        input_path = sys.argv[1]
        
        if os.path.isfile(input_path) and input_path.endswith('.srt'):
            # 單個檔案
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            clean_subtitle_file(input_path, output_path)
        elif os.path.isdir(input_path):
            # 目錄批量處理
            batch_clean_subtitles(input_path)
        else:
            print("❌ 請提供有效的SRT檔案或目錄路徑")
    else:
        # 互動模式
        print("請選擇處理模式:")
        print("1. 清理單個SRT檔案")
        print("2. 批量清理目錄中的所有SRT檔案")
        print("3. 清理當前目錄中的所有SRT檔案")
        
        choice = input("\n請輸入選擇 (1-3): ").strip()
        
        if choice == "1":
            input_file = input("請輸入SRT檔案路徑: ").strip().strip('"')
            output_file = input("請輸入輸出檔案路徑 (留空自動生成): ").strip().strip('"')
            output_file = output_file if output_file else None
            clean_subtitle_file(input_file, output_file)
            
        elif choice == "2":
            directory = input("請輸入目錄路徑: ").strip().strip('"')
            batch_clean_subtitles(directory)
            
        elif choice == "3":
            batch_clean_subtitles(".")
            
        else:
            print("❌ 無效的選擇")
    
    print("\n按任意鍵退出...")
    input()

if __name__ == "__main__":
    main()