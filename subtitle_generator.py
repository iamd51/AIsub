#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
from typing import List, Tuple, Dict
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import cv2
import numpy as np
from pydub import AudioSegment
import re

class SubtitleGenerator:
    def __init__(self, config_path: str = "config.json"):
        """初始化字幕生成器"""
        self.config = self.load_config(config_path)
        self.setup_gemini()
    
    def load_config(self, config_path: str) -> Dict:
        """載入設定檔"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"設定檔 {config_path} 不存在")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"設定檔 {config_path} 格式錯誤")
            sys.exit(1)
    
    def setup_gemini(self):
        """設定 Gemini API"""
        api_key = self.config.get("gemini_api_key")
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            print("請在 config.json 中設定正確的 Gemini API Key")
            sys.exit(1)
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.config.get("model_name", "gemini-pro"))
    
    def load_lyrics(self, lyrics_path: str) -> str:
        """載入歌詞檔案"""
        try:
            with open(lyrics_path, 'r', encoding='utf-8') as f:
                lyrics = f.read().strip()
            return lyrics
        except FileNotFoundError:
            print(f"歌詞檔案 {lyrics_path} 不存在")
            sys.exit(1)
    
    def get_video_duration(self, video_path: str) -> float:
        """取得影片長度"""
        try:
            with VideoFileClip(video_path) as video:
                return video.duration
        except Exception as e:
            print(f"無法讀取影片檔案: {e}")
            sys.exit(1)
    
    def analyze_audio_segments(self, video_path: str) -> List[Tuple[float, float]]:
        """分析音訊片段，找出歌唱部分"""
        try:
            with VideoFileClip(video_path) as video:
                audio = video.audio
                # 簡化版本：將整個音訊分成固定長度的片段
                duration = video.duration
                chunk_duration = self.config["audio_settings"]["chunk_duration"]
                
                segments = []
                current_time = 0
                while current_time < duration:
                    end_time = min(current_time + chunk_duration, duration)
                    segments.append((current_time, end_time))
                    current_time = end_time
                
                return segments
        except Exception as e:
            print(f"音訊分析錯誤: {e}")
            return []
    
    def generate_timing_with_gemini(self, lyrics: str, video_duration: float) -> List[Dict]:
        """使用 Gemini API 生成歌詞時間軸"""
        
        # 計算歌詞行數和平均時間
        lyrics_lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        avg_time_per_line = video_duration / len(lyrics_lines) if lyrics_lines else 3.0
        
        prompt = f"""
        請為以下日文歌詞分配精確的時間軸。這是一首 {video_duration:.1f} 秒的歌曲，共有 {len(lyrics_lines)} 行歌詞。

        歌詞內容：
        {lyrics}

        時間分配規則：
        1. 歌曲通常有前奏，第一行歌詞大約在 {video_duration * 0.1:.1f}-{video_duration * 0.2:.1f} 秒開始
        2. 每行歌詞平均顯示 {avg_time_per_line:.1f} 秒
        3. 考慮日文歌曲的節奏，通常是 4/4 拍
        4. 副歌部分節奏較快，主歌部分較慢
        5. 最後一行歌詞應該在 {video_duration * 0.9:.1f} 秒前結束
        6. 時間不能重疊，每行之間可以有 0.1-0.3 秒的間隔

        請按照以下 JSON 格式回傳，只要 JSON 不要其他文字：
        [
            {{"start_time": 10.5, "end_time": 14.2, "text": "第一行歌詞"}},
            {{"start_time": 14.5, "end_time": 18.1, "text": "第二行歌詞"}}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            # 提取 JSON 部分
            response_text = response.text.strip()
            
            # 尋找 JSON 陣列
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                timing_data = json.loads(json_str)
                return timing_data
            else:
                print("無法從 Gemini 回應中提取 JSON")
                return []
                
        except Exception as e:
            print(f"Gemini API 錯誤: {e}")
            return []
    
    def create_srt_file(self, timing_data: List[Dict], output_path: str):
        """建立 SRT 字幕檔案"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, item in enumerate(timing_data, 1):
                    start_time = self.seconds_to_srt_time(item['start_time'])
                    end_time = self.seconds_to_srt_time(item['end_time'])
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{item['text']}\n\n")
            
            print(f"字幕檔案已儲存至: {output_path}")
            
        except Exception as e:
            print(f"建立字幕檔案錯誤: {e}")
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """將秒數轉換為 SRT 時間格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"   
 
    def process_video(self, video_path: str, lyrics_path: str, output_path: str, burn_to_video: bool = False, video_output_path: str = None):
        """處理影片並生成字幕"""
        print("開始處理影片...")
        
        # 載入歌詞
        lyrics = self.load_lyrics(lyrics_path)
        print(f"已載入歌詞，共 {len(lyrics.splitlines())} 行")
        
        # 取得影片資訊
        video_duration = self.get_video_duration(video_path)
        print(f"影片長度: {video_duration:.2f} 秒")
        
        # 使用 Gemini 生成時間軸
        print("正在使用 Gemini API 分析歌詞時間軸...")
        timing_data = self.generate_timing_with_gemini(lyrics, video_duration)
        
        if not timing_data:
            print("無法生成時間軸，請檢查 API 設定")
            return
        
        print(f"已生成 {len(timing_data)} 個字幕片段")
        
        # 建立 SRT 檔案
        self.create_srt_file(timing_data, output_path)
        print("字幕生成完成！")
        
        # 如果需要燒錄到影片
        if burn_to_video and video_output_path:
            from video_processor import VideoProcessor
            processor = VideoProcessor()
            processor.burn_subtitles_to_video(video_path, output_path, video_output_path)

def main():
    parser = argparse.ArgumentParser(description="日文歌曲字幕生成器")
    parser.add_argument("--video", "-v", required=True, help="影片檔案路徑")
    parser.add_argument("--lyrics", "-l", required=True, help="歌詞檔案路徑")
    parser.add_argument("--output", "-o", required=True, help="輸出字幕檔案路徑")
    parser.add_argument("--config", "-c", default="config.json", help="設定檔路徑")
    parser.add_argument("--burn", "-b", action="store_true", help="將字幕燒錄到影片中")
    parser.add_argument("--video-output", "-vo", help="燒錄字幕後的影片輸出路徑")
    
    args = parser.parse_args()
    
    # 檢查檔案是否存在
    if not os.path.exists(args.video):
        print(f"影片檔案不存在: {args.video}")
        sys.exit(1)
    
    if not os.path.exists(args.lyrics):
        print(f"歌詞檔案不存在: {args.lyrics}")
        sys.exit(1)
    
    # 如果要燒錄字幕但沒指定輸出路徑
    if args.burn and not args.video_output:
        print("使用 --burn 參數時必須指定 --video-output 路徑")
        sys.exit(1)
    
    # 建立字幕生成器並處理
    generator = SubtitleGenerator(args.config)
    generator.process_video(args.video, args.lyrics, args.output, args.burn, args.video_output)

if __name__ == "__main__":
    main()