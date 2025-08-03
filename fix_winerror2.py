#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修復 [WinError 2] 問題的腳本
"""

import os
import sys
import subprocess
import shutil

def check_python_path():
    """檢查 Python 路徑"""
    print("🔍 檢查 Python 環境...")
    print(f"   Python 可執行檔: {sys.executable}")
    print(f"   Python 版本: {sys.version}")
    print(f"   Python 路徑: {sys.path[:3]}...")  # 只顯示前3個路徑
    
    # 檢查是否在 PATH 中
    python_in_path = shutil.which('python')
    if python_in_path:
        print(f"   PATH 中的 Python: {python_in_path}")
    else:
        print("   ⚠️ Python 不在 PATH 中")
    
    return True

def check_whisper_installation():
    """檢查 Whisper 安裝"""
    print("\n🔍 檢查 Whisper 安裝...")
    try:
        import whisper
        print(f"   ✅ Whisper 模組: {whisper.__file__}")
        print(f"   ✅ Whisper 版本: {getattr(whisper, '__version__', '未知')}")
        
        # 測試模型載入
        model = whisper.load_model("tiny", device="cpu")
        print("   ✅ 模型載入測試通過")
        return True
    except Exception as e:
        print(f"   ❌ Whisper 問題: {e}")
        return False

def check_file_permissions():
    """檢查檔案權限"""
    print("\n🔍 檢查檔案權限...")
    current_dir = os.getcwd()
    print(f"   工作目錄: {current_dir}")
    
    # 檢查讀取權限
    if os.access(current_dir, os.R_OK):
        print("   ✅ 目錄可讀")
    else:
        print("   ❌ 目錄不可讀")
        return False
    
    # 檢查寫入權限
    if os.access(current_dir, os.W_OK):
        print("   ✅ 目錄可寫")
    else:
        print("   ❌ 目錄不可寫")
        return False
    
    # 測試創建檔案
    test_file = "test_permissions.tmp"
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("   ✅ 檔案創建測試通過")
        return True
    except Exception as e:
        print(f"   ❌ 檔案創建失敗: {e}")
        return False

def fix_encoding_issues():
    """修復編碼問題"""
    print("\n🔧 設定編碼環境...")
    
    # 設定環境變數
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Windows 特定設定
    if sys.platform.startswith('win'):
        try:
            # 設定控制台編碼
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
            print("   ✅ 控制台編碼設定為 UTF-8")
        except:
            print("   ⚠️ 無法設定控制台編碼")
    
    print("   ✅ Python 編碼環境已設定")
    return True

def fix_environment_variables():
    """修復環境變數"""
    print("\n🔧 檢查和修復環境變數...")
    
    # 檢查 WHISPER_CACHE_DIR
    cache_dir = os.environ.get('WHISPER_CACHE_DIR')
    if cache_dir:
        print(f"   WHISPER_CACHE_DIR: {cache_dir}")
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir, exist_ok=True)
                print(f"   ✅ 創建緩存目錄: {cache_dir}")
            except Exception as e:
                print(f"   ❌ 創建緩存目錄失敗: {e}")
                return False
    else:
        print("   ℹ️ 未設定 WHISPER_CACHE_DIR，使用預設位置")
    
    # 確保預設緩存目錄存在
    default_cache = os.path.expanduser("~/.cache/whisper")
    if not os.path.exists(default_cache):
        try:
            os.makedirs(default_cache, exist_ok=True)
            print(f"   ✅ 創建預設緩存目錄: {default_cache}")
        except Exception as e:
            print(f"   ❌ 創建預設緩存目錄失敗: {e}")
    
    return True

def reinstall_whisper():
    """重新安裝 Whisper"""
    print("\n🔧 嘗試重新安裝 Whisper...")
    
    try:
        # 升級 pip
        print("   📦 升級 pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # 重新安裝 Whisper
        print("   📦 重新安裝 OpenAI Whisper...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'openai-whisper'], 
                      check=True, capture_output=True)
        
        # 重新安裝 PyTorch
        print("   📦 重新安裝 PyTorch...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'torch', 'torchvision', 'torchaudio'], 
                      check=True, capture_output=True)
        
        print("   ✅ 重新安裝完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 重新安裝失敗: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 其他錯誤: {e}")
        return False

def main():
    """主修復程序"""
    print("=" * 60)
    print("🔧 Whisper [WinError 2] 問題診斷和修復工具")
    print("=" * 60)
    
    checks = [
        ("Python 環境檢查", check_python_path),
        ("Whisper 安裝檢查", check_whisper_installation), 
        ("檔案權限檢查", check_file_permissions),
        ("編碼環境修復", fix_encoding_issues),
        ("環境變數修復", fix_environment_variables),
    ]
    
    results = []
    for name, func in checks:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} 失敗: {e}")
            results.append((name, False))
    
    # 檢查結果
    failed_checks = [name for name, result in results if not result]
    
    if failed_checks:
        print(f"\n⚠️ 發現問題: {', '.join(failed_checks)}")
        
        # 如果 Whisper 有問題，嘗試重新安裝
        if "Whisper 安裝檢查" in failed_checks:
            response = input("\n是否要嘗試重新安裝 Whisper? (y/n): ")
            if response.lower() == 'y':
                if reinstall_whisper():
                    print("✅ 重新安裝完成，請重新啟動程式")
                else:
                    print("❌ 重新安裝失敗")
    else:
        print("\n🎉 所有檢查都通過！")
        print("如果問題仍然存在，可能是以下原因:")
        print("1. 防毒軟體阻擋")
        print("2. Windows Defender 實時保護")
        print("3. 檔案路徑包含特殊字符")
        print("4. 記憶體不足")
        print("5. 磁碟空間不足")
    
    print("\n💡 建議:")
    print("1. 重新啟動程式")
    print("2. 嘗試使用不同的檔案路徑")
    print("3. 暫時停用防毒軟體")
    print("4. 以系統管理員身分執行")

if __name__ == "__main__":
    main()
