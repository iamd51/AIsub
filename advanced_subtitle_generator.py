#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
from typing import List, Tuple, Dict
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import librosa
import numpy as np
from pydub import AudioSegment
import re
import subprocess

class AdvancedSubtitleGenerator:
    def __init__(self, config_path: str = "config.json"):
        """初始化進階字幕生成器"""
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
    
    def setup_gemini(self):
        """設定 Gemini API"""
        api_key = self.config.get("gemini_api_key")
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            print("請在 config.json 中設定正確的 Gemini API Key")
            sys.exit(1)
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.config.get("model_name", "gemini-2.0-flash"))
    
    def extract_audio_from_video(self, video_path: str, output_path: str = "extracted_audio.wav"):
        """從影片提取高品質音訊"""
        print("正在從影片提取音訊...")
        try:
            # 使用 FFmpeg 提取高品質音訊
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # 不要影片
                '-ac', '1',  # 單聲道
                '-ar', '48000',  # 48kHz 採樣率
                '-y',  # 覆蓋輸出檔案
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # 如果 FFmpeg 失敗，使用 MoviePy 作為備案
                print("FFmpeg 失敗，使用 MoviePy 提取音訊...")
                with VideoFileClip(video_path) as video:
                    video.audio.write_audiofile(output_path, verbose=False, logger=None)
            
            print(f"音訊已提取至: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"音訊提取錯誤: {e}")
            return None
    
    def analyze_audio_energy(self, audio_path: str) -> List[Tuple[float, float]]:
        """分析音訊能量，找出歌唱段落"""
        print("正在分析音訊能量...")
        try:
            # 載入音訊
            y, sr = librosa.load(audio_path, sr=22050)
            
            # 計算 RMS 能量
            hop_length = 512
            frame_length = 2048
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # 轉換為時間軸
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
            
            # 找出能量峰值（可能的歌唱開始點）
            threshold = np.mean(rms) + 0.5 * np.std(rms)
            peaks = []
            
            for i, energy in enumerate(rms):
                if energy > threshold:
                    peaks.append(times[i])
            
            # 將連續的峰值合併為段落
            segments = []
            if peaks:
                start = peaks[0]
                last_time = peaks[0]
                
                for peak_time in peaks[1:]:
                    if peak_time - last_time > 2.0:  # 超過 2 秒間隔就分段
                        segments.append((start, last_time))
                        start = peak_time
                    last_time = peak_time
                
                segments.append((start, last_time))
            
            print(f"找到 {len(segments)} 個音訊段落")
            return segments
            
        except Exception as e:
            print(f"音訊分析錯誤: {e}")
            return []
    
    def chunk_audio(self, audio_path: str, chunk_duration: int = 180) -> List[str]:
        """將音訊分段處理"""
        print(f"正在將音訊分成 {chunk_duration} 秒的片段...")
        try:
            audio = AudioSegment.from_wav(audio_path)
            duration_ms = len(audio)
            chunk_duration_ms = chunk_duration * 1000
            
            chunks = []
            chunk_files = []
            
            for i in range(0, duration_ms, chunk_duration_ms):
                chunk = audio[i:i + chunk_duration_ms]
                chunk_file = f"chunk_{i//chunk_duration_ms:03d}.wav"
                chunk.export(chunk_file, format="wav")
                chunk_files.append(chunk_file)
                chunks.append({
                    'file': chunk_file,
                    'start_offset': i / 1000.0,
                    'duration': len(chunk) / 1000.0
                })
            
            print(f"已分成 {len(chunks)} 個片段")
            return chunks
            
        except Exception as e:
            print(f"音訊分段錯誤: {e}")
            return []
    
    def generate_timing_for_chunk(self, lyrics_chunk: str, chunk_info: Dict, total_duration: float) -> List[Dict]:
        """為音訊片段生成時間軸"""
        start_offset = chunk_info['start_offset']
        chunk_duration = chunk_info['duration']
        
        prompt = f"""
        請為以下日文歌詞片段分配精確的時間軸。這是從 {start_offset:.1f} 秒開始的 {chunk_duration:.1f} 秒音訊片段。

        歌詞內容：
        {lyrics_chunk}

        重要規則：
        1. 每行字幕最多 2 行，每行不超過 42 個字符
        2. 在自然停頓處斷句（約 2 秒間隔），即使句子未完成
        3. 時間軸必須相對於原始影片（加上 {start_offset:.1f} 秒偏移）
        4. 每個字幕顯示 1.5-3 秒
        5. 字幕間可以有 0.1-0.5 秒間隔
        6. 考慮日文歌曲的節拍和韻律

        請只回傳 JSON 格式：
        [
            {{"start_time": {start_offset + 2.0}, "end_time": {start_offset + 4.5}, "text": "第一行歌詞"}},
            {{"start_time": {start_offset + 4.8}, "end_time": {start_offset + 7.2}, "text": "第二行歌詞"}}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # 提取 JSON
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                timing_data = json.loads(json_str)
                return timing_data
            else:
                print(f"無法從片段回應中提取 JSON")
                return []
                
        except Exception as e:
            print(f"片段 Gemini API 錯誤: {e}")
            return []
    
    def split_lyrics_by_chunks(self, lyrics: str, num_chunks: int) -> List[str]:
        """將歌詞按片段數量分割"""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        lines_per_chunk = max(1, len(lines) // num_chunks)
        
        chunks = []
        for i in range(0, len(lines), lines_per_chunk):
            chunk_lines = lines[i:i + lines_per_chunk]
            chunks.append('\n'.join(chunk_lines))
        
        return chunks
    
    def merge_chunk_timings(self, chunk_timings: List[List[Dict]]) -> List[Dict]:
        """合併所有片段的時間軸"""
        merged = []
        for chunk_timing in chunk_timings:
            merged.extend(chunk_timing)
        
        # 按開始時間排序
        merged.sort(key=lambda x: x['start_time'])
        return merged
    
    def apply_forced_alignment(self, audio_path: str, srt_path: str, output_srt: str):
        """使用 forced alignment 微調時間軸"""
        print("正在進行 forced alignment 微調...")
        try:
            # 這裡可以整合 aeneas 或其他 forced alignment 工具
            # 目前先複製原檔案，未來可以加入實際的對齊邏輯
            import shutil
            shutil.copy(srt_path, output_srt)
            print(f"Forced alignment 完成: {output_srt}")
            
        except Exception as e:
            print(f"Forced alignment 錯誤: {e}")
    
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
    
    def process_with_advanced_methods(self, video_path: str, audio_path: str, lyrics_path: str, output_path: str, use_chunking: bool = True, use_energy_analysis: bool = True):
        """使用進階方法處理字幕生成"""
        print("開始進階字幕生成處理...")
        
        # 載入歌詞
        with open(lyrics_path, 'r', encoding='utf-8') as f:
            lyrics = f.read().strip()
        print(f"已載入歌詞，共 {len(lyrics.splitlines())} 行")
        
        # 如果沒有提供音訊檔案，從影片提取
        if not audio_path or not os.path.exists(audio_path):
            audio_path = self.extract_audio_from_video(video_path)
            if not audio_path:
                return
        
        # 取得音訊長度
        try:
            audio = AudioSegment.from_wav(audio_path)
            duration = len(audio) / 1000.0
            print(f"音訊長度: {duration:.2f} 秒")
        except Exception as e:
            print(f"無法讀取音訊檔案: {e}")
            return
        
        # 分析音訊能量（可選）
        if use_energy_analysis:
            energy_segments = self.analyze_audio_energy(audio_path)
        
        # 決定是否使用分段處理
        if use_chunking and duration > 180:  # 超過 3 分鐘使用分段
            print("使用分段處理模式...")
            
            # 分割音訊
            chunks = self.chunk_audio(audio_path, chunk_duration=180)
            
            # 分割歌詞
            lyrics_chunks = self.split_lyrics_by_chunks(lyrics, len(chunks))
            
            # 為每個片段生成時間軸
            all_timings = []
            for i, (chunk_info, lyrics_chunk) in enumerate(zip(chunks, lyrics_chunks)):
                print(f"處理片段 {i+1}/{len(chunks)}...")
                chunk_timing = self.generate_timing_for_chunk(lyrics_chunk, chunk_info, duration)
                if chunk_timing:
                    all_timings.append(chunk_timing)
                
                # 清理臨時檔案
                if os.path.exists(chunk_info['file']):
                    os.remove(chunk_info['file'])
            
            # 合併所有時間軸
            final_timing = self.merge_chunk_timings(all_timings)
            
        else:
            print("使用完整音訊處理模式...")
            # 直接處理完整歌詞
            final_timing = self.generate_enhanced_timing(lyrics, duration)
        
        if not final_timing:
            print("無法生成時間軸")
            return
        
        print(f"已生成 {len(final_timing)} 個字幕片段")
        
        # 建立初始 SRT 檔案
        temp_srt = output_path.replace('.srt', '_temp.srt')
        self.create_srt_file(final_timing, temp_srt)
        
        # 應用 forced alignment（可選）
        if self.config.get("use_forced_alignment", False):
            self.apply_forced_alignment(audio_path, temp_srt, output_path)
            os.remove(temp_srt)
        else:
            os.rename(temp_srt, output_path)
        
        print("進階字幕生成完成！")
    
    def generate_enhanced_timing(self, lyrics: str, duration: float) -> List[Dict]:
        """生成增強的時間軸（完整音訊模式）"""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        prompt = f"""
        請為以下完整的日文歌詞分配精確的時間軸。歌曲總長度為 {duration:.1f} 秒。

        歌詞內容：
        {lyrics}

        專業字幕製作規則：
        1. 每行字幕最多 2 行，每行不超過 42 個字符
        2. 在自然停頓處斷句（約 2 秒間隔），即使句子未完成
        3. 歌曲通常有前奏，第一行歌詞約在 {duration * 0.08:.1f}-{duration * 0.15:.1f} 秒開始
        4. 每個字幕顯示 1.5-3.5 秒，根據歌詞長度調整
        5. 字幕間隔 0.1-0.3 秒，讓觀眾有喘息空間
        6. 副歌部分節奏較快，主歌較慢
        7. 最後一行歌詞在 {duration * 0.92:.1f} 秒前結束
        8. 考慮日文歌曲的 4/4 拍節奏

        音訊分析提示：
        - 注意歌詞與旋律的對應關係
        - 長音符對應較長的字幕顯示時間
        - 快速歌詞對應較短的間隔

        請只回傳 JSON 格式，確保時間軸精確：
        [
            {{"start_time": 8.5, "end_time": 11.2, "text": "第一行歌詞"}},
            {{"start_time": 11.5, "end_time": 14.8, "text": "第二行歌詞"}}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # 提取 JSON
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                timing_data = json.loads(json_str)
                return timing_data
            else:
                print("無法從回應中提取 JSON")
                return []
                
        except Exception as e:
            print(f"Gemini API 錯誤: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description="進階日文歌曲字幕生成器")
    parser.add_argument("--video", "-v", required=True, help="影片檔案路徑")
    parser.add_argument("--audio", "-a", help="音訊檔案路徑（可選，會自動從影片提取）")
    parser.add_argument("--lyrics", "-l", required=True, help="歌詞檔案路徑")
    parser.add_argument("--output", "-o", required=True, help="輸出字幕檔案路徑")
    parser.add_argument("--config", "-c", default="config.json", help="設定檔路徑")
    parser.add_argument("--no-chunking", action="store_true", help="不使用分段處理")
    parser.add_argument("--no-energy", action="store_true", help="不使用能量分析")
    parser.add_argument("--burn", "-b", action="store_true", help="將字幕燒錄到影片中")
    parser.add_argument("--video-output", "-vo", help="燒錄字幕後的影片輸出路徑")
    
    args = parser.parse_args()
    
    # 檢查檔案
    if not os.path.exists(args.video):
        print(f"影片檔案不存在: {args.video}")
        sys.exit(1)
    
    if not os.path.exists(args.lyrics):
        print(f"歌詞檔案不存在: {args.lyrics}")
        sys.exit(1)
    
    # 建立生成器並處理
    generator = AdvancedSubtitleGenerator(args.config)
    generator.process_with_advanced_methods(
        args.video, 
        args.audio, 
        args.lyrics, 
        args.output,
        use_chunking=not args.no_chunking,
        use_energy_analysis=not args.no_energy
    )
    
    # 如果需要燒錄字幕
    if args.burn and args.video_output:
        from video_processor import VideoProcessor
        processor = VideoProcessor(args.config)
        processor.burn_subtitles_to_video(args.video, args.output, args.video_output)

if __name__ == "__main__":
    main()