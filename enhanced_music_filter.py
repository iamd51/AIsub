#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增強版音樂字幕過濾器
整合到主程式中，防止生成包含無關內容的字幕
"""

import re
from typing import List, Dict, Any

class EnhancedMusicFilter:
    """增強版音樂字幕過濾器"""
    
    def __init__(self):
        # 音樂元數據關鍵詞
        self.music_metadata_keywords = [
            "作詞", "作曲", "編曲", "作詞・作曲・編曲",
            "初音ミク", "ボーカロイド", "VOCALOID",
            "Composer", "Lyricist", "Arranger",
            "Music by", "Lyrics by", "Arranged by",
            "Original", "Cover", "Remix"
        ]
        
        # 音樂符號
        self.music_symbols = ["♪", "♫", "♬", "♩", "🎵", "🎶"]
        
        # 重複詞彙檢測閾值
        self.repeat_threshold = 3
        
        # 無意義內容長度閾值
        self.meaningless_length_threshold = 50
    
    def is_music_metadata(self, text: str) -> bool:
        """檢查是否為音樂元數據"""
        text_lower = text.lower()
        
        # 檢查關鍵詞
        for keyword in self.music_metadata_keywords:
            if keyword.lower() in text_lower:
                return True
        
        # 檢查是否主要由音樂符號組成
        symbol_count = sum(text.count(symbol) for symbol in self.music_symbols)
        if symbol_count > len(text) * 0.3:  # 超過30%是音樂符號
            return True
        
        return False
    
    def has_excessive_repetition(self, text: str) -> bool:
        """檢查是否有過度重複"""
        words = text.split()
        if len(words) <= 3:
            return False
        
        # 統計詞彙出現次數
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # 檢查最大重複次數
        max_repeat = max(word_counts.values()) if word_counts else 0
        return max_repeat > self.repeat_threshold
    
    def clean_music_metadata(self, text: str) -> str:
        """清理音樂元數據"""
        # 音樂製作相關的正則表達式
        patterns = [
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
            r"Original.*by.*",
        ]
        
        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)
        
        # 移除過多的重複字符
        cleaned_text = re.sub(r"(.)\1{4,}", r"\1", cleaned_text)
        
        # 移除只包含符號的行
        lines = cleaned_text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not re.match(r'^[♪♫♬♩・･\-_=\s]+$', line):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def should_filter_segment(self, text: str) -> tuple[bool, str]:
        """
        判斷是否應該過濾這個片段
        返回 (是否過濾, 原因)
        """
        if not text or not text.strip():
            return True, "空內容"
        
        # 檢查音樂元數據
        if self.is_music_metadata(text):
            if len(text) < self.meaningless_length_threshold or text.count("作詞") > 1:
                return True, "音樂元數據"
        
        # 檢查過度重複
        if self.has_excessive_repetition(text):
            return True, "過度重複"
        
        # 檢查是否主要由符號組成
        non_symbol_chars = sum(1 for char in text if char not in "♪♫♬♩・･\-_=\s\n")
        if non_symbol_chars < len(text) * 0.3:
            return True, "主要為符號"
        
        return False, "保留"
    
    def filter_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """過濾字幕片段列表"""
        filtered_segments = []
        
        for segment in segments:
            text = segment.get("text", "").strip()
            
            # 先清理文字
            cleaned_text = self.clean_music_metadata(text)
            
            # 判斷是否應該過濾
            should_filter, reason = self.should_filter_segment(cleaned_text)
            
            if not should_filter:
                # 更新清理後的文字
                segment["text"] = cleaned_text
                filtered_segments.append(segment)
            else:
                print(f"🚫 過濾片段 ({reason}): {text[:30]}...")
        
        return filtered_segments
    
    def filter_srt_content(self, srt_content: str) -> str:
        """過濾SRT字幕內容"""
        # 解析SRT內容
        segments = self.parse_srt(srt_content)
        
        # 過濾片段
        filtered_segments = self.filter_segments(segments)
        
        # 重新生成SRT
        return self.generate_srt(filtered_segments)
    
    def parse_srt(self, srt_content: str) -> List[Dict[str, Any]]:
        """解析SRT內容為片段列表"""
        segments = []
        blocks = re.split(r'\n\s*\n', srt_content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                number = int(lines[0])
                timestamp = lines[1]
                text = '\n'.join(lines[2:])
                
                # 解析時間戳
                time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', timestamp)
                if time_match:
                    start_time = time_match.group(1)
                    end_time = time_match.group(2)
                    
                    segments.append({
                        "number": number,
                        "start": start_time,
                        "end": end_time,
                        "text": text
                    })
            except (ValueError, IndexError):
                continue
        
        return segments
    
    def generate_srt(self, segments: List[Dict[str, Any]]) -> str:
        """從片段列表生成SRT內容"""
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            srt_lines.append(str(i))
            srt_lines.append(f"{segment['start']} --> {segment['end']}")
            srt_lines.append(segment['text'])
            srt_lines.append("")  # 空行分隔
        
        return '\n'.join(srt_lines).strip()

# 全域實例
enhanced_filter = EnhancedMusicFilter()

def filter_music_content(text: str) -> tuple[bool, str]:
    """
    過濾音樂相關無關內容的便捷函數
    返回 (是否保留, 清理後的文字)
    """
    cleaned_text = enhanced_filter.clean_music_metadata(text)
    should_filter, reason = enhanced_filter.should_filter_segment(cleaned_text)
    
    if should_filter:
        return False, ""
    else:
        return True, cleaned_text

def filter_srt_file(input_file: str, output_file: str = None) -> bool:
    """
    過濾SRT檔案的便捷函數
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filtered_content = enhanced_filter.filter_srt_content(content)
        
        if output_file is None:
            output_file = input_file.replace('.srt', '_filtered.srt')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(filtered_content)
        
        return True
    except Exception as e:
        print(f"過濾SRT檔案失敗: {e}")
        return False