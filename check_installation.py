#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Whisper 字幕生成器 - 安裝檢查工具
檢查所有必要的檔案和套件是否正確安裝
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

# 設定 Windows 編碼環境
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 嘗試設定控制台編碼
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass

def safe_print(text):
    """安全的列印函數，處理編碼問題"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 移除 emoji 和特殊字符
        safe_text = text.encode('ascii', errors='ignore').decode('ascii')
        print(safe_text)

def check_python_version():
    """檢查 Python 版本"""
    safe_print("[Python] 檢查 Python 版本...")
    version = sys.version_info
    safe_print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        safe_print("   [錯誤] Python 版本過舊，建議使用 Python 3.8 或更新版本")
        return False
    else:
        safe_print("   [成功] Python 版本符合要求")
        return True

def check_required_packages():
    """檢查必要套件"""
    safe_print("\n[套件] 檢查必要套件...")
    
    required_packages = [
        ("whisper", "OpenAI Whisper"),
        ("torch", "PyTorch"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("tkinter", "Tkinter (GUI)"),
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            importlib.import_module(package)
            safe_print(f"   [成功] {description}")
        except ImportError:
            safe_print(f"   [錯誤] {description} - 未安裝")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_project_files():
    """檢查專案檔案"""
    safe_print("\n[檔案] 檢查專案檔案...")
    
    required_files = [
        ("whisper_subtitle_gui.py", "主程式"),
        ("video_processor.py", "影片處理器"),
        ("subtitle_editor.py", "字幕編輯器"),
        ("requirements.txt", "套件需求檔案"),
        ("start_whisper_gui.bat", "啟動腳本"),
        ("install_whisper.bat", "安裝腳本"),
    ]
    
    optional_files = [
        ("whisper_accuracy_optimizer.py", "智能優化器（可選）"),
        ("whisper_config.json.template", "配置模板"),
        ("NotoSansCJK-Regular.ttc", "日文字體（可選）"),
    ]
    
    missing_files = []
    missing_optional = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 檢查必要檔案
    for filename, description in required_files:
        file_path = os.path.join(script_dir, filename)
        if os.path.exists(file_path):
            safe_print(f"   [成功] {description} ({filename})")
        else:
            safe_print(f"   [錯誤] {description} ({filename}) - 檔案不存在")
            missing_files.append(filename)
    
    # 檢查可選檔案
    safe_print("\n[檔案] 檢查可選檔案...")
    for filename, description in optional_files:
        file_path = os.path.join(script_dir, filename)
        if os.path.exists(file_path):
            safe_print(f"   [成功] {description} ({filename})")
        else:
            safe_print(f"   [警告] {description} ({filename}) - 檔案不存在（程式仍可運行）")
            missing_optional.append(filename)
    
    return len(missing_files) == 0, missing_files

def check_gpu_support():
    """檢查 GPU 支援"""
    safe_print("\n[GPU] 檢查 GPU 支援...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            safe_print(f"   [成功] CUDA 可用，找到 {gpu_count} 個 GPU")
            safe_print(f"   [資訊] GPU: {gpu_name}")
            return True
        else:
            safe_print("   [警告] CUDA 不可用，將使用 CPU 模式")
            return False
    except ImportError:
        safe_print("   [錯誤] PyTorch 未安裝，無法檢查 GPU")
        return False

def check_whisper_models():
    """檢查 Whisper 模型"""
    safe_print("\n[模型] 檢查 Whisper 模型...")
    
    # 檢查預設模型目錄
    import os
    model_dir = os.path.expanduser("~/.cache/whisper")
    
    if os.path.exists(model_dir):
        models = [f for f in os.listdir(model_dir) if f.endswith(('.pt', '.bin'))]
        if models:
            safe_print(f"   [成功] 找到 {len(models)} 個模型:")
            for model in models:
                model_path = os.path.join(model_dir, model)
                size_mb = os.path.getsize(model_path) / (1024 * 1024)
                safe_print(f"      [檔案] {model} ({size_mb:.1f} MB)")
        else:
            safe_print("   [警告] 模型目錄存在但沒有模型檔案")
            safe_print("   [提示] 首次使用時會自動下載")
    else:
        safe_print("   [警告] 模型目錄不存在")
        safe_print("   [提示] 首次使用時會自動創建並下載模型")

def check_font_files():
    """檢查字體檔案"""
    safe_print("\n[字體] 檢查字體檔案...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, "NotoSansCJK-Regular.ttc")
    
    if os.path.exists(font_path):
        size_mb = os.path.getsize(font_path) / (1024 * 1024)
        safe_print(f"   [成功] 日文字體已存在 ({size_mb:.1f} MB)")
    else:
        safe_print("   [警告] 日文字體不存在")
        safe_print("   [提示] 程式會自動下載，或使用系統字體")

def provide_solutions(missing_packages, missing_files):
    """提供解決方案"""
    if missing_packages or missing_files:
        safe_print("\n[解決方案]:")
        
        if missing_packages:
            safe_print("\n[套件] 安裝缺少的套件:")
            safe_print("   方法 1: 執行 install_whisper.bat")
            safe_print("   方法 2: 手動安裝")
            safe_print("   pip install openai-whisper torch opencv-python Pillow numpy")
        
        if missing_files:
            safe_print("\n[檔案] 缺少的檔案:")
            for filename in missing_files:
                safe_print(f"   [錯誤] {filename}")
            safe_print("   [提示] 請重新從 GitHub 下載完整專案")
            safe_print("   [連結] https://github.com/your-repo/whisper-subtitle-generator")

def main():
    """主函數"""
    safe_print("=" * 60)
    safe_print("    Whisper 字幕生成器 - 安裝檢查工具")
    safe_print("=" * 60)
    
    # 檢查各項目
    python_ok = check_python_version()
    packages_ok, missing_packages = check_required_packages()
    files_ok, missing_files = check_project_files()
    gpu_available = check_gpu_support()
    
    check_whisper_models()
    check_font_files()
    
    # 總結
    safe_print("\n" + "=" * 60)
    safe_print("[總結] 檢查結果總結:")
    safe_print("=" * 60)
    
    if python_ok and packages_ok and files_ok:
        safe_print("[成功] 所有檢查通過！程式應該可以正常運行")
        if gpu_available:
            safe_print("[GPU] GPU 加速可用，處理速度會更快")
        else:
            safe_print("[CPU] 將使用 CPU 模式，處理速度較慢但仍可正常工作")
    else:
        safe_print("[錯誤] 發現問題，需要修正:")
        if not python_ok:
            safe_print("   - Python 版本問題")
        if not packages_ok:
            safe_print("   - 套件安裝問題")
        if not files_ok:
            safe_print("   - 檔案缺失問題")
        
        provide_solutions(missing_packages, missing_files)
    
    safe_print("\n按任意鍵退出...")
    input()

if __name__ == "__main__":
    main()