#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import json
import os
from typing import List, Dict
import threading
import time

class SubtitleEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("日文歌曲字幕時間軸編輯器")
        self.root.geometry("1000x700")
        
        # 初始化 pygame mixer
        pygame.mixer.init()
        
        # 變數
        self.video_path = ""
        self.lyrics_lines = []
        self.subtitles = []
        self.current_time = 0.0
        self.duration = 0.0
        self.is_playing = False
        self.current_line_index = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """設定使用者介面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 檔案選擇區域
        file_frame = ttk.LabelFrame(main_frame, text="檔案選擇", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(file_frame, text="選擇影片檔案", command=self.select_video).grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="載入歌詞檔案", command=self.load_lyrics).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="載入現有字幕", command=self.load_existing_srt).grid(row=0, column=2, padx=5)
        
        # 播放控制區域
        control_frame = ttk.LabelFrame(main_frame, text="播放控制", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="播放/暫停", command=self.toggle_play).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="停止", command=self.stop_audio).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="重播", command=self.restart_audio).grid(row=0, column=2, padx=5)
        
        # 時間顯示
        self.time_label = ttk.Label(control_frame, text="00:00 / 00:00")
        self.time_label.grid(row=0, column=3, padx=20)
        
        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     variable=self.progress_var, command=self.seek_audio)
        self.progress_bar.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # 歌詞和時間軸編輯區域
        edit_frame = ttk.LabelFrame(main_frame, text="歌詞時間軸編輯", padding="5")
        edit_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 歌詞列表
        lyrics_frame = ttk.Frame(edit_frame)
        lyrics_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Label(lyrics_frame, text="歌詞列表:").grid(row=0, column=0, sticky=tk.W)
        
        self.lyrics_listbox = tk.Listbox(lyrics_frame, height=15, width=40)
        self.lyrics_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.lyrics_listbox.bind('<<ListboxSelect>>', self.on_lyrics_select)
        
        lyrics_scroll = ttk.Scrollbar(lyrics_frame, orient=tk.VERTICAL, command=self.lyrics_listbox.yview)
        lyrics_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.lyrics_listbox.configure(yscrollcommand=lyrics_scroll.set)
        
        # 時間軸編輯區域
        timing_frame = ttk.Frame(edit_frame)
        timing_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Label(timing_frame, text="時間軸編輯:").grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(timing_frame, text="開始時間:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.start_time_var = tk.StringVar()
        self.start_time_entry = ttk.Entry(timing_frame, textvariable=self.start_time_var, width=10)
        self.start_time_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(timing_frame, text="結束時間:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.end_time_var = tk.StringVar()
        self.end_time_entry = ttk.Entry(timing_frame, textvariable=self.end_time_var, width=10)
        self.end_time_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 快速設定按鈕
        ttk.Button(timing_frame, text="設為當前時間", command=self.set_current_time_as_start).grid(row=3, column=0, pady=5)
        ttk.Button(timing_frame, text="設為結束時間", command=self.set_current_time_as_end).grid(row=3, column=1, pady=5)
        
        ttk.Button(timing_frame, text="更新時間軸", command=self.update_timing).grid(row=4, column=0, columnspan=2, pady=5)
        
        # 預覽區域
        preview_frame = ttk.LabelFrame(timing_frame, text="預覽", padding="5")
        preview_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=8, width=50)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        preview_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        
        # 儲存按鈕
        save_frame = ttk.Frame(main_frame)
        save_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(save_frame, text="儲存 SRT 檔案", command=self.save_srt).grid(row=0, column=0, padx=5)
        ttk.Button(save_frame, text="燒錄到影片", command=self.burn_to_video).grid(row=0, column=1, padx=5)
        
        # 設定網格權重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.rowconfigure(0, weight=1)
        lyrics_frame.rowconfigure(1, weight=1)
        
        # 開始時間更新線程
        self.start_time_update_thread()
    
    def start_time_update_thread(self):
        """開始時間更新線程"""
        def update_time():
            while True:
                if self.is_playing and pygame.mixer.music.get_busy():
                    self.current_time += 0.1
                    self.root.after(0, self.update_time_display)
                time.sleep(0.1)
        
        thread = threading.Thread(target=update_time, daemon=True)
        thread.start()    

    def select_video(self):
        """選擇影片檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇影片檔案",
            filetypes=[("影片檔案", "*.mp4 *.avi *.mov *.mkv"), ("所有檔案", "*.*")]
        )
        if file_path:
            self.video_path = file_path
            # 提取音訊用於播放
            self.extract_audio()
    
    def extract_audio(self):
        """從影片提取音訊"""
        try:
            from moviepy.editor import VideoFileClip
            video = VideoFileClip(self.video_path)
            self.duration = video.duration
            
            # 提取音訊並儲存為臨時檔案
            audio_path = "temp_audio.wav"
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            
            # 載入音訊到 pygame
            pygame.mixer.music.load(audio_path)
            messagebox.showinfo("成功", f"影片載入成功！長度: {self.duration:.1f} 秒")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"載入影片失敗: {e}")
    
    def load_lyrics(self):
        """載入歌詞檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇歌詞檔案",
            filetypes=[("文字檔案", "*.txt"), ("所有檔案", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                self.lyrics_lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # 初始化字幕列表
                self.subtitles = []
                for i, line in enumerate(self.lyrics_lines):
                    self.subtitles.append({
                        'start': i * 3.0,  # 預設每行 3 秒
                        'end': (i + 1) * 3.0,
                        'text': line
                    })
                
                # 更新界面
                self.update_lyrics_listbox()
                self.update_preview()
                messagebox.showinfo("成功", f"載入 {len(self.lyrics_lines)} 行歌詞")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"載入歌詞失敗: {e}")
    
    def load_existing_srt(self):
        """載入現有的 SRT 檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇 SRT 檔案",
            filetypes=[("SRT 檔案", "*.srt"), ("所有檔案", "*.*")]
        )
        if file_path:
            try:
                self.subtitles = self.parse_srt_file(file_path)
                self.lyrics_lines = [sub['text'] for sub in self.subtitles]
                self.update_lyrics_listbox()
                self.update_preview()
                messagebox.showinfo("成功", f"載入 {len(self.subtitles)} 個字幕")
            except Exception as e:
                messagebox.showerror("錯誤", f"載入 SRT 檔案失敗: {e}")
    
    def parse_srt_file(self, srt_path: str) -> List[Dict]:
        """解析 SRT 檔案"""
        subtitles = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        blocks = content.split('\n\n')
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                time_line = lines[1]
                start_str, end_str = time_line.split(' --> ')
                
                start_time = self.srt_time_to_seconds(start_str)
                end_time = self.srt_time_to_seconds(end_str)
                text = '\n'.join(lines[2:])
                
                subtitles.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
        
        return subtitles
    
    def srt_time_to_seconds(self, time_str: str) -> float:
        """將 SRT 時間格式轉換為秒數"""
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        return h * 3600 + m * 60 + s + ms / 1000.0
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """將秒數轉換為 SRT 時間格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def update_lyrics_listbox(self):
        """更新歌詞列表框"""
        self.lyrics_listbox.delete(0, tk.END)
        for i, subtitle in enumerate(self.subtitles):
            time_str = f"[{subtitle['start']:.1f}s] {subtitle['text'][:30]}..."
            self.lyrics_listbox.insert(tk.END, time_str)
    
    def on_lyrics_select(self, event):
        """歌詞選擇事件"""
        selection = self.lyrics_listbox.curselection()
        if selection:
            self.current_line_index = selection[0]
            subtitle = self.subtitles[self.current_line_index]
            self.start_time_var.set(f"{subtitle['start']:.1f}")
            self.end_time_var.set(f"{subtitle['end']:.1f}")
    
    def toggle_play(self):
        """播放/暫停切換"""
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(start=self.current_time)
            self.is_playing = True
        else:
            if self.is_playing:
                pygame.mixer.music.pause()
                self.is_playing = False
            else:
                pygame.mixer.music.unpause()
                self.is_playing = True
    
    def stop_audio(self):
        """停止播放"""
        pygame.mixer.music.stop()
        self.is_playing = False
    
    def restart_audio(self):
        """重新播放"""
        self.current_time = 0.0
        pygame.mixer.music.play()
        self.is_playing = True
    
    def seek_audio(self, value):
        """跳轉到指定時間"""
        if self.duration > 0:
            self.current_time = float(value) * self.duration / 100
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.play(start=self.current_time)
    
    def set_current_time_as_start(self):
        """設定當前時間為開始時間"""
        self.start_time_var.set(f"{self.current_time:.1f}")
    
    def set_current_time_as_end(self):
        """設定當前時間為結束時間"""
        self.end_time_var.set(f"{self.current_time:.1f}")
    
    def update_timing(self):
        """更新選中歌詞的時間軸"""
        if self.current_line_index < len(self.subtitles):
            try:
                start_time = float(self.start_time_var.get())
                end_time = float(self.end_time_var.get())
                
                if start_time >= end_time:
                    messagebox.showerror("錯誤", "開始時間必須小於結束時間")
                    return
                
                self.subtitles[self.current_line_index]['start'] = start_time
                self.subtitles[self.current_line_index]['end'] = end_time
                
                self.update_lyrics_listbox()
                self.update_preview()
                
            except ValueError:
                messagebox.showerror("錯誤", "請輸入有效的時間數值")
    
    def update_time_display(self):
        """更新時間顯示"""
        current_str = f"{int(self.current_time//60):02d}:{int(self.current_time%60):02d}"
        total_str = f"{int(self.duration//60):02d}:{int(self.duration%60):02d}"
        self.time_label.config(text=f"{current_str} / {total_str}")
        
        if self.duration > 0:
            progress = (self.current_time / self.duration) * 100
            self.progress_var.set(progress)
    
    def update_preview(self):
        """更新預覽"""
        self.preview_text.delete(1.0, tk.END)
        for i, subtitle in enumerate(self.subtitles[:10]):  # 只顯示前 10 行
            start_str = self.seconds_to_srt_time(subtitle['start'])
            end_str = self.seconds_to_srt_time(subtitle['end'])
            preview_line = f"{i+1}\n{start_str} --> {end_str}\n{subtitle['text']}\n\n"
            self.preview_text.insert(tk.END, preview_line)
    
    def save_srt(self):
        """儲存 SRT 檔案"""
        file_path = filedialog.asksaveasfilename(
            title="儲存 SRT 檔案",
            defaultextension=".srt",
            filetypes=[("SRT 檔案", "*.srt"), ("所有檔案", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for i, subtitle in enumerate(self.subtitles, 1):
                        start_str = self.seconds_to_srt_time(subtitle['start'])
                        end_str = self.seconds_to_srt_time(subtitle['end'])
                        f.write(f"{i}\n{start_str} --> {end_str}\n{subtitle['text']}\n\n")
                
                messagebox.showinfo("成功", f"SRT 檔案已儲存至: {file_path}")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存失敗: {e}")
    
    def burn_to_video(self):
        """燒錄字幕到影片"""
        if not self.video_path:
            messagebox.showerror("錯誤", "請先選擇影片檔案")
            return
        
        output_path = filedialog.asksaveasfilename(
            title="儲存影片檔案",
            defaultextension=".mp4",
            filetypes=[("MP4 檔案", "*.mp4"), ("所有檔案", "*.*")]
        )
        if output_path:
            try:
                # 先儲存臨時 SRT 檔案
                temp_srt = "temp_subtitles.srt"
                with open(temp_srt, 'w', encoding='utf-8') as f:
                    for i, subtitle in enumerate(self.subtitles, 1):
                        start_str = self.seconds_to_srt_time(subtitle['start'])
                        end_str = self.seconds_to_srt_time(subtitle['end'])
                        f.write(f"{i}\n{start_str} --> {end_str}\n{subtitle['text']}\n\n")
                
                # 使用 video_processor 燒錄字幕
                from video_processor import VideoProcessor
                processor = VideoProcessor()
                processor.burn_subtitles_to_video(self.video_path, temp_srt, output_path)
                
                # 清理臨時檔案
                if os.path.exists(temp_srt):
                    os.remove(temp_srt)
                
                messagebox.showinfo("成功", f"影片已儲存至: {output_path}")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"燒錄失敗: {e}")
    
    def run(self):
        """執行應用程式"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SubtitleEditor()
    app.run()