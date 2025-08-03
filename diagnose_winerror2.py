#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
深度診斷 [WinError 2] 問題
專門針對 Whisper 音訊處理失敗的問題
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def safe_print(text):
    """安全的列印函數"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', errors='ignore').decode('ascii')
        print(safe_text)

def test_ffmpeg_basic():
    """基本 FFmpeg 測試"""
    safe_print("🔍 測試 FFmpeg 基本功能...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            safe_print("✅ FFmpeg 命令列可用")
            # 顯示版本資訊
            version_line = result.stdout.split('\n')[0]
            safe_print(f"   版本: {version_line}")
            return True
        else:
            safe_print(f"❌ FFmpeg 返回錯誤碼: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        safe_print("❌ FFmpeg 執行超時")
        return False
    except FileNotFoundError:
        safe_print("❌ FFmpeg 命令找不到")
        return False
    except Exception as e:
        safe_print(f"❌ FFmpeg 測試失敗: {e}")
        return False

def test_ffmpeg_audio_processing():
    """測試 FFmpeg 音訊處理功能"""
    safe_print("🎵 測試 FFmpeg 音訊處理...")
    
    try:
        # 創建一個簡單的測試音訊檔案（靜音）
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_path = temp_audio.name
        
        # 使用 FFmpeg 生成測試音訊
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=duration=1:sample_rate=16000:channels=1',
            '-y', temp_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(temp_path):
            safe_print("✅ FFmpeg 音訊處理正常")
            os.unlink(temp_path)  # 清理測試檔案
            return True
        else:
            safe_print(f"❌ FFmpeg 音訊處理失敗: {result.stderr}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return False
            
    except Exception as e:
        safe_print(f"❌ 音訊處理測試失敗: {e}")
        return False

def test_whisper_audio_loading():
    """測試 Whisper 音訊載入功能"""
    safe_print("🤖 測試 Whisper 音訊載入...")
    
    try:
        import whisper
        from whisper.audio import load_audio
        
        # 創建測試音訊檔案
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_path = temp_audio.name
        
        # 生成測試音訊
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=duration=2:sample_rate=16000:channels=1',
            '-y', temp_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            safe_print("❌ 無法創建測試音訊檔案")
            return False
        
        # 測試 Whisper 載入音訊
        try:
            audio_data = load_audio(temp_path)
            safe_print(f"✅ Whisper 音訊載入成功 (長度: {len(audio_data)} 樣本)")
            os.unlink(temp_path)
            return True
        except Exception as e:
            safe_print(f"❌ Whisper 音訊載入失敗: {e}")
            safe_print(f"   這就是 [WinError 2] 的原因！")
            os.unlink(temp_path)
            return False
            
    except ImportError:
        safe_print("❌ Whisper 模組未安裝")
        return False
    except Exception as e:
        safe_print(f"❌ Whisper 測試失敗: {e}")
        return False

def check_environment_variables():
    """檢查環境變數"""
    safe_print("🌍 檢查環境變數...")
    
    # 檢查 PATH
    path_env = os.environ.get('PATH', '')
    safe_print(f"PATH 長度: {len(path_env)} 字符")
    
    # 檢查是否包含 FFmpeg 路徑
    ffmpeg_paths = []
    for path in path_env.split(os.pathsep):
        if path and os.path.exists(os.path.join(path, 'ffmpeg.exe')):
            ffmpeg_paths.append(path)
    
    if ffmpeg_paths:
        safe_print(f"✅ 在 PATH 中找到 FFmpeg: {ffmpeg_paths}")
    else:
        safe_print("⚠️ PATH 中沒有 FFmpeg")
    
    # 檢查特殊環境變數
    special_vars = ['FFMPEG_BINARY', 'FFPROBE_BINARY']
    for var in special_vars:
        value = os.environ.get(var)
        if value:
            safe_print(f"✅ {var}: {value}")
        else:
            safe_print(f"ℹ️ {var}: 未設定")

def check_file_permissions():
    """檢查檔案權限"""
    safe_print("🔐 檢查檔案權限...")
    
    # 檢查當前目錄權限
    current_dir = os.getcwd()
    try:
        # 嘗試創建臨時檔案
        with tempfile.NamedTemporaryFile(dir=current_dir, delete=True) as temp_file:
            temp_file.write(b"test")
        safe_print("✅ 當前目錄有寫入權限")
    except Exception as e:
        safe_print(f"❌ 當前目錄權限問題: {e}")
    
    # 檢查 FFmpeg 執行權限
    try:
        result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            ffmpeg_path = result.stdout.strip().split('\n')[0]
            safe_print(f"✅ FFmpeg 位置: {ffmpeg_path}")
            
            # 檢查是否可執行
            if os.access(ffmpeg_path, os.X_OK):
                safe_print("✅ FFmpeg 有執行權限")
            else:
                safe_print("❌ FFmpeg 沒有執行權限")
        else:
            safe_print("❌ 找不到 FFmpeg 位置")
    except Exception as e:
        safe_print(f"❌ 權限檢查失敗: {e}")

def fix_environment_issues():
    """修復環境問題"""
    safe_print("🔧 嘗試修復環境問題...")
    
    script_dir = Path(__file__).parent
    
    # 檢查本地 FFmpeg
    local_ffmpeg = script_dir / "ffmpeg.exe"
    if local_ffmpeg.exists():
        safe_print("✅ 找到本地 FFmpeg")
        
        # 設定環境變數
        current_path = os.environ.get('PATH', '')
        if str(script_dir) not in current_path:
            os.environ['PATH'] = str(script_dir) + os.pathsep + current_path
            safe_print("✅ 已將程式目錄加入 PATH")
        
        os.environ['FFMPEG_BINARY'] = str(local_ffmpeg)
        safe_print("✅ 已設定 FFMPEG_BINARY")
        
        return True
    else:
        safe_print("❌ 本地沒有 FFmpeg")
        return False

def create_test_script():
    """創建測試腳本"""
    safe_print("📝 創建測試腳本...")
    
    test_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 設定環境變數
script_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")

if os.path.exists(ffmpeg_path):
    os.environ['PATH'] = script_dir + os.pathsep + os.environ.get('PATH', '')
    os.environ['FFMPEG_BINARY'] = ffmpeg_path
    print(f"✅ 環境設定完成: {ffmpeg_path}")
else:
    print("❌ 找不到 ffmpeg.exe")

# 測試 Whisper
try:
    import whisper
    from whisper.audio import load_audio
    print("✅ Whisper 模組載入成功")
    
    # 載入模型
    model = whisper.load_model("tiny")
    print("✅ 模型載入成功")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()
"""
    
    with open("test_whisper_env.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    safe_print("✅ 已創建 test_whisper_env.py")

def main():
    """主函數"""
    safe_print("=" * 60)
    safe_print("    [WinError 2] 深度診斷工具")
    safe_print("=" * 60)
    
    # 基本檢查
    ffmpeg_basic = test_ffmpeg_basic()
    ffmpeg_audio = test_ffmpeg_audio_processing()
    
    # 環境檢查
    check_environment_variables()
    check_file_permissions()
    
    # Whisper 測試
    whisper_ok = test_whisper_audio_loading()
    
    # 總結
    safe_print("\n" + "=" * 60)
    safe_print("診斷結果:")
    safe_print("=" * 60)
    
    if ffmpeg_basic and ffmpeg_audio and whisper_ok:
        safe_print("✅ 所有測試通過，問題可能已解決")
    else:
        safe_print("❌ 發現問題:")
        if not ffmpeg_basic:
            safe_print("   - FFmpeg 基本功能異常")
        if not ffmpeg_audio:
            safe_print("   - FFmpeg 音訊處理異常")
        if not whisper_ok:
            safe_print("   - Whisper 音訊載入失敗 (這是 [WinError 2] 的直接原因)")
        
        # 嘗試修復
        safe_print("\n🔧 嘗試修復...")
        if fix_environment_issues():
            safe_print("✅ 環境修復完成，請重新測試")
            
            # 重新測試 Whisper
            if test_whisper_audio_loading():
                safe_print("🎉 修復成功！")
            else:
                safe_print("❌ 修復後仍有問題")
        
        # 創建測試腳本
        create_test_script()
        
        safe_print("\n💡 建議:")
        safe_print("1. 執行 python test_whisper_env.py 進行進一步測試")
        safe_print("2. 確保 ffmpeg.exe 在程式目錄中")
        safe_print("3. 以管理員身分執行程式")
    
    safe_print("\n按任意鍵退出...")
    input()

if __name__ == "__main__":
    main()