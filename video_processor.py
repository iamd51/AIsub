#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from moviepy.editor import VideoFileClip, CompositeVideoClip
from typing import List, Dict
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import urllib.request

class VideoProcessor:
    def __init__(self, config_path: str = "config.json"):
        """初始化影片處理器"""
        self.config = self.load_config(config_path)
        self.font = self.load_japanese_font()
    
    def load_config(self, config_path: str) -> Dict:
        """載入設定檔"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"設定檔 {config_path} 不存在")
            sys.exit(1)
    
    def load_japanese_font(self):
        """載入支援日文的字體"""
        font_path = "NotoSansCJK-Regular.ttc"
        
        # 如果字體檔案不存在，嘗試下載
        if not os.path.exists(font_path):
            print("正在下載日文字體...")
            try:
                # 使用 Google Fonts 的 Noto Sans JP
                font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTC/NotoSansCJK-Regular.ttc"
                urllib.request.urlretrieve(font_url, font_path)
                print("字體下載完成")
            except Exception as e:
                print(f"字體下載失敗: {e}")
                print("將使用系統預設字體")
                return None
        
        try:
            font_size = self.config["subtitle_settings"]["font_size"]
            return ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"載入字體失敗: {e}")
            try:
                # 嘗試使用系統字體
                return ImageFont.truetype("msgothic.ttc", self.config["subtitle_settings"]["font_size"])
            except:
                print("使用預設字體")
                return ImageFont.load_default()
    
    def parse_srt_file(self, srt_path: str) -> List[Dict]:
        """解析 SRT 字幕檔案"""
        subtitles = []
        
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            blocks = content.split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # 解析時間軸
                    time_line = lines[1]
                    start_str, end_str = time_line.split(' --> ')
                    
                    start_time = self.srt_time_to_seconds(start_str)
                    end_time = self.srt_time_to_seconds(end_str)
                    
                    # 合併字幕文字（可能有多行）
                    text = '\n'.join(lines[2:])
                    
                    subtitles.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text
                    })
            
            return subtitles
            
        except Exception as e:
            print(f"解析 SRT 檔案錯誤: {e}")
            return []
    
    def srt_time_to_seconds(self, time_str: str) -> float:
        """將 SRT 時間格式轉換為秒數"""
        # 格式: 00:00:00,000
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        
        return h * 3600 + m * 60 + s + ms / 1000.0
    
    def create_subtitle_frame(self, frame: np.ndarray, text: str, video_size: tuple) -> np.ndarray:
        """在影片幀上添加字幕"""
        settings = self.config["subtitle_settings"]
        
        # 複製幀以避免修改原始數據
        frame_with_subtitle = frame.copy()
        
        # 轉換為 PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(frame_with_subtitle, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # 分割多行文字
        lines = text.split('\n')
        
        # 計算文字尺寸和位置
        line_height = int(settings["font_size"] * 1.2)
        total_height = line_height * len(lines)
        
        # 從底部開始計算位置
        start_y = video_size[1] - settings["margin"] - total_height
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # 計算文字尺寸
            if self.font:
                bbox = draw.textbbox((0, 0), line, font=self.font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                text_width = len(line) * settings["font_size"] // 2
                text_height = settings["font_size"]
            
            # 居中位置
            x = (video_size[0] - text_width) // 2
            y = start_y + i * line_height
            
            # 確保文字在畫面內
            y = max(0, min(y, video_size[1] - text_height - 10))
            
            # 添加黑色邊框（描邊效果）
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=self.font, fill=(0, 0, 0))
            
            # 添加白色文字
            draw.text((x, y), line, font=self.font, fill=(255, 255, 255))
        
        # 轉換回 OpenCV 格式
        frame_with_subtitle = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return frame_with_subtitle
    
    def burn_subtitles_to_video(self, video_path: str, srt_path: str, output_path: str):
        """將字幕燒錄到影片中"""
        print("開始燒錄字幕到影片...")
        
        try:
            # 載入影片
            video = VideoFileClip(video_path)
            print(f"影片尺寸: {video.size}")
            
            # 解析字幕
            subtitles = self.parse_srt_file(srt_path)
            if not subtitles:
                print("無法解析字幕檔案")
                return
            
            print(f"找到 {len(subtitles)} 個字幕片段")
            
            # 建立字幕索引
            subtitle_index = 0
            current_subtitle = None
            
            def add_subtitle_to_frame(get_frame, t):
                """為每一幀添加字幕的函數"""
                nonlocal subtitle_index, current_subtitle
                
                frame = get_frame(t)
                
                # 尋找當前時間對應的字幕
                current_subtitle = None
                for subtitle in subtitles:
                    if subtitle['start'] <= t <= subtitle['end']:
                        current_subtitle = subtitle
                        break
                
                # 如果有字幕，添加到幀上
                if current_subtitle:
                    frame = self.create_subtitle_frame(frame, current_subtitle['text'], video.size)
                
                return frame
            
            # 應用字幕到影片
            final_video = video.fl(add_subtitle_to_frame, apply_to=['mask'])
            
            # 輸出影片
            print("正在輸出影片...")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                bitrate='8000k',  # 高位元率保持品質
                ffmpeg_params=['-crf', '18']  # 高品質設定
            )
            
            # 清理資源
            video.close()
            final_video.close()
            
            print(f"字幕燒錄完成！輸出檔案: {output_path}")
            
        except Exception as e:
            print(f"燒錄字幕錯誤: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="影片字幕燒錄工具")
    parser.add_argument("--video", "-v", required=True, help="原始影片檔案")
    parser.add_argument("--srt", "-s", required=True, help="SRT 字幕檔案")
    parser.add_argument("--output", "-o", required=True, help="輸出影片檔案")
    parser.add_argument("--config", "-c", default="config.json", help="設定檔路徑")
    
    args = parser.parse_args()
    
    # 檢查檔案
    if not os.path.exists(args.video):
        print(f"影片檔案不存在: {args.video}")
        sys.exit(1)
    
    if not os.path.exists(args.srt):
        print(f"字幕檔案不存在: {args.srt}")
        sys.exit(1)
    
    # 處理影片
    processor = VideoProcessor(args.config)
    processor.burn_subtitles_to_video(args.video, args.srt, args.output)

if __name__ == "__main__":
    main()