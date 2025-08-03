#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import json
import time
import warnings
import tempfile
from pathlib import Path
import sys

# 設定 Python 編碼環境
if sys.platform.startswith('win'):
    # Windows 環境下設定編碼
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    # 設定控制台編碼
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass  # 如果都失敗就使用預設

# 抑制 Whisper 的 Triton 警告
warnings.filterwarnings("ignore", message=".*Failed to launch Triton kernels.*")
warnings.filterwarnings("ignore", message=".*falling back to a slower.*")

class WhisperSubtitleGUI:
    def __init__(self):
        # 檢查關鍵檔案是否存在
        self.check_essential_files()
        
        # 檢查並修復 FFmpeg 問題
        self.check_and_fix_ffmpeg()
        
        self.root = tk.Tk()
        self.root.title("Whisper 字幕生成器")
        self.root.geometry("1000x900")  # 增加視窗高度以容納更多內容
        self.root.resizable(True, True)
        
        # 設定最小視窗大小
        self.root.minsize(900, 750)
        
        # 變數
        self.video_path = tk.StringVar()
        self.audio_path = tk.StringVar()
        self.output_srt_path = tk.StringVar()
        self.output_video_path = tk.StringVar()
        self.whisper_model = tk.StringVar(value="medium")
        self.language = tk.StringVar(value="auto")  # 改為自動偵測
        self.use_audio_file = tk.BooleanVar(value=False)
        self.custom_model_dir = tk.StringVar()
        self.use_custom_model_dir = tk.BooleanVar(value=False)
        self.device = tk.StringVar(value="auto")
        self.use_gpu = tk.BooleanVar(value=True)
        self.music_mode = tk.BooleanVar(value=False)
        self.filter_repetitive = tk.BooleanVar(value=True)
        self.no_speech_threshold = tk.DoubleVar(value=0.6)
        self.temperature = tk.DoubleVar(value=0.0)
        self.use_optimization = tk.BooleanVar(value=True)
        self.multi_pass_mode = tk.BooleanVar(value=False)
        self.quality_level = tk.StringVar(value="auto")
        self.content_type = tk.StringVar(value="auto")
        self.is_processing = False
        
        self.setup_ui()
        self.load_config()
    
    def check_essential_files(self):
        """檢查關鍵檔案是否存在"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        essential_files = [
            "video_processor.py",
            "subtitle_editor.py"
        ]
        
        # 檢查可選但重要的檔案
        optional_files = [
            "whisper_accuracy_optimizer.py"
        ]
        
        missing_files = []
        missing_optional = []
        
        for filename in essential_files:
            file_path = os.path.join(script_dir, filename)
            if not os.path.exists(file_path):
                missing_files.append(filename)
        
        for filename in optional_files:
            file_path = os.path.join(script_dir, filename)
            if not os.path.exists(file_path):
                missing_optional.append(filename)
        
        if missing_files:
            import tkinter.messagebox as msgbox
            error_msg = f"缺少關鍵檔案:\n\n"
            for filename in missing_files:
                error_msg += f"• {filename}\n"
            error_msg += f"\n請確保所有檔案都在同一個資料夾中。\n"
            error_msg += f"建議執行 check_installation.bat 進行完整檢查。"
            
            # 創建一個臨時的 root 視窗來顯示錯誤
            temp_root = tk.Tk()
            temp_root.withdraw()  # 隱藏主視窗
            msgbox.showerror("檔案缺失", error_msg)
            temp_root.destroy()
            sys.exit(1)
        
        if missing_optional:
            print(f"⚠️ 可選檔案缺失: {', '.join(missing_optional)}")
            print("   程式將以基本模式運行，部分優化功能不可用")
    
    def check_and_fix_ffmpeg(self):
        """檢查並修復 FFmpeg 問題"""
        # 強制設定本地 FFmpeg 環境
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(script_dir, "ffmpeg.exe")
        
        # 優先使用本地 FFmpeg
        if os.path.exists(local_ffmpeg):
            # 強制設定環境變數
            current_path = os.environ.get('PATH', '')
            if script_dir not in current_path:
                os.environ['PATH'] = script_dir + os.pathsep + current_path
            
            os.environ['FFMPEG_BINARY'] = local_ffmpeg
            os.environ['FFPROBE_BINARY'] = os.path.join(script_dir, "ffprobe.exe")
            print(f"✅ 使用本地 FFmpeg: {local_ffmpeg}")
            
            # 測試本地 FFmpeg
            try:
                result = subprocess.run([local_ffmpeg, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ 本地 FFmpeg 測試通過")
                    return True
            except Exception as e:
                print(f"⚠️ 本地 FFmpeg 測試失敗: {e}")
        
        # 檢查系統 FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ 系統 FFmpeg 檢查通過")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        # FFmpeg 不可用，顯示詳細警告
        print("❌ FFmpeg 未找到或不可用")
        print("💡 這會導致 [WinError 2] 系統找不到指定的檔案 錯誤")
        print("🔧 建議解決方案:")
        print("   1. 執行: python diagnose_winerror2.py (深度診斷)")
        print("   2. 執行: python fix_ffmpeg_issue.py (自動修復)")
        print("   3. 手動下載 ffmpeg.exe 到程式目錄")
        
        # 在 Windows 上嘗試自動修復
        if sys.platform.startswith('win'):
            try:
                import tkinter.messagebox as msgbox
                temp_root = tk.Tk()
                temp_root.withdraw()
                
                response = msgbox.askyesno(
                    "FFmpeg 缺失 - [WinError 2] 錯誤", 
                    "檢測到 FFmpeg 缺失，這會導致以下錯誤：\n"
                    "[WinError 2] 系統找不到指定的檔案\n\n"
                    "是否要執行深度診斷和自動修復？\n"
                    "(需要網路連線)"
                )
                
                temp_root.destroy()
                
                if response:
                    self.run_ffmpeg_diagnosis()
                    
            except Exception as e:
                print(f"自動修復對話框失敗: {e}")
        
        return False
    
    def run_ffmpeg_diagnosis(self):
        """執行 FFmpeg 診斷"""
        try:
            print("� 啟在動 FFmpeg 診斷工具...")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            diagnosis_script = os.path.join(script_dir, "diagnose_winerror2.py")
            
            if os.path.exists(diagnosis_script):
                # 在新視窗中執行診斷
                subprocess.Popen([sys.executable, diagnosis_script], 
                               cwd=script_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
                print("✅ 診斷工具已啟動")
            else:
                print("❌ 找不到診斷腳本")
                # 嘗試執行修復腳本
                fix_script = os.path.join(script_dir, "fix_ffmpeg_issue.py")
                if os.path.exists(fix_script):
                    subprocess.Popen([sys.executable, fix_script], 
                                   cwd=script_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    print("✅ 修復工具已啟動")
                
        except Exception as e:
            print(f"診斷工具啟動失敗: {e}")
    
    def auto_install_ffmpeg(self):
        """自動安裝 FFmpeg（保留向後相容性）"""
        self.run_ffmpeg_diagnosis()
    
    def setup_ui(self):
        """設定使用者介面"""
        # 主框架 - 使用 Scrollable Frame
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        # 儲存 canvas 和 scrollable_frame 為實例變數，方便後續使用
        self.main_canvas = main_canvas
        self.scrollable_frame = scrollable_frame
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加滑鼠滾輪支援 - 改進版本
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 綁定滾輪事件到多個元件
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        main_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.root.bind("<MouseWheel>", _on_mousewheel)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 主要內容框架
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 確保 scrollable_frame 可以擴展
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.rowconfigure(0, weight=1)
        
        # 標題
        title_label = ttk.Label(main_frame, text="Whisper 字幕生成器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 模式選擇 - 簡化為僅生成字幕
        mode_frame = ttk.LabelFrame(main_frame, text="操作模式", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        
        self.operation_mode = tk.StringVar(value="generate_only")
        
        ttk.Radiobutton(mode_frame, text="生成字幕檔案（SRT）", variable=self.operation_mode, 
                       value="generate_only", command=self.update_ui_mode).grid(row=0, column=0, sticky=tk.W, padx=10)
        ttk.Radiobutton(mode_frame, text="僅燒錄現有字幕到影片", variable=self.operation_mode, 
                       value="burn_only", command=self.update_ui_mode).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # 添加提示說明
        mode_info = ttk.Label(mode_frame, text="💡 建議：先生成字幕檔案，檢查並編輯後再燒錄到影片", 
                             font=("Arial", 9), foreground="blue")
        mode_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 檔案選擇區域
        file_frame = ttk.LabelFrame(main_frame, text="檔案選擇", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
        
        # 影片檔案選擇
        ttk.Label(file_frame, text="影片檔案:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="瀏覽", command=self.select_video_file).grid(row=0, column=2, padx=5)
        
        # 音訊檔案選擇（可選）
        self.use_audio_check = ttk.Checkbutton(file_frame, text="使用 WAV 音訊檔案 (更準確)", 
                                              variable=self.use_audio_file, command=self.toggle_audio_input)
        self.use_audio_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.audio_entry = ttk.Entry(file_frame, textvariable=self.audio_path, width=50, state="disabled")
        self.audio_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self.audio_btn = ttk.Button(file_frame, text="瀏覽", command=self.select_audio_file, state="disabled")
        self.audio_btn.grid(row=1, column=2, padx=5)
        
        # SRT 檔案路徑（輸出或輸入，根據模式而定）
        self.srt_label = ttk.Label(file_frame, text="字幕檔案:")
        self.srt_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.output_srt_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        self.srt_btn = ttk.Button(file_frame, text="瀏覽", command=self.select_srt_file)
        self.srt_btn.grid(row=2, column=2, padx=5)
        
        # 影片輸出路徑
        ttk.Label(file_frame, text="輸出影片:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.output_video_path, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="瀏覽", command=self.select_video_output).grid(row=3, column=2, padx=5)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Whisper 設定區域 - 使用更緊湊的水平佈局
        self.whisper_frame = ttk.LabelFrame(main_frame, text="Whisper 設定", padding="8")
        self.whisper_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 8))
        
        # 基本設定（水平排列）
        basic_row = ttk.Frame(self.whisper_frame)
        basic_row.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 模型選擇
        ttk.Label(basic_row, text="模型:").pack(side=tk.LEFT, padx=(0, 5))
        model_combo = ttk.Combobox(basic_row, textvariable=self.whisper_model, 
                                  values=["tiny", "base", "small", "medium", "large", "large-v3", "turbo"],
                                  width=10, state="readonly")
        model_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 語言選擇（自動偵測預設）
        ttk.Label(basic_row, text="語言:").pack(side=tk.LEFT, padx=(0, 5))
        language_combo = ttk.Combobox(basic_row, textvariable=self.language, 
                                     values=["auto", "zh", "zh-cn", "zh-tw", "ja", "en", "ko", "es", "fr", "de"],
                                     width=8, state="readonly")
        language_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 內容類型（幫助語言偵測）
        ttk.Label(basic_row, text="內容類型:").pack(side=tk.LEFT, padx=(0, 5))
        content_combo = ttk.Combobox(basic_row, textvariable=self.content_type,
                                    values=["auto", "speech", "music", "song", "podcast", "audiobook"],
                                    width=12, state="readonly")
        content_combo.pack(side=tk.LEFT)
        
        # GPU 設定
        ttk.Checkbutton(basic_row, text="GPU 加速", 
                       variable=self.use_gpu, command=self.toggle_gpu_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(basic_row, text="設備:").pack(side=tk.LEFT)
        device_combo = ttk.Combobox(basic_row, textvariable=self.device,
                                   values=["auto", "cuda", "cpu"], 
                                   state="readonly", width=6)
        device_combo.pack(side=tk.LEFT, padx=5)
        
        # 第二行：音樂和參數設定
        music_row = ttk.Frame(self.whisper_frame)
        music_row.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 音樂模式
        self.music_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(music_row, text="🎵 音樂模式", 
                       variable=self.music_mode, command=self.toggle_music_mode).pack(side=tk.LEFT, padx=(0, 15))
        
        # 過濾選項
        self.filter_repetitive = tk.BooleanVar(value=True)
        ttk.Checkbutton(music_row, text="過濾重複", 
                       variable=self.filter_repetitive).pack(side=tk.LEFT, padx=(0, 15))
        
        # 靜音閾值
        ttk.Label(music_row, text="靜音:").pack(side=tk.LEFT)
        self.no_speech_threshold = tk.DoubleVar(value=0.6)
        ttk.Scale(music_row, from_=0.1, to=1.0, variable=self.no_speech_threshold, 
                 orient=tk.HORIZONTAL, length=80).pack(side=tk.LEFT, padx=(2, 10))
        
        # 溫度
        ttk.Label(music_row, text="溫度:").pack(side=tk.LEFT)
        self.temperature = tk.DoubleVar(value=0.0)
        ttk.Scale(music_row, from_=0.0, to=1.0, variable=self.temperature, 
                 orient=tk.HORIZONTAL, length=80).pack(side=tk.LEFT, padx=(2, 0))
        
        # 第三行：進階優化選項 - 全部水平排列
        advanced_row = ttk.Frame(self.whisper_frame)
        advanced_row.grid(row=2, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(5, 5))
        
        # 優化選項
        self.use_optimization = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_row, text="🧠 智能優化", 
                       variable=self.use_optimization).pack(side=tk.LEFT, padx=(0, 10))
        
        self.multi_pass_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_row, text="🔄 多次通過", 
                       variable=self.multi_pass_mode).pack(side=tk.LEFT, padx=(0, 15))
        
        # 品質等級
        ttk.Label(advanced_row, text="品質:").pack(side=tk.LEFT)
        self.quality_level = tk.StringVar(value="auto")
        quality_combo = ttk.Combobox(advanced_row, textvariable=self.quality_level,
                                   values=["auto", "fast", "balanced", "high", "ultra"], 
                                   state="readonly", width=8)
        quality_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        # 內容類型
        ttk.Label(advanced_row, text="類型:").pack(side=tk.LEFT)
        self.content_type = tk.StringVar(value="auto")
        content_combo = ttk.Combobox(advanced_row, textvariable=self.content_type,
                                   values=["auto", "speech", "music", "mixed"], 
                                   state="readonly", width=8)
        content_combo.pack(side=tk.LEFT, padx=5)
        
        # 模型說明 - 移到第四行
        model_info = ttk.Label(self.whisper_frame, text="💡 模型: tiny(快) → base → small → medium(推薦) → large(準確)", 
                              font=("Arial", 8), foreground="gray")
        model_info.grid(row=3, column=0, columnspan=6, sticky=tk.W, pady=(5, 0))
        
        # 第四行：模型位置設定 - 水平排列
        model_dir_row = ttk.Frame(self.whisper_frame)
        model_dir_row.grid(row=4, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.custom_model_check = ttk.Checkbutton(model_dir_row, text="自訂模型位置", 
                                                 variable=self.use_custom_model_dir, 
                                                 command=self.toggle_custom_model_dir)
        self.custom_model_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_dir_entry = ttk.Entry(model_dir_row, textvariable=self.custom_model_dir, width=35, state="disabled")
        self.model_dir_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        self.model_dir_btn = ttk.Button(model_dir_row, text="瀏覽", command=self.select_model_directory, state="disabled")
        self.model_dir_btn.pack(side=tk.LEFT)
        

        
        # 第五行：工具按鈕 - 水平排列，更緊湊
        tools_row = ttk.Frame(self.whisper_frame)
        tools_row.grid(row=5, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(8, 0))
        
        # 主要工具按鈕
        ttk.Button(tools_row, text="📁 模型", command=self.check_downloaded_models).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tools_row, text="🚀 GPU", command=self.check_gpu_availability).pack(side=tk.LEFT, padx=5)
        ttk.Button(tools_row, text="⚙️ 設定", command=self.show_env_setup).pack(side=tk.LEFT, padx=5)
        ttk.Button(tools_row, text="🎵 音樂幫助", command=self.show_music_help).pack(side=tk.LEFT, padx=5)
        ttk.Button(tools_row, text="🧠 優化說明", command=self.show_optimization_help).pack(side=tk.LEFT, padx=5)
        
        # 字幕設定區域 - 更緊湊的水平佈局
        subtitle_frame = ttk.LabelFrame(main_frame, text="字幕設定", padding="6")
        subtitle_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(8, 5))
        
        # 水平排列所有設定
        settings_row = ttk.Frame(subtitle_frame)
        settings_row.pack(fill=tk.X)
        
        # 字體大小
        ttk.Label(settings_row, text="字體大小:").pack(side=tk.LEFT)
        self.font_size = tk.IntVar(value=48)
        font_size_spin = ttk.Spinbox(settings_row, from_=20, to=100, textvariable=self.font_size, width=6)
        font_size_spin.pack(side=tk.LEFT, padx=(5, 20))
        
        # 字幕位置
        ttk.Label(settings_row, text="底部邊距:").pack(side=tk.LEFT)
        self.margin = tk.IntVar(value=80)
        margin_spin = ttk.Spinbox(settings_row, from_=20, to=200, textvariable=self.margin, width=6)
        margin_spin.pack(side=tk.LEFT, padx=5)
        
        # 控制按鈕區域 - 簡化佈局
        control_frame = ttk.LabelFrame(main_frame, text="執行操作", padding="8")
        control_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 8))
        
        # 使用水平佈局，兩個主要按鈕
        buttons_row = ttk.Frame(control_frame)
        buttons_row.pack(fill=tk.X)
        
        self.generate_btn = ttk.Button(buttons_row, text="🎤 生成字幕", 
                                      command=self.generate_subtitles)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        self.burn_only_btn = ttk.Button(buttons_row, text="🔥 燒錄字幕", 
                                       command=self.burn_subtitles)
        self.burn_only_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 添加字幕編輯器按鈕
        self.edit_btn = ttk.Button(buttons_row, text="✏️ 編輯字幕", 
                                  command=self.open_subtitle_editor, state="disabled")
        self.edit_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 進度條和狀態 - 更緊湊
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 8))
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 3))
        
        self.status_label = ttk.Label(progress_frame, text="準備就緒", foreground="green")
        self.status_label.pack()
        
        # 日誌區域 - 增加高度並改善滾動
        log_frame = ttk.LabelFrame(main_frame, text="處理日誌", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 5))
        
        # 增加日誌區域高度，並確保有足夠空間顯示內容
        self.log_text = tk.Text(log_frame, height=12, wrap=tk.WORD, font=("Consolas", 9))
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 設定網格權重 - 讓日誌區域可以擴展
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)  # 日誌區域可以垂直擴展
        
        # 延遲綁定滾輪事件到所有子元件
        def bind_all_mousewheel():
            def bind_recursive(widget):
                try:
                    widget.bind("<MouseWheel>", lambda e: self.main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
                    for child in widget.winfo_children():
                        bind_recursive(child)
                except:
                    pass
            bind_recursive(main_frame)
        
        # 在 UI 完成後綁定滾輪事件
        self.root.after(100, bind_all_mousewheel)
        
        # 初始化 UI 模式
        self.update_ui_mode()
        
        # 確保滾動區域正確設定
        self.root.after(200, self.update_scroll_region)
    
    def load_config(self):
        """載入設定檔"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "whisper_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.whisper_model.set(config.get("model", "medium"))
                    self.language.set(config.get("language", "auto"))  # 改為自動偵測預設
                    self.font_size.set(config.get("font_size", 48))
                    self.margin.set(config.get("margin", 80))
                    self.use_audio_file.set(config.get("use_audio_file", False))
                    self.use_custom_model_dir.set(config.get("use_custom_model_dir", False))
                    self.custom_model_dir.set(config.get("custom_model_dir", ""))
                    self.operation_mode.set(config.get("operation_mode", "generate_only"))
                    self.use_gpu.set(config.get("use_gpu", True))
                    self.device.set(config.get("device", "auto"))
                    self.use_optimization.set(config.get("use_optimization", True))
                    self.multi_pass_mode.set(config.get("multi_pass_mode", False))
                    self.quality_level.set(config.get("quality_level", "auto"))
                    self.content_type.set(config.get("content_type", "auto"))
                    self.toggle_audio_input()  # 更新界面狀態
                    self.toggle_custom_model_dir()  # 更新模型目錄界面狀態
                    self.toggle_gpu_settings()  # 更新 GPU 界面狀態
                    self.update_ui_mode()  # 更新操作模式界面
                    self.log("✅ 設定檔載入成功")
            else:
                self.log("ℹ️ 設定檔不存在，使用預設設定")
                # 首次啟動時自動儲存預設設定
                self.save_config()
        except Exception as e:
            self.log(f"載入設定失敗: {e}")
            self.log("ℹ️ 將使用預設設定")
    
    def save_config(self):
        """儲存設定檔"""
        try:
            config = {
                "model": self.whisper_model.get(),
                "language": self.language.get(),
                "font_size": self.font_size.get(),
                "margin": self.margin.get(),
                "use_audio_file": self.use_audio_file.get(),
                "use_custom_model_dir": self.use_custom_model_dir.get(),
                "custom_model_dir": self.custom_model_dir.get(),
                "operation_mode": self.operation_mode.get(),
                "use_gpu": self.use_gpu.get(),
                "device": self.device.get(),
                "use_optimization": self.use_optimization.get(),
                "multi_pass_mode": self.multi_pass_mode.get(),
                "quality_level": self.quality_level.get(),
                "content_type": self.content_type.get()
            }
            config_path = os.path.join(os.path.dirname(__file__), "whisper_config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"儲存設定失敗: {e}")
    
    def select_video_file(self):
        """選擇影片檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇影片檔案",
            filetypes=[
                ("影片檔案", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"),
                ("MP4 檔案", "*.mp4"),
                ("AVI 檔案", "*.avi"),
                ("MOV 檔案", "*.mov"),
                ("MKV 檔案", "*.mkv"),
                ("所有檔案", "*.*")
            ]
        )
        if file_path:
            self.video_path.set(file_path)
            # 自動設定輸出路徑
            base_name = Path(file_path).stem
            dir_name = Path(file_path).parent
            self.output_srt_path.set(str(dir_name / f"{base_name}_whisper.srt"))
            self.output_video_path.set(str(dir_name / f"{base_name}_with_subs.mp4"))
    
    def select_audio_file(self):
        """選擇音訊檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇音訊檔案",
            filetypes=[
                ("WAV 檔案", "*.wav"),
                ("音訊檔案", "*.wav *.mp3 *.flac *.m4a *.aac *.ogg"),
                ("MP3 檔案", "*.mp3"),
                ("FLAC 檔案", "*.flac"),
                ("所有檔案", "*.*")
            ]
        )
        if file_path:
            self.audio_path.set(file_path)
            # 如果沒有設定影片檔案，根據音訊檔案設定輸出路徑
            if not self.video_path.get():
                base_name = Path(file_path).stem
                dir_name = Path(file_path).parent
                self.output_srt_path.set(str(dir_name / f"{base_name}_whisper.srt"))
    
    def toggle_audio_input(self):
        """切換音訊輸入選項"""
        if self.use_audio_file.get():
            self.audio_entry.config(state="normal")
            self.audio_btn.config(state="normal")
        else:
            self.audio_entry.config(state="disabled")
            self.audio_btn.config(state="disabled")
            self.audio_path.set("")
    
    def show_model_location(self):
        """顯示 Whisper 模型存放位置"""
        import os
        import platform
        
        # Whisper 模型的預設存放位置
        if platform.system() == "Windows":
            model_dir = os.path.expanduser("~/.cache/whisper")
        else:
            model_dir = os.path.expanduser("~/.cache/whisper")
        
        info_text = f"""Whisper 模型存放位置：
{model_dir}

模型檔案格式：
• 新版格式: [模型名稱].pt (例如: medium.pt)
• 舊版格式: ggml-[模型名稱].bin (例如: ggml-medium.bin)

模型檔案大小：
• tiny: ~39 MB
• base: ~74 MB  
• small: ~244 MB
• medium: ~769 MB
• large: ~1550 MB

注意事項：
1. 首次使用會自動下載模型
2. 下載需要網路連線
3. 模型會永久儲存在本機
4. 新舊格式都可以使用
5. 可以手動刪除不需要的模型節省空間"""
        
        # 建立資訊視窗
        info_window = tk.Toplevel(self.root)
        info_window.title("Whisper 模型資訊")
        info_window.geometry("500x300")
        info_window.resizable(False, False)
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, info_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 添加開啟資料夾按鈕
        btn_frame = ttk.Frame(info_window)
        btn_frame.pack(pady=10)
        
        def open_model_dir():
            try:
                if os.path.exists(model_dir):
                    if platform.system() == "Windows":
                        os.startfile(model_dir)
                    else:
                        subprocess.run(["open", model_dir])
                else:
                    messagebox.showinfo("提示", "模型資料夾尚未建立\n首次使用 Whisper 時會自動建立")
            except Exception as e:
                messagebox.showerror("錯誤", f"無法開啟資料夾: {e}")
        
        ttk.Button(btn_frame, text="開啟模型資料夾", command=open_model_dir).pack()
    
    def toggle_custom_model_dir(self):
        """切換自訂模型目錄選項"""
        if self.use_custom_model_dir.get():
            self.model_dir_entry.config(state="normal")
            self.model_dir_btn.config(state="normal")
        else:
            self.model_dir_entry.config(state="disabled")
            self.model_dir_btn.config(state="disabled")
            self.custom_model_dir.set("")
    
    def select_model_directory(self):
        """選擇模型存放目錄"""
        dir_path = filedialog.askdirectory(
            title="選擇 Whisper 模型存放目錄",
            initialdir=os.path.expanduser("~")
        )
        if dir_path:
            self.custom_model_dir.set(dir_path)
            self.log(f"設定模型目錄: {dir_path}")
    
    def show_default_model_location(self):
        """顯示預設模型位置"""
        self.show_model_location()
    
    def check_downloaded_models(self):
        """檢查已下載的模型"""
        import os
        import platform
        
        # 檢查預設位置
        default_dir = os.path.expanduser("~/.cache/whisper")
        custom_dir = self.custom_model_dir.get() if self.use_custom_model_dir.get() else None
        
        model_info = "已下載的 Whisper 模型：\n\n"
        
        # 檢查預設位置
        model_info += f"預設位置: {default_dir}\n"
        if os.path.exists(default_dir):
            # 檢查新格式 (.pt) 和舊格式 (.bin)
            pt_models = [f for f in os.listdir(default_dir) if f.endswith('.pt')]
            bin_models = [f for f in os.listdir(default_dir) if f.endswith('.bin') and f.startswith('ggml-')]
            
            if pt_models or bin_models:
                for model in pt_models:
                    size = os.path.getsize(os.path.join(default_dir, model)) / (1024*1024)
                    model_info += f"  • {model} ({size:.1f} MB) [新格式]\n"
                for model in bin_models:
                    size = os.path.getsize(os.path.join(default_dir, model)) / (1024*1024)
                    model_info += f"  • {model} ({size:.1f} MB) [舊格式]\n"
            else:
                model_info += "  (無模型檔案)\n"
        else:
            model_info += "  (目錄不存在)\n"
        
        # 檢查自訂位置
        if custom_dir and os.path.exists(custom_dir):
            model_info += f"\n自訂位置: {custom_dir}\n"
            # 檢查新格式 (.pt) 和舊格式 (.bin)
            pt_models = [f for f in os.listdir(custom_dir) if f.endswith('.pt')]
            bin_models = [f for f in os.listdir(custom_dir) if f.endswith('.bin') and f.startswith('ggml-')]
            
            if pt_models or bin_models:
                for model in pt_models:
                    size = os.path.getsize(os.path.join(custom_dir, model)) / (1024*1024)
                    model_info += f"  • {model} ({size:.1f} MB) [新格式]\n"
                for model in bin_models:
                    size = os.path.getsize(os.path.join(custom_dir, model)) / (1024*1024)
                    model_info += f"  • {model} ({size:.1f} MB) [舊格式]\n"
            else:
                model_info += "  (無模型檔案)\n"
        
        # 檢查環境變數
        whisper_cache = os.environ.get('WHISPER_CACHE_DIR')
        if whisper_cache:
            model_info += f"\n環境變數 WHISPER_CACHE_DIR: {whisper_cache}\n"
            if os.path.exists(whisper_cache):
                # 檢查新格式 (.pt) 和舊格式 (.bin)
                pt_models = [f for f in os.listdir(whisper_cache) if f.endswith('.pt')]
                bin_models = [f for f in os.listdir(whisper_cache) if f.endswith('.bin') and f.startswith('ggml-')]
                
                if pt_models or bin_models:
                    for model in pt_models:
                        size = os.path.getsize(os.path.join(whisper_cache, model)) / (1024*1024)
                        model_info += f"  • {model} ({size:.1f} MB) [新格式]\n"
                    for model in bin_models:
                        size = os.path.getsize(os.path.join(whisper_cache, model)) / (1024*1024)
                        model_info += f"  • {model} ({size:.1f} MB) [舊格式]\n"
                else:
                    model_info += "  (無模型檔案)\n"
            else:
                model_info += "  (目錄不存在)\n"
        
        # 顯示資訊視窗
        info_window = tk.Toplevel(self.root)
        info_window.title("已下載的模型")
        info_window.geometry("600x400")
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, model_info)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(info_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_env_setup(self):
        """顯示環境變數設定說明"""
        env_info = """設定 Whisper 模型位置的方法：

方法1: 使用環境變數 (推薦)
1. 按 Win+R，輸入 sysdm.cpl
2. 點擊「進階」→「環境變數」
3. 在「使用者變數」中點擊「新增」
4. 變數名稱: WHISPER_CACHE_DIR
5. 變數值: 你的模型存放路徑 (例如: D:\\whisper_models)
6. 重新啟動程式

方法2: 移動現有模型
1. 將模型檔案從預設位置複製到新位置
2. 設定環境變數指向新位置
3. 刪除舊位置的檔案（可選）

方法3: 使用程式內建選項
1. 勾選「自訂模型位置」
2. 選擇你的模型存放目錄
3. 程式會在執行時指定該位置

注意事項：
• 模型檔案名稱格式: [模型名稱].pt
• 確保目錄有讀寫權限
• 環境變數優先級最高"""
        
        # 建立說明視窗
        info_window = tk.Toplevel(self.root)
        info_window.title("模型位置設定說明")
        info_window.geometry("600x500")
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, env_info)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(info_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加快速設定按鈕
        btn_frame = ttk.Frame(info_window)
        btn_frame.pack(pady=10)
        
        def set_env_var():
            """設定環境變數的輔助功能"""
            if self.custom_model_dir.get():
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "WHISPER_CACHE_DIR", 0, winreg.REG_SZ, self.custom_model_dir.get())
                    winreg.CloseKey(key)
                    messagebox.showinfo("成功", f"環境變數已設定為: {self.custom_model_dir.get()}\n請重新啟動程式以生效")
                except Exception as e:
                    messagebox.showerror("錯誤", f"設定環境變數失敗: {e}")
            else:
                messagebox.showwarning("警告", "請先選擇模型目錄")
        
        ttk.Button(btn_frame, text="快速設定環境變數", command=set_env_var).pack()
    
    def toggle_gpu_settings(self):
        """切換 GPU 設定"""
        if self.use_gpu.get():
            self.device.set("auto")
        else:
            self.device.set("cpu")
    
    def check_gpu_availability(self):
        """檢查 GPU 可用性"""
        gpu_info = "GPU 可用性檢查:\n\n"
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_info += f"✅ CUDA 可用\n"
                gpu_info += f"📊 GPU 數量: {gpu_count}\n"
                
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                    gpu_info += f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)\n"
                
                current_gpu = torch.cuda.current_device()
                gpu_info += f"🎯 當前使用: GPU {current_gpu}\n"
            else:
                gpu_info += "❌ CUDA 不可用\n"
                gpu_info += "💡 將使用 CPU 處理\n"
        except ImportError:
            gpu_info += "❌ PyTorch 未安裝\n"
            gpu_info += "💡 無法檢查 GPU 狀態\n"
        except Exception as e:
            gpu_info += f"⚠️ 檢查時出錯: {e}\n"
        
        # 檢查其他 GPU 加速選項
        try:
            import whisper
            gpu_info += f"\n🎤 Whisper 版本: {whisper.__version__}\n"
        except:
            pass
        
        gpu_info += "\n💡 建議:\n"
        gpu_info += "- 如果有 NVIDIA GPU，使用 CUDA 會大幅提升速度\n"
        gpu_info += "- Windows 上可能會看到 Triton 警告，但不影響 GPU 功能\n"
        gpu_info += "- 如果沒有 GPU，CPU 模式仍可正常工作\n"
        gpu_info += "- 可以嘗試 Const-me/Whisper 獲得更好的 GPU 性能\n"
        
        gpu_info += "\n⚠️ 常見警告說明:\n"
        gpu_info += "- 'Failed to launch Triton kernels' 是正常的\n"
        gpu_info += "- Triton 在 Windows 上支援有限\n"
        gpu_info += "- GPU 加速仍然有效，只是使用備用實現\n"
        
        # 顯示資訊視窗
        info_window = tk.Toplevel(self.root)
        info_window.title("GPU 可用性檢查")
        info_window.geometry("500x400")
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, gpu_info)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(info_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def toggle_music_mode(self):
        """切換音樂模式設定"""
        if self.music_mode.get():
            # 音樂模式：調整參數以更好識別歌曲
            self.no_speech_threshold.set(0.3)  # 降低靜音閾值
            self.temperature.set(0.2)  # 增加一點隨機性
            self.log("🎵 已啟用音樂模式，調整參數以更好識別歌曲")
        else:
            # 一般模式：恢復預設值
            self.no_speech_threshold.set(0.6)
            self.temperature.set(0.0)
            self.log("💬 已切換到一般語音模式")
    
    def update_scroll_region(self):
        """更新滾動區域"""
        try:
            self.scrollable_frame.update_idletasks()
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        except:
            pass
    
    def update_ui_mode(self):
        """根據操作模式更新 UI"""
        mode = self.operation_mode.get()
        
        if mode == "generate_only":
            # 僅生成字幕模式
            self.srt_label.config(text="字幕檔案 (輸出):")
            self.srt_btn.config(command=self.select_srt_output)
            
            # 顯示 Whisper 設定
            self.whisper_frame.grid()
            
            # 顯示音訊選項
            self.use_audio_check.grid()
            if self.use_audio_file.get():
                self.audio_entry.grid()
                self.audio_btn.grid()
            
            # 按鈕狀態 - 只保留生成字幕和編輯按鈕
            self.generate_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
            if hasattr(self, 'edit_btn'):
                self.edit_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
            self.burn_only_btn.pack_forget()
            
            self.log("模式: 僅生成字幕檔案")
            
        elif mode == "burn_only":
            # 僅燒錄模式
            self.srt_label.config(text="字幕檔案 (輸入):")
            self.srt_btn.config(command=self.select_existing_srt)
            
            # 隱藏 Whisper 設定
            self.whisper_frame.grid_remove()
            
            # 隱藏音訊選項
            self.use_audio_check.grid_remove()
            self.audio_entry.grid_remove()
            self.audio_btn.grid_remove()
            
            # 按鈕狀態
            self.generate_btn.pack_forget()
            if hasattr(self, 'edit_btn'):
                self.edit_btn.pack_forget()
            self.burn_only_btn.pack(side=tk.LEFT, padx=(0, 0), fill=tk.X, expand=True)
            
            self.log("模式: 僅燒錄現有字幕到影片")
    
    def select_srt_file(self):
        """根據模式選擇 SRT 檔案"""
        if self.operation_mode.get() == "generate_only":
            self.select_srt_output()
        else:
            self.select_existing_srt()
    
    def select_existing_srt(self):
        """選擇現有的 SRT 檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇現有字幕檔案",
            filetypes=[("SRT 檔案", "*.srt"), ("所有檔案", "*.*")]
        )
        if file_path:
            self.output_srt_path.set(file_path)
            self.log(f"已選擇字幕檔案: {file_path}")
            
            # 如果字幕檔案存在，啟用編輯按鈕
            if hasattr(self, 'edit_btn'):
                self.edit_btn.config(state="normal")
            
            # 檢查字幕內容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    subtitle_count = content.count('-->')
                    self.log(f"字幕檔案包含 {subtitle_count} 個字幕片段")
            except Exception as e:
                self.log(f"讀取字幕檔案時出錯: {e}")
                messagebox.showwarning("警告", f"無法讀取字幕檔案: {e}")
    
    def select_srt_output(self):
        """選擇 SRT 輸出路徑"""
        file_path = filedialog.asksaveasfilename(
            title="儲存字幕檔案",
            defaultextension=".srt",
            filetypes=[("SRT 檔案", "*.srt"), ("所有檔案", "*.*")]
        )
        if file_path:
            self.output_srt_path.set(file_path)
    
    def select_video_output(self):
        """選擇影片輸出路徑"""
        file_path = filedialog.asksaveasfilename(
            title="儲存影片檔案",
            defaultextension=".mp4",
            filetypes=[("MP4 檔案", "*.mp4"), ("所有檔案", "*.*")]
        )
        if file_path:
            self.output_video_path.set(file_path) 
   
    def log(self, message):
        """添加日誌訊息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def set_status(self, message, color="black"):
        """設定狀態訊息"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def start_progress(self):
        """開始進度條"""
        self.progress.start()
        self.is_processing = True
        
        # 停用所有按鈕
        self.generate_btn.config(state="disabled")
        self.burn_only_btn.config(state="disabled")
        if hasattr(self, 'edit_btn'):
            self.edit_btn.config(state="disabled")
    
    def stop_progress(self):
        """停止進度條"""
        self.progress.stop()
        self.is_processing = False
        
        # 恢復按鈕狀態
        mode = self.operation_mode.get()
        if mode == "generate_only":
            self.generate_btn.config(state="normal")
            # 如果生成了字幕檔案，啟用編輯按鈕
            if hasattr(self, 'edit_btn') and os.path.exists(self.output_srt_path.get()):
                self.edit_btn.config(state="normal")
        elif mode == "burn_only":
            self.burn_only_btn.config(state="normal")
    
    def validate_inputs(self, check_srt=False):
        """驗證輸入"""
        mode = self.operation_mode.get()
        
        if mode == "generate_only":
            # 僅生成字幕模式的驗證
            if self.use_audio_file.get():
                if not self.audio_path.get():
                    messagebox.showerror("錯誤", "請選擇音訊檔案")
                    return False
                if not os.path.exists(self.audio_path.get()):
                    messagebox.showerror("錯誤", "音訊檔案不存在")
                    return False
            else:
                if not self.video_path.get():
                    messagebox.showerror("錯誤", "請選擇影片檔案")
                    return False
                if not os.path.exists(self.video_path.get()):
                    messagebox.showerror("錯誤", "影片檔案不存在")
                    return False
            
            # 燒錄字幕時需要影片檔案
            if check_srt:
                if not os.path.exists(self.output_srt_path.get()):
                    messagebox.showerror("錯誤", "字幕檔案不存在，請先生成字幕")
                    return False
                if not self.video_path.get() or not os.path.exists(self.video_path.get()):
                    messagebox.showerror("錯誤", "燒錄字幕需要影片檔案")
                    return False
        
        elif mode == "burn_only":
            # 僅燒錄模式的驗證
            if not self.video_path.get():
                messagebox.showerror("錯誤", "請選擇影片檔案")
                return False
            if not os.path.exists(self.video_path.get()):
                messagebox.showerror("錯誤", "影片檔案不存在")
                return False
            if not self.output_srt_path.get():
                messagebox.showerror("錯誤", "請選擇字幕檔案")
                return False
            if not os.path.exists(self.output_srt_path.get()):
                messagebox.showerror("錯誤", "字幕檔案不存在")
                return False
        
        return True
    
    def generate_subtitles(self):
        """使用 Whisper 生成字幕"""
        if not self.validate_inputs():
            return
        
        def run_whisper():
            try:
                self.start_progress()
                self.set_status("正在初始化 Whisper...", "blue")
                self.log("=" * 50)
                self.log("🎤 開始 Whisper 字幕生成")
                self.log("=" * 50)
                
                # 環境診斷資訊
                self.log(f"💻 工作目錄: {os.getcwd()}")
                self.log(f"🐍 Python 版本: {sys.version}")
                self.log(f"📁 腳本目錄: {os.path.dirname(os.path.abspath(__file__))}")
                
                # 決定輸入檔案
                input_file = self.audio_path.get() if self.use_audio_file.get() else self.video_path.get()
                self.log(f"📁 輸入檔案: {input_file}")
                self.log(f"📁 輸出檔案: {self.output_srt_path.get()}")
                self.log(f"🎯 使用模型: {self.whisper_model.get()}")
                self.log(f"🌍 語言設定: {self.language.get()}")
                
                # 顯示模型資訊
                try:
                    import whisper
                    model_info = {
                        'tiny': '39 MB, 最快速度',
                        'base': '74 MB, 快速',
                        'small': '244 MB, 平衡',
                        'medium': '769 MB, 推薦',
                        'large': '1550 MB, 最高精度',
                        'large-v3': '1550 MB, 最新版本',
                        'turbo': '809 MB, 快速高精度'
                    }
                    model_desc = model_info.get(self.whisper_model.get(), '未知模型')
                    self.log(f"📋 模型資訊: {model_desc}")
                except:
                    pass
                
                # 檢查檔案是否存在
                if not os.path.exists(input_file):
                    raise FileNotFoundError(f"輸入檔案不存在: {input_file}")
                
                # 顯示檔案資訊
                file_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
                self.log(f"📊 檔案大小: {file_size:.1f} MB")
                
                # 檢查路徑是否包含中文字符，如果是則直接使用 Python API
                has_chinese_chars = any(ord(c) > 127 for c in input_file) or any(ord(c) > 127 for c in self.output_srt_path.get())
                if has_chinese_chars and sys.platform.startswith('win'):
                    self.log("🔧 偵測到中文路徑，直接使用 Python API 避免編碼問題")
                    try:
                        success = False
                        if self.use_optimization.get():
                            self.log("🧠 嘗試使用優化版 Python API...")
                            success = self.run_whisper_python_api(input_file, self.output_srt_path.get())
                        
                        if not success:
                            self.log("🔄 回退到基本版本...")
                            success = self.run_basic_whisper_api(input_file, self.output_srt_path.get())
                        
                        if success:
                            self.set_status("✅ 字幕生成完成！", "green")
                            self.log("🎉 字幕生成成功完成！")
                            # 啟用編輯按鈕
                            if hasattr(self, 'edit_btn'):
                                self.edit_btn.config(state="normal")
                        else:
                            self.set_status("❌ 字幕生成失敗", "red")
                            self.log("❌ 字幕生成失敗")
                        return
                    except Exception as e:
                        self.log(f"❌ Python API 失敗: {e}")
                        self.log("🔄 回退到命令行模式...")
                
                # 設定環境變數（如果使用自訂模型位置）
                env = os.environ.copy()
                if self.use_custom_model_dir.get() and self.custom_model_dir.get():
                    env['WHISPER_CACHE_DIR'] = self.custom_model_dir.get()
                    self.log(f"🔧 使用自訂模型位置: {self.custom_model_dir.get()}")
                
                # 檢查 Whisper 是否安裝
                self.set_status("檢查 Whisper 安裝...", "blue")
                try:
                    # 先嘗試檢查 whisper 模組
                    import whisper as whisper_module
                    self.log("✅ Whisper Python 模組已安裝")
                    
                    # 再檢查命令行工具
                    result = subprocess.run(["whisper", "--help"], capture_output=True, text=True, timeout=15, shell=True)
                    if result.returncode == 0:
                        self.log("✅ Whisper 命令行工具檢查通過")
                    else:
                        self.log("⚠️ Whisper 命令行工具可能有問題，但 Python 模組可用")
                        self.log("   將嘗試使用 Python 模組直接調用")
                        
                except ImportError:
                    self.log("❌ Whisper Python 模組未安裝")
                    raise FileNotFoundError("Whisper Python 模組未安裝")
                except subprocess.TimeoutExpired:
                    self.log("⚠️ Whisper 命令響應超時，但將繼續嘗試")
                except FileNotFoundError:
                    self.log("⚠️ 找不到 whisper 命令，嘗試使用 Python 模組")
                except Exception as e:
                    self.log(f"⚠️ Whisper 檢查時出現問題: {e}")
                    self.log("   將嘗試繼續執行...")
                
                # 建立 Whisper 命令
                self.set_status("準備 Whisper 命令...", "blue")
                
                # 處理包含中文字符的路徑
                safe_input_file = input_file
                safe_output_dir = str(Path(self.output_srt_path.get()).parent)
                
                # 在 Windows 上，如果路徑包含中文字符，使用短路徑名稱
                if sys.platform.startswith('win'):
                    try:
                        import win32api
                        if any(ord(c) > 127 for c in input_file):
                            safe_input_file = win32api.GetShortPathName(input_file)
                            self.log(f"🔧 使用短路徑名稱: {safe_input_file}")
                        if any(ord(c) > 127 for c in safe_output_dir):
                            safe_output_dir = win32api.GetShortPathName(safe_output_dir)
                            self.log(f"🔧 使用短輸出目錄: {safe_output_dir}")
                    except ImportError:
                        self.log("⚠️ win32api 未安裝，無法使用短路徑名稱")
                    except Exception as e:
                        self.log(f"⚠️ 獲取短路徑名稱失敗: {e}")
                
                cmd = [
                    "whisper",
                    safe_input_file,
                    "--model", self.whisper_model.get(),
                    "--output_format", "srt",
                    "--output_dir", safe_output_dir,
                    "--verbose", "True"
                ]
                
                # 添加設備參數 (GPU 加速)
                if self.use_gpu.get():
                    device = self.device.get()
                    if device == "auto":
                        # 自動偵測最佳設備
                        try:
                            import torch
                            if torch.cuda.is_available():
                                device = "cuda"
                                self.log("🚀 偵測到 CUDA，使用 GPU 加速")
                            else:
                                device = "cpu"
                                self.log("💻 未偵測到 CUDA，使用 CPU")
                        except ImportError:
                            device = "cpu"
                            self.log("💻 PyTorch 未安裝，使用 CPU")
                    
                    cmd.extend(["--device", device])
                    self.log(f"⚙️ 使用設備: {device}")
                else:
                    cmd.extend(["--device", "cpu"])
                    self.log("💻 強制使用 CPU 模式")
                
                # 添加語言參數（如果不是自動偵測）
                if self.language.get() != "auto":
                    cmd.extend(["--language", self.language.get()])
                
                # 添加進階選項
                cmd.extend([
                    "--no_speech_threshold", str(self.no_speech_threshold.get()),
                    "--temperature", str(self.temperature.get()),
                    "--condition_on_previous_text", "False"  # 避免重複內容
                ])
                
                # 音樂模式的特殊設定
                if self.music_mode.get():
                    cmd.extend([
                        "--compression_ratio_threshold", "2.8",  # 放寬壓縮比限制
                        "--logprob_threshold", "-1.5",  # 放寬機率閾值
                        "--best_of", "3"  # 增加候選數量
                    ])
                    self.log("🎵 音樂模式：使用特殊參數優化歌曲識別")
                
                # 如果使用音訊檔案，添加額外的精確度選項
                if self.use_audio_file.get():
                    cmd.extend([
                        "--word_timestamps", "True",  # 詞級時間戳
                    ])
                    self.log("🎵 使用音訊檔案模式，啟用高精度選項")
                
                self.log(f"🔧 靜音閾值: {self.no_speech_threshold.get()}")
                self.log(f"🔧 溫度: {self.temperature.get()}")
                self.log(f"🔧 過濾重複: {self.filter_repetitive.get()}")
                
                self.log(f"⚙️ 執行命令: {' '.join(cmd)}")
                self.log("-" * 50)
                
                # 執行 Whisper
                self.set_status("正在執行 Whisper 語音識別...", "blue")
                self.log("🚀 開始語音識別處理...")
                
                # 設定環境變數以解決編碼問題
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUTF8'] = '1'
                
                # 嘗試不同的執行方式和編碼
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='replace',  # 處理編碼錯誤
                        env=env,
                        bufsize=1,
                        universal_newlines=True,
                        shell=True  # 在 Windows 上使用 shell
                    )
                except Exception as e:
                    self.log(f"⚠️ 使用 shell=True 執行失敗: {e}")
                    # 嘗試不使用 shell，並使用不同的編碼策略
                    try:
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            encoding='utf-8',
                            errors='replace',
                            env=env,
                            bufsize=1,
                            universal_newlines=True,
                            shell=False
                        )
                    except Exception as e2:
                        self.log(f"⚠️ UTF-8 編碼失敗，嘗試系統預設編碼: {e2}")
                        # 最後嘗試使用系統預設編碼
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            encoding='cp950',  # Windows 繁體中文編碼
                            errors='replace',
                            env=env,
                            bufsize=1,
                            universal_newlines=True,
                            shell=True
                        )
                
                # 即時顯示輸出並解析進度
                output_lines = []
                last_progress_time = time.time()
                
                try:
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            try:
                                line = line.strip()
                                if line:  # 只記錄非空行
                                    output_lines.append(line)
                                    self.log(line)
                                    
                                    # 解析進度資訊
                                    if "Loading model" in line:
                                        self.set_status("正在載入 Whisper 模型...", "blue")
                                    elif "Detecting language" in line:
                                        self.set_status("正在偵測語言...", "blue")
                                    elif "%" in line and ("transcribe" in line.lower() or "processing" in line.lower()):
                                        self.set_status("正在轉錄音訊...", "blue")
                                    elif "Writing" in line and ".srt" in line:
                                        self.set_status("正在寫入字幕檔案...", "blue")
                                    elif "100%" in line:
                                        self.set_status("處理完成，正在生成字幕...", "blue")
                                    elif "UnicodeEncodeError" in line:
                                        self.log("⚠️ 偵測到編碼錯誤，但處理將繼續...")
                                        self.log("💡 建議: 將檔案移至不含中文字符的路徑")
                                    elif "Skipping" in line and "due to" in line:
                                        self.log("⚠️ Whisper 跳過了某些內容，但處理將繼續...")
                                    
                                    last_progress_time = time.time()
                            except UnicodeDecodeError as e:
                                # 嘗試使用不同編碼解碼
                                try:
                                    line_bytes = line.encode('cp950', errors='ignore')
                                    line = line_bytes.decode('utf-8', errors='replace')
                                    output_lines.append(line)
                                    self.log(f"🔧 編碼修正: {line}")
                                except:
                                    self.log(f"⚠️ 編碼錯誤，跳過此行: {e}")
                                continue
                            except Exception as e:
                                self.log(f"⚠️ 處理輸出時出錯: {e}")
                                continue
                        
                        # 檢查是否長時間沒有輸出
                        if time.time() - last_progress_time > 30:  # 30秒沒有輸出
                            self.log("⏰ 處理中，請耐心等待...")
                            last_progress_time = time.time()
                            
                except Exception as e:
                    self.log(f"⚠️ 讀取 Whisper 輸出時出錯: {e}")
                    self.log("   程式將繼續等待 Whisper 完成...")
                
                process.wait()
                
                self.log("-" * 50)
                self.log(f"🏁 Whisper 處理完成，返回碼: {process.returncode}")
                
                self.log(f"🏁 Whisper 命令行處理完成，返回碼: {process.returncode}")
                
                # 檢查是否生成了 SRT 檔案
                input_name = Path(input_file).stem
                possible_srt_files = [
                    Path(self.output_srt_path.get()),
                    Path(self.output_srt_path.get()).parent / f"{input_name}.srt",
                    Path(input_file).parent / f"{input_name}.srt"
                ]
                
                srt_found = False
                for srt_file in possible_srt_files:
                    if srt_file.exists():
                        self.log(f"✅ 找到生成的字幕檔案: {srt_file}")
                        if str(srt_file) != self.output_srt_path.get():
                            # 移動到指定位置
                            srt_file.rename(self.output_srt_path.get())
                            self.log(f"📁 字幕檔案已移動至: {self.output_srt_path.get()}")
                        srt_found = True
                        process.returncode = 0  # 標記為成功
                        break
                
                # 如果命令行沒有生成檔案，嘗試使用 Python API
                if not srt_found:
                    self.log("⚠️ 命令行未生成字幕檔案，嘗試使用 Python API...")
                    try:
                        if self.use_optimization.get():
                            success = self.run_whisper_python_api(input_file, self.output_srt_path.get())
                        else:
                            success = self.run_basic_whisper_api(input_file, self.output_srt_path.get())
                        
                        if success:
                            process.returncode = 0  # 標記為成功
                            srt_found = True
                    except Exception as e:
                        self.log(f"❌ Python API 也失敗: {e}")
                
                if srt_found and process.returncode == 0:
                    # 檢查字幕內容
                    try:
                        # 嘗試不同的編碼方式讀取 SRT 檔案
                        content = None
                        for encoding in ['utf-8', 'utf-8-sig', 'cp950', 'gbk', 'latin1']:
                            try:
                                with open(self.output_srt_path.get(), 'r', encoding=encoding) as f:
                                    content = f.read()
                                    break
                            except UnicodeDecodeError:
                                continue
                        
                        if content:
                            subtitle_count = content.count('-->')
                            self.log(f"📊 生成字幕片段數量: {subtitle_count}")
                            
                            if subtitle_count > 0:
                                self.set_status("✅ 字幕生成完成！", "green")
                                self.log("🎉 字幕生成成功完成！")
                                # 啟用編輯按鈕
                                if hasattr(self, 'edit_btn'):
                                    self.edit_btn.config(state="normal")
                                
                                # 顯示成功通知
                                messagebox.showinfo("成功", f"字幕生成完成！\n\n檔案位置: {self.output_srt_path.get()}\n字幕片段: {subtitle_count} 個\n\n現在可以點擊「編輯字幕」檢查內容。")
                                # 暫時不自動預覽，讓使用者主動選擇
                                # self.preview_subtitles()
                            else:
                                self.set_status("⚠️ 字幕檔案為空", "orange")
                                self.log("⚠️ 字幕檔案已生成但內容為空")
                        else:
                            self.log("⚠️ 無法以任何編碼讀取字幕檔案")
                    except Exception as e:
                        self.log(f"⚠️ 無法讀取字幕內容: {e}")
                else:
                    self.set_status("❌ Whisper 執行失敗", "red")
                    self.log(f"❌ Whisper 執行失敗，返回碼: {process.returncode}")
                    self.log("💡 請檢查上方的錯誤訊息")
                    
                    # 顯示最後幾行輸出作為錯誤參考
                    if output_lines:
                        self.log("📋 最後的輸出訊息:")
                        for line in output_lines[-5:]:
                            self.log(f"   {line}")
                
            except FileNotFoundError as e:
                self.set_status("❌ 找不到 Whisper", "red")
                self.log("❌ 錯誤: 找不到 Whisper 程式")
                self.log("💡 解決方法:")
                self.log("   1. 執行 install_whisper.bat")
                self.log("   2. 或手動執行: pip install openai-whisper")
                self.log("   3. 重新啟動程式")
                messagebox.showerror("錯誤", "找不到 Whisper 程式\n\n請執行以下步驟:\n1. 雙擊 install_whisper.bat\n2. 或執行: pip install openai-whisper\n3. 重新啟動程式")
            except Exception as e:
                self.set_status(f"❌ 生成字幕失敗: {e}", "red")
                self.log(f"❌ 未預期的錯誤: {e}")
                self.log("💡 請檢查:")
                self.log("   - 檔案是否損壞")
                self.log("   - 磁碟空間是否足夠")
                self.log("   - 防毒軟體是否阻擋")
                messagebox.showerror("錯誤", f"生成字幕時發生錯誤:\n{e}\n\n請檢查日誌中的詳細資訊")
            finally:
                self.stop_progress()
                self.log("=" * 50)
        
        # 在新線程中執行
        thread = threading.Thread(target=run_whisper, daemon=True)
        thread.start()
    
    def run_whisper_python_api(self, input_file: str, output_srt: str) -> bool:
        """使用 Python API 直接調用 Whisper（優化版本）"""
        try:
            # 抑制 Whisper 警告
            import warnings
            warnings.filterwarnings("ignore", message=".*Failed to launch Triton kernels.*")
            warnings.filterwarnings("ignore", message=".*falling back to a slower.*")
            
            import whisper
            
            # 檢查輸入檔案是否存在
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"輸入檔案不存在: {input_file}")
            
            # 檢查輸出目錄是否存在，如果不存在則創建
            output_dir = os.path.dirname(output_srt)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    self.log(f"🔧 創建輸出目錄: {output_dir}")
                except Exception as e:
                    self.log(f"❌ 創建輸出目錄失敗: {e}")
                    return False
            
            # 嘗試載入優化器，如果失敗則使用基本版本
            try:
                from whisper_accuracy_optimizer import WhisperAccuracyOptimizer
                optimizer = WhisperAccuracyOptimizer()
                self.log("🐍 使用優化版 Python API 調用 Whisper...")
                use_optimizer = True
            except ImportError as e:
                self.log(f"⚠️ 優化器未找到: {e}")
                self.log("⚠️ 使用基本版 Python API...")
                optimizer = None
                use_optimizer = False
            except Exception as e:
                self.log(f"⚠️ 載入優化器時出錯: {e}")
                self.log("⚠️ 使用基本版 Python API...")
                optimizer = None
                use_optimizer = False
            
            # 決定內容類型
            if self.content_type.get() == "auto":
                content_type = "music" if self.music_mode.get() else "speech"
            else:
                content_type = self.content_type.get()
            
            # 智能語言偵測
            language = self.language.get()
            if language == "auto":
                self.log("🔍 使用自動語言偵測...")
                language = None  # Whisper 會自動偵測
            else:
                self.log(f"🌍 使用指定語言: {language}")
            
            # 決定品質等級
            if self.quality_level.get() == "auto":
                # 根據模型大小自動決定品質等級
                quality_map = {
                    "tiny": "fast",
                    "base": "balanced", 
                    "small": "balanced",
                    "medium": "high",
                    "large": "ultra"
                }
                quality_level = quality_map.get(self.whisper_model.get(), "high")
            else:
                quality_level = self.quality_level.get()
            
            self.log(f"🎯 內容類型: {content_type}, 語言: {language if language else 'auto'}, 品質等級: {quality_level}")
            
            # 獲取優化參數
            if use_optimizer:
                optimized_params = optimizer.optimize_whisper_params(
                    content_type=content_type,
                    language=language if language else "auto",
                    quality_level=quality_level
                )
                
                self.log("⚙️ 使用優化參數:")
                for key, value in optimized_params.items():
                    if key != "temperature":  # temperature 會特別處理
                        self.log(f"   {key}: {value}")
            else:
                # 使用基本參數
                optimized_params = {
                    "language": language,  # None 表示自動偵測
                    "temperature": [0.0],
                    "no_speech_threshold": self.no_speech_threshold.get(),
                    "condition_on_previous_text": False
                }
                self.log("⚙️ 使用基本參數（無優化器）")
            
            # 決定使用的設備
            device = "cpu"
            if self.use_gpu.get():
                try:
                    import torch
                    if torch.cuda.is_available():
                        device = "cuda"
                        self.log("🚀 Python API 使用 GPU 加速")
                        self.log("ℹ️ 注意: Windows 上可能會看到 Triton 警告，但 GPU 仍正常工作")
                    else:
                        self.log("💻 GPU 不可用，Python API 使用 CPU")
                except ImportError:
                    self.log("💻 PyTorch 未安裝，Python API 使用 CPU")
            else:
                self.log("💻 Python API 強制使用 CPU")
            
            # 載入模型
            self.set_status("正在載入 Whisper 模型...", "blue")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = whisper.load_model(self.whisper_model.get(), device=device)
                self.log(f"✅ 模型 {self.whisper_model.get()} 載入成功 (設備: {device})")
            except Exception as e:
                self.log(f"❌ 模型載入失敗: {e}")
                import traceback
                self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                return False
            
            # 根據設定決定是否使用多次通過轉錄
            if self.multi_pass_mode.get() and use_optimizer:
                self.set_status("正在執行多次通過轉錄...", "blue")
                try:
                    result = optimizer.multi_pass_transcription(
                        model=model,
                        audio_file=input_file,
                        params=optimized_params,
                        language=language
                    )
                    self.log("✅ 多次通過轉錄完成")
                except Exception as e:
                    self.log(f"❌ 多次通過轉錄失敗: {e}")
                    import traceback
                    self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                    return False
            else:
                self.set_status("正在執行單次轉錄...", "blue")
                # 使用優化參數進行單次轉錄
                try:
                    whisper_params = {k: v for k, v in optimized_params.items() 
                                    if k not in ["temperature"] and v is not None}
                    temperature = optimized_params.get("temperature", [0.0])
                    if isinstance(temperature, list):
                        temperature = temperature[0]  # 使用第一個溫度值
                    
                    self.log(f"🔧 轉錄參數: {whisper_params}")
                    self.log(f"🔧 溫度: {temperature}")
                    
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        result = model.transcribe(
                            input_file,
                            temperature=temperature,
                            **whisper_params
                        )
                    self.log("✅ 單次轉錄完成")
                except Exception as e:
                    self.log(f"❌ 單次轉錄失敗: {e}")
                    import traceback
                    self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                    return False
            
            # 生成 SRT 字幕
            if use_optimizer:
                self.set_status("正在生成優化的 SRT 字幕...", "blue")
                try:
                    srt_content = optimizer.generate_optimized_srt(
                        result=result,
                        language=language,
                        filter_repetitive=self.filter_repetitive.get(),
                        merge_short_segments=True
                    )
                except Exception as e:
                    self.log(f"❌ 生成優化 SRT 失敗: {e}")
                    import traceback
                    self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                    return False
            else:
                self.set_status("正在生成 SRT 字幕...", "blue")
                srt_content = self.generate_basic_srt(result)
            
            # 寫入檔案
            try:
                with open(output_srt, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                self.log(f"✅ 檔案寫入成功: {output_srt}")
            except Exception as e:
                self.log(f"❌ 檔案寫入失敗: {e}")
                import traceback
                self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                return False
            
            # 驗證檔案是否成功寫入
            if os.path.exists(output_srt):
                file_size = os.path.getsize(output_srt)
                subtitle_count = srt_content.count('-->')
                original_count = len(result.get("segments", []))
                
                self.log(f"✅ 優化的 SRT 檔案已生成: {output_srt}")
                self.log(f"📊 檔案大小: {file_size} bytes")
                self.log(f"📊 原始片段: {original_count}, 優化後: {subtitle_count}")
                
                if use_optimizer and original_count > 0:
                    reduction_rate = (original_count - subtitle_count) / original_count * 100
                    self.log(f"📊 優化率: {reduction_rate:.1f}% (移除了 {original_count - subtitle_count} 個低品質片段)")
                
                # 保存優化報告
                if use_optimizer:
                    try:
                        quality_scores = []
                        for segment in result.get("segments", []):
                            if "avg_logprob" in segment:
                                quality_scores.append(max(0, min(1, (segment["avg_logprob"] + 3) / 3)))
                        
                        optimizer.save_optimization_report(
                            original_segments=original_count,
                            final_segments=subtitle_count,
                            quality_scores=quality_scores,
                            output_path=output_srt
                        )
                    except Exception as e:
                        self.log(f"⚠️ 保存優化報告失敗: {e}")
                
                if subtitle_count > 0:
                    if use_optimizer:
                        self.set_status("✅ 優化版 Python API 字幕生成完成！", "green")
                    else:
                        self.set_status("✅ Python API 字幕生成完成！", "green")
                    return True
                else:
                    self.log("⚠️ 字幕檔案為空，可能需要調整參數")
                    return False
            else:
                self.log("❌ 檔案寫入失敗")
                return False
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"❌ 優化版 Python API 執行失敗: {e}")
            self.log(f"� 詳細錯誤信息:\n{error_details}")
            return False
    
    def generate_basic_srt(self, result):
        """生成基本的 SRT 字幕（無優化器時使用）"""
        srt_content = ""
        segments = result.get("segments", [])
        
        for i, segment in enumerate(segments, 1):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"].strip()
            
            if not text:
                continue
            
            # 格式化時間
            start_str = self.seconds_to_srt_time(start_time)
            end_str = self.seconds_to_srt_time(end_time)
            
            # 添加字幕片段
            srt_content += f"{i}\n"
            srt_content += f"{start_str} --> {end_str}\n"
            srt_content += f"{text}\n\n"
        
        return srt_content
    
    def seconds_to_srt_time(self, seconds):
        """將秒數轉換為 SRT 時間格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def run_basic_whisper_api(self, input_file: str, output_srt: str) -> bool:
        """基本版本的 Whisper API（作為備用方案）"""
        try:
            import warnings
            warnings.filterwarnings("ignore", message=".*Failed to launch Triton kernels.*")
            warnings.filterwarnings("ignore", message=".*falling back to a slower.*")
            
            import whisper
            
            self.log("🔄 使用基本版 Python API...")
            
            # 檢查輸入檔案是否存在
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"輸入檔案不存在: {input_file}")
                
            # 檢查輸出目錄是否存在，如果不存在則創建
            output_dir = os.path.dirname(output_srt)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    self.log(f"🔧 創建輸出目錄: {output_dir}")
                except Exception as e:
                    self.log(f"❌ 創建輸出目錄失敗: {e}")
                    return False
            
            # 決定使用的設備
            device = "cpu"
            if self.use_gpu.get():
                try:
                    import torch
                    if torch.cuda.is_available():
                        device = "cuda"
                        self.log("🚀 基本API使用 GPU 加速")
                    else:
                        self.log("💻 GPU不可用，基本API使用 CPU")
                except ImportError:
                    self.log("💻 PyTorch未安裝，基本API使用 CPU")
            else:
                self.log("💻 基本API強制使用 CPU")
            
            # 載入模型
            self.log(f"📥 正在載入模型: {self.whisper_model.get()} (設備: {device})")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    model = whisper.load_model(self.whisper_model.get(), device=device)
                    self.log(f"✅ 模型載入成功")
                except Exception as e:
                    self.log(f"❌ 模型載入失敗: {e}")
                    return False
            
            # 基本轉錄選項
            language = self.language.get()
            options = {
                "language": language if language != "auto" else None,
                "task": "transcribe",
                "no_speech_threshold": self.no_speech_threshold.get(),
                "temperature": self.temperature.get(),
                "condition_on_previous_text": False,
            }
            
            if language == "auto":
                self.log("🔍 基本API使用自動語言偵測...")
            else:
                self.log(f"🌍 基本API使用指定語言: {language}")
            
            # 執行轉錄
            try:
                self.log("🚀 開始轉錄...")
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    result = model.transcribe(input_file, **options)
                self.log("✅ 轉錄完成")
            except Exception as e:
                self.log(f"❌ 轉錄失敗: {e}")
                import traceback
                self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                return False
            
            # 生成基本 SRT
            try:
                self.log("📝 生成 SRT 內容...")
                srt_content = self.generate_srt_from_result(result)
                self.log("✅ SRT 內容生成完成")
            except Exception as e:
                self.log(f"❌ SRT 生成失敗: {e}")
                import traceback
                self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                return False
            
            # 寫入檔案
            try:
                with open(output_srt, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                self.log(f"✅ 檔案寫入成功: {output_srt}")
            except Exception as e:
                self.log(f"❌ 檔案寫入失敗: {e}")
                import traceback
                self.log(f"🔍 詳細錯誤:\n{traceback.format_exc()}")
                return False
            
            if os.path.exists(output_srt):
                subtitle_count = srt_content.count('-->')
                self.log(f"✅ 基本版 SRT 檔案已生成，字幕片段: {subtitle_count} 個")
                return subtitle_count > 0
            
            return False
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"❌ 基本版 API 也失敗: {e}")
            self.log(f"🔍 詳細錯誤信息:\n{error_details}")
            return False
    
    def generate_srt_from_result(self, result) -> str:
        """從 Whisper 結果生成 SRT 格式"""
        srt_content = ""
        filtered_segments = []
        
        # 過濾重複和無意義的內容
        for segment in result["segments"]:
            text = segment["text"].strip()
            
            # 跳過空白或太短的內容
            if len(text) < 2:
                continue
            
            # 過濾重複內容
            if self.filter_repetitive.get():
                # 檢查是否與前面的內容重複
                is_repetitive = False
                for prev_segment in filtered_segments[-3:]:  # 檢查最近3個片段
                    if self.is_similar_text(text, prev_segment["text"]):
                        is_repetitive = True
                        break
                
                if is_repetitive:
                    self.log(f"⚠️ 跳過重複內容: {text[:30]}...")
                    continue
            
            # 使用增強版音樂內容過濾器
            try:
                from enhanced_music_filter import filter_music_content
                should_keep, cleaned_text = filter_music_content(text)
                
                if not should_keep:
                    continue
                
                # 使用清理後的文字
                text = cleaned_text
                
            except ImportError:
                # 如果增強版過濾器不可用，使用基本過濾
                meaningless_patterns = [
                    "作詞・作曲・編曲", "作詞", "作曲", "編曲",
                    "初音ミク", "ボーカロイド", "VOCALOID",
                    "♪", "♫", "♬", "♩"
                ]
                
                is_meaningless = any(pattern in text for pattern in meaningless_patterns)
                if is_meaningless and (len(text) < 50 or text.count("作詞") > 2):
                    self.log(f"⚠️ 跳過無意義內容: {text[:30]}...")
                    continue
            
            filtered_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": text
            })
        
        # 生成 SRT 內容
        for i, segment in enumerate(filtered_segments, 1):
            start_time = self.seconds_to_srt_time(segment["start"])
            end_time = self.seconds_to_srt_time(segment["end"])
            text = segment["text"]
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
        
        self.log(f"📊 原始片段: {len(result['segments'])}, 過濾後: {len(filtered_segments)}")
        return srt_content
    
    def is_similar_text(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """檢查兩個文字是否相似"""
        # 簡單的相似度檢查
        if text1 == text2:
            return True
        
        # 檢查包含關係
        if len(text1) > 10 and len(text2) > 10:
            if text1 in text2 or text2 in text1:
                return True
        
        # 檢查字符重疊度
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        if len(set1) > 0 and len(set2) > 0:
            overlap = len(set1.intersection(set2))
            similarity = overlap / max(len(set1), len(set2))
            return similarity > threshold
        
        return False
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """將秒數轉換為 SRT 時間格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def preview_subtitles(self):
        """預覽字幕內容"""
        try:
            # 嘗試不同編碼讀取字幕檔案
            content = None
            used_encoding = None
            
            for encoding in ['utf-8', 'utf-8-sig', 'cp950', 'gbk', 'latin1']:
                try:
                    with open(self.output_srt_path.get(), 'r', encoding=encoding) as f:
                        content = f.read()
                        used_encoding = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                messagebox.showerror("錯誤", "無法讀取字幕檔案，可能是編碼問題")
                return
            
            # 建立預覽視窗
            preview_window = tk.Toplevel(self.root)
            preview_window.title(f"字幕預覽 (編碼: {used_encoding})")
            preview_window.geometry("600x400")
            
            text_widget = tk.Text(preview_window, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(preview_window, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.insert(1.0, content)
            text_widget.config(state=tk.DISABLED)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            messagebox.showerror("錯誤", f"無法預覽字幕: {e}")
    
    def open_subtitle_editor(self):
        """開啟字幕編輯器"""
        srt_file = self.output_srt_path.get()
        if not srt_file or not os.path.exists(srt_file):
            messagebox.showwarning("警告", "請先選擇一個存在的字幕檔案")
            return
        
        try:
            # 檢查字幕編輯器檔案是否存在
            script_dir = os.path.dirname(os.path.abspath(__file__))
            editor_path = os.path.join(script_dir, "subtitle_editor.py")
            
            if not os.path.exists(editor_path):
                messagebox.showerror("錯誤", "找不到字幕編輯器檔案 (subtitle_editor.py)")
                return
            
            # 啟動字幕編輯器
            import subprocess
            subprocess.Popen([sys.executable, editor_path, srt_file], 
                           cwd=script_dir, shell=False)
            self.log(f"✏️ 已開啟字幕編輯器: {srt_file}")
            
        except Exception as e:
            self.log(f"❌ 開啟字幕編輯器失敗: {e}")
            messagebox.showerror("錯誤", f"無法開啟字幕編輯器: {e}")
    
    def burn_subtitles(self):
        """燒錄字幕到影片"""
        if not self.validate_inputs(check_srt=True):
            return
        
        def run_burn():
            try:
                self.start_progress()
                self.set_status("正在準備燒錄字幕...", "blue")
                self.log("=" * 50)
                self.log("🔥 開始字幕燒錄處理")
                self.log("=" * 50)
                
                # 檢查檔案
                video_file = self.video_path.get()
                srt_file = self.output_srt_path.get()
                output_file = self.output_video_path.get()
                
                self.log(f"📹 影片檔案: {video_file}")
                self.log(f"📝 字幕檔案: {srt_file}")
                self.log(f"💾 輸出檔案: {output_file}")
                
                # 檢查檔案大小
                video_size = os.path.getsize(video_file) / (1024 * 1024)  # MB
                self.log(f"📊 影片大小: {video_size:.1f} MB")
                
                # 檢查字幕內容
                try:
                    with open(srt_file, 'r', encoding='utf-8') as f:
                        srt_content = f.read()
                        subtitle_count = srt_content.count('-->')
                        self.log(f"📊 字幕片段數量: {subtitle_count}")
                except Exception as e:
                    self.log(f"⚠️ 讀取字幕檔案時出錯: {e}")
                
                self.set_status("正在載入影片和字幕...", "blue")
                
                # 更新設定檔
                config = {
                    "subtitle_settings": {
                        "font_size": self.font_size.get(),
                        "margin": self.margin.get()
                    }
                }
                
                import tempfile
                temp_dir = tempfile.gettempdir()
                config_path = os.path.join(temp_dir, f"temp_config_{os.getpid()}.json")
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                
                self.log(f"⚙️ 字幕設定: 字體大小={self.font_size.get()}, 邊距={self.margin.get()}")
                
                # 使用我們的 video_processor
                self.set_status("正在處理影片和字幕...", "blue")
                self.log("🎬 開始影片處理...")
                
                from video_processor import VideoProcessor
                processor = VideoProcessor(config_path)
                
                # 這裡可以添加進度回調，但先用基本版本
                processor.burn_subtitles_to_video(
                    video_file,
                    srt_file,
                    output_file
                )
                
                # 清理臨時檔案
                if os.path.exists(config_path):
                    os.remove(config_path)
                
                # 檢查輸出檔案
                if os.path.exists(output_file):
                    output_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                    self.log(f"✅ 輸出檔案大小: {output_size:.1f} MB")
                    
                    self.set_status("✅ 字幕燒錄完成！", "green")
                    self.log("🎉 字幕燒錄成功完成！")
                    self.log(f"💾 檔案已儲存至: {output_file}")
                    
                    messagebox.showinfo("完成", f"字幕燒錄完成！\n\n輸出檔案: {output_file}\n檔案大小: {output_size:.1f} MB")
                else:
                    raise Exception("輸出檔案未生成")
                
            except Exception as e:
                self.set_status(f"❌ 燒錄失敗: {e}", "red")
                self.log(f"❌ 燒錄錯誤: {e}")
                self.log("💡 可能的原因:")
                self.log("   - 磁碟空間不足")
                self.log("   - 輸出路徑權限不足")
                self.log("   - 影片檔案損壞")
                self.log("   - 字幕檔案格式錯誤")
                messagebox.showerror("錯誤", f"燒錄字幕失敗:\n{e}\n\n請檢查日誌中的詳細資訊")
            finally:
                self.stop_progress()
                self.log("=" * 50)
        
        # 在新線程中執行
        thread = threading.Thread(target=run_burn, daemon=True)
        thread.start()
    
    def process_all_in_one(self):
        """一鍵完成生成和燒錄"""
        if not self.validate_inputs():
            return
        
        def run_all():
            # 先生成字幕
            self.generate_subtitles()
            
            # 等待字幕生成完成
            while self.is_processing:
                self.root.after(100)
            
            # 如果字幕生成成功，繼續燒錄
            if os.path.exists(self.output_srt_path.get()):
                self.root.after(1000, self.burn_subtitles)  # 延遲 1 秒後開始燒錄
        
        # 在新線程中執行
        thread = threading.Thread(target=run_all, daemon=True)
        thread.start()
    
    def run(self):
        """執行應用程式"""
        # 儲存設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def show_music_help(self):
        """顯示音樂識別幫助"""
        try:
            # 檢查是否存在音樂故障排除指南
            help_file_path = os.path.join(os.path.dirname(__file__), "music_troubleshooting.md")
            if os.path.exists(help_file_path):
                with open(help_file_path, 'r', encoding='utf-8') as f:
                    help_content = f.read()
            else:
                help_content = """音樂識別幫助指南

🎵 音樂模式設定：
• 啟用「音樂模式」可以優化歌曲識別
• 降低「靜音閾值」到 0.3-0.4
• 適當提高「溫度」到 0.2-0.3

🔧 參數調整建議：
• 使用 medium 或 large 模型獲得更好效果
• 啟用「過濾重複內容」避免歌詞重複
• 使用高品質 WAV 音訊檔案

⚠️ 常見問題：
• 歌詞識別不完整 → 降低靜音閾值
• 出現重複內容 → 啟用過濾功能
• 識別語言錯誤 → 手動指定語言

💡 最佳實踐：
• 先用小模型測試，確認參數後再用大模型
• 對於複雜歌曲，可以嘗試多個溫度設定
• 使用字幕編輯器進行後期調整"""
            
            # 建立幫助視窗
            help_window = tk.Toplevel(self.root)
            help_window.title("音樂識別幫助")
            help_window.geometry("600x500")
            
            text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.insert(1.0, help_content)
            text_widget.config(state=tk.DISABLED)
            
            scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            messagebox.showerror("錯誤", f"無法顯示幫助: {e}")
    
    def show_optimization_help(self):
        """顯示優化功能說明"""
        help_content = """🚀 Whisper 智能優化功能說明

✨ 智能優化 (推薦開啟)：
• 自動調整識別參數以提高準確度
• 智能過濾重複和無意義內容
• 根據內容類型優化處理策略
• 生成詳細的優化報告

🔄 多次通過模式：
• 使用多個溫度值進行轉錄
• 自動選擇品質最佳的結果
• 提高準確度但增加處理時間
• 適合重要內容的精確轉錄

📊 品質等級設定：
• auto: 根據模型自動選擇
• fast: 快速模式，適合預覽
• balanced: 平衡模式，日常使用
• high: 高品質模式，推薦設定
• ultra: 超高品質，最佳準確度

🎯 內容類型設定：
• auto: 根據音樂模式自動判斷
• speech: 語音內容優化
• music: 音樂/歌曲內容優化
• mixed: 混合內容處理

💡 使用建議：
• 首次使用建議開啟智能優化
• 對於重要內容可啟用多次通過模式
• 根據內容特性選擇合適的類型
• 查看優化報告了解處理效果

⚠️ 注意事項：
• 優化功能會增加處理時間
• 多次通過模式需要更多計算資源
• 優化報告會保存在字幕檔案旁邊
• 如果優化失敗會自動回退到基本模式"""
        
        # 建立說明視窗
        help_window = tk.Toplevel(self.root)
        help_window.title("優化功能說明")
        help_window.geometry("700x600")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, help_content)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_closing(self):
        """關閉程式時的處理"""
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    app = WhisperSubtitleGUI()
    app.run()