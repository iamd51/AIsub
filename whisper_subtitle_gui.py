#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import json
from pathlib import Path

class WhisperSubtitleGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Whisper 字幕生成器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 變數
        self.video_path = tk.StringVar()
        self.audio_path = tk.StringVar()
        self.output_srt_path = tk.StringVar()
        self.output_video_path = tk.StringVar()
        self.whisper_model = tk.StringVar(value="medium")
        self.language = tk.StringVar(value="ja")
        self.use_audio_file = tk.BooleanVar(value=False)
        self.custom_model_dir = tk.StringVar()
        self.use_custom_model_dir = tk.BooleanVar(value=False)
        self.is_processing = False
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """設定使用者介面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 標題
        title_label = ttk.Label(main_frame, text="Whisper 字幕生成器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 模式選擇
        mode_frame = ttk.LabelFrame(main_frame, text="操作模式", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.operation_mode = tk.StringVar(value="generate_and_burn")
        
        ttk.Radiobutton(mode_frame, text="生成字幕 + 燒錄影片", variable=self.operation_mode, 
                       value="generate_and_burn", command=self.update_ui_mode).grid(row=0, column=0, sticky=tk.W, padx=10)
        ttk.Radiobutton(mode_frame, text="僅燒錄現有字幕到影片", variable=self.operation_mode, 
                       value="burn_only", command=self.update_ui_mode).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # 檔案選擇區域
        file_frame = ttk.LabelFrame(main_frame, text="檔案選擇", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
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
        
        # Whisper 設定區域
        self.whisper_frame = ttk.LabelFrame(main_frame, text="Whisper 設定", padding="10")
        self.whisper_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 模型選擇
        ttk.Label(self.whisper_frame, text="模型大小:").grid(row=0, column=0, sticky=tk.W, pady=2)
        model_combo = ttk.Combobox(self.whisper_frame, textvariable=self.whisper_model, 
                                  values=["tiny", "base", "small", "medium", "large"], 
                                  state="readonly", width=15)
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 語言選擇
        ttk.Label(self.whisper_frame, text="語言:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        lang_combo = ttk.Combobox(self.whisper_frame, textvariable=self.language,
                                 values=["ja", "en", "zh", "ko", "auto"], 
                                 state="readonly", width=10)
        lang_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # 模型說明
        model_info = ttk.Label(self.whisper_frame, text="模型說明: tiny(快速) → base → small → medium(推薦) → large(最準確)", 
                              font=("Arial", 8), foreground="gray")
        model_info.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 模型位置設定
        self.custom_model_check = ttk.Checkbutton(self.whisper_frame, text="自訂模型位置", 
                                                 variable=self.use_custom_model_dir, 
                                                 command=self.toggle_custom_model_dir)
        self.custom_model_check.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        self.model_dir_entry = ttk.Entry(self.whisper_frame, textvariable=self.custom_model_dir, width=40, state="disabled")
        self.model_dir_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        
        self.model_dir_btn = ttk.Button(self.whisper_frame, text="瀏覽", command=self.select_model_directory, state="disabled")
        self.model_dir_btn.grid(row=2, column=3, padx=5)
        
        # 模型管理按鈕
        model_mgmt_frame = ttk.Frame(self.whisper_frame)
        model_mgmt_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(model_mgmt_frame, text="查看預設位置", command=self.show_default_model_location).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(model_mgmt_frame, text="檢查已下載模型", command=self.check_downloaded_models).pack(side=tk.LEFT, padx=5)
        ttk.Button(model_mgmt_frame, text="設定環境變數", command=self.show_env_setup).pack(side=tk.LEFT, padx=5)
        
        # 字幕設定區域
        subtitle_frame = ttk.LabelFrame(main_frame, text="字幕設定", padding="10")
        subtitle_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 字體大小
        ttk.Label(subtitle_frame, text="字體大小:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.font_size = tk.IntVar(value=48)
        font_size_spin = ttk.Spinbox(subtitle_frame, from_=20, to=100, textvariable=self.font_size, width=10)
        font_size_spin.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 字幕位置
        ttk.Label(subtitle_frame, text="底部邊距:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        self.margin = tk.IntVar(value=80)
        margin_spin = ttk.Spinbox(subtitle_frame, from_=20, to=200, textvariable=self.margin, width=10)
        margin_spin.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # 控制按鈕區域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 主要按鈕
        self.generate_btn = ttk.Button(control_frame, text="1. 生成字幕 (Whisper)", 
                                      command=self.generate_subtitles, style="Accent.TButton")
        self.generate_btn.grid(row=0, column=0, padx=10)
        
        self.burn_btn = ttk.Button(control_frame, text="2. 燒錄字幕到影片", 
                                  command=self.burn_subtitles, state="disabled")
        self.burn_btn.grid(row=0, column=1, padx=10)
        
        self.all_in_one_btn = ttk.Button(control_frame, text="一鍵完成 (生成+燒錄)", 
                                        command=self.process_all_in_one, style="Accent.TButton")
        self.all_in_one_btn.grid(row=0, column=2, padx=10)
        
        self.burn_only_btn = ttk.Button(control_frame, text="僅燒錄字幕", 
                                       command=self.burn_subtitles, style="Accent.TButton")
        self.burn_only_btn.grid(row=0, column=3, padx=10)
        
        # 進度條
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 狀態標籤
        self.status_label = ttk.Label(main_frame, text="準備就緒", foreground="green")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # 日誌區域
        log_frame = ttk.LabelFrame(main_frame, text="處理日誌", padding="5")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 設定網格權重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 初始化 UI 模式
        self.update_ui_mode()
    
    def load_config(self):
        """載入設定檔"""
        try:
            if os.path.exists("whisper_config.json"):
                with open("whisper_config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.whisper_model.set(config.get("model", "medium"))
                    self.language.set(config.get("language", "ja"))
                    self.font_size.set(config.get("font_size", 48))
                    self.margin.set(config.get("margin", 80))
                    self.use_audio_file.set(config.get("use_audio_file", False))
                    self.use_custom_model_dir.set(config.get("use_custom_model_dir", False))
                    self.custom_model_dir.set(config.get("custom_model_dir", ""))
                    self.operation_mode.set(config.get("operation_mode", "generate_and_burn"))
                    self.toggle_audio_input()  # 更新界面狀態
                    self.toggle_custom_model_dir()  # 更新模型目錄界面狀態
                    self.update_ui_mode()  # 更新操作模式界面
        except Exception as e:
            self.log(f"載入設定失敗: {e}")
    
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
                "operation_mode": self.operation_mode.get()
            }
            with open("whisper_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"儲存設定失敗: {e}")
    
    def select_video_file(self):
        """選擇影片檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇影片檔案",
            filetypes=[
                ("影片檔案", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
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
                ("音訊檔案", "*.wav *.mp3 *.flac *.m4a *.aac"),
                ("WAV 檔案", "*.wav"),
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
    
    def update_ui_mode(self):
        """根據操作模式更新 UI"""
        mode = self.operation_mode.get()
        
        if mode == "generate_and_burn":
            # 生成字幕模式
            self.srt_label.config(text="字幕檔案 (輸出):")
            self.srt_btn.config(command=self.select_srt_output)
            
            # 顯示 Whisper 設定
            self.whisper_frame.grid()
            
            # 顯示音訊選項
            self.use_audio_check.grid()
            if self.use_audio_file.get():
                self.audio_entry.grid()
                self.audio_btn.grid()
            
            # 按鈕狀態
            self.generate_btn.grid()
            self.burn_btn.grid()
            self.all_in_one_btn.grid()
            self.burn_only_btn.grid_remove()
            
            self.log("模式: 生成字幕 + 燒錄影片")
            
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
            self.generate_btn.grid_remove()
            self.burn_btn.grid_remove()
            self.all_in_one_btn.grid_remove()
            self.burn_only_btn.grid()
            
            self.log("模式: 僅燒錄現有字幕到影片")
    
    def select_srt_file(self):
        """根據模式選擇 SRT 檔案"""
        if self.operation_mode.get() == "generate_and_burn":
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
        self.burn_btn.config(state="disabled")
        self.all_in_one_btn.config(state="disabled")
        self.burn_only_btn.config(state="disabled")
    
    def stop_progress(self):
        """停止進度條"""
        self.progress.stop()
        self.is_processing = False
        
        mode = self.operation_mode.get()
        if mode == "generate_and_burn":
            self.generate_btn.config(state="normal")
            if os.path.exists(self.output_srt_path.get()):
                self.burn_btn.config(state="normal")
            self.all_in_one_btn.config(state="normal")
        elif mode == "burn_only":
            self.burn_only_btn.config(state="normal")
    
    def validate_inputs(self, check_srt=False):
        """驗證輸入"""
        mode = self.operation_mode.get()
        
        if mode == "generate_and_burn":
            # 生成字幕模式的驗證
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
                self.set_status("正在使用 Whisper 生成字幕...", "blue")
                self.log("開始 Whisper 字幕生成...")
                
                # 決定輸入檔案
                input_file = self.audio_path.get() if self.use_audio_file.get() else self.video_path.get()
                
                # 設定環境變數（如果使用自訂模型位置）
                env = os.environ.copy()
                if self.use_custom_model_dir.get() and self.custom_model_dir.get():
                    env['WHISPER_CACHE_DIR'] = self.custom_model_dir.get()
                    self.log(f"使用自訂模型位置: {self.custom_model_dir.get()}")
                
                # 建立 Whisper 命令
                cmd = [
                    "whisper",
                    input_file,
                    "--model", self.whisper_model.get(),
                    "--output_format", "srt",
                    "--output_dir", str(Path(self.output_srt_path.get()).parent),
                    "--verbose", "True"
                ]
                
                # 添加語言參數（如果不是自動偵測）
                if self.language.get() != "auto":
                    cmd.extend(["--language", self.language.get()])
                
                # 如果使用音訊檔案，添加額外的精確度選項
                if self.use_audio_file.get():
                    cmd.extend([
                        "--word_timestamps", "True",  # 詞級時間戳
                        "--condition_on_previous_text", "True"  # 基於前文的條件生成
                    ])
                
                self.log(f"執行命令: {' '.join(cmd)}")
                
                # 執行 Whisper
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    env=env  # 使用修改後的環境變數
                )
                
                # 即時顯示輸出
                for line in process.stdout:
                    self.log(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    # 尋找生成的 SRT 檔案
                    input_name = Path(input_file).stem
                    generated_srt = Path(self.output_srt_path.get()).parent / f"{input_name}.srt"
                    
                    if generated_srt.exists():
                        # 如果輸出路徑不同，移動檔案
                        if str(generated_srt) != self.output_srt_path.get():
                            generated_srt.rename(self.output_srt_path.get())
                        
                        self.set_status("字幕生成完成！", "green")
                        self.log(f"字幕已儲存至: {self.output_srt_path.get()}")
                        self.burn_btn.config(state="normal")
                        
                        # 詢問是否要預覽字幕
                        if messagebox.askyesno("完成", "字幕生成完成！是否要預覽字幕內容？"):
                            self.preview_subtitles()
                    else:
                        self.set_status("找不到生成的字幕檔案", "red")
                        self.log("錯誤: 找不到生成的字幕檔案")
                else:
                    self.set_status("Whisper 執行失敗", "red")
                    self.log(f"Whisper 執行失敗，返回碼: {process.returncode}")
                
            except FileNotFoundError:
                self.set_status("找不到 Whisper", "red")
                self.log("錯誤: 找不到 Whisper 程式，請確認已正確安裝")
                messagebox.showerror("錯誤", "找不到 Whisper 程式\n請執行: pip install openai-whisper")
            except Exception as e:
                self.set_status(f"生成字幕失敗: {e}", "red")
                self.log(f"錯誤: {e}")
            finally:
                self.stop_progress()
        
        # 在新線程中執行
        thread = threading.Thread(target=run_whisper, daemon=True)
        thread.start()
    
    def preview_subtitles(self):
        """預覽字幕內容"""
        try:
            with open(self.output_srt_path.get(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 建立預覽視窗
            preview_window = tk.Toplevel(self.root)
            preview_window.title("字幕預覽")
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
    
    def burn_subtitles(self):
        """燒錄字幕到影片"""
        if not self.validate_inputs(check_srt=True):
            return
        
        def run_burn():
            try:
                self.start_progress()
                self.set_status("正在燒錄字幕到影片...", "blue")
                self.log("開始燒錄字幕...")
                
                # 更新設定檔
                config = {
                    "subtitle_settings": {
                        "font_size": self.font_size.get(),
                        "margin": self.margin.get()
                    }
                }
                
                with open("temp_config.json", 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                
                # 使用我們的 video_processor
                from video_processor import VideoProcessor
                processor = VideoProcessor("temp_config.json")
                processor.burn_subtitles_to_video(
                    self.video_path.get(),
                    self.output_srt_path.get(),
                    self.output_video_path.get()
                )
                
                # 清理臨時檔案
                if os.path.exists("temp_config.json"):
                    os.remove("temp_config.json")
                
                self.set_status("字幕燒錄完成！", "green")
                self.log(f"影片已儲存至: {self.output_video_path.get()}")
                
                messagebox.showinfo("完成", f"字幕燒錄完成！\n輸出檔案: {self.output_video_path.get()}")
                
            except Exception as e:
                self.set_status(f"燒錄失敗: {e}", "red")
                self.log(f"燒錄錯誤: {e}")
                messagebox.showerror("錯誤", f"燒錄字幕失敗: {e}")
            finally:
                self.stop_progress()
        
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
    
    def on_closing(self):
        """關閉程式時的處理"""
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    app = WhisperSubtitleGUI()
    app.run()