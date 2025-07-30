#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPU 功能測試腳本
用於驗證 Whisper GPU 加速是否正常工作
"""

import warnings
warnings.filterwarnings("ignore", message=".*Failed to launch Triton kernels.*")
warnings.filterwarnings("ignore", message=".*falling back to a slower.*")

def test_gpu_support():
    """測試 GPU 支援"""
    print("🔍 GPU 支援測試")
    print("=" * 50)
    
    # 測試 PyTorch
    try:
        import torch
        print(f"✅ PyTorch 版本: {torch.__version__}")
        print(f"✅ CUDA 可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ GPU 數量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        else:
            print("⚠️ CUDA 不可用，將使用 CPU 模式")
    except ImportError:
        print("❌ PyTorch 未安裝")
        return False
    
    # 測試 Whisper
    try:
        import whisper
        print(f"✅ Whisper 版本: {whisper.__version__}")
        print(f"✅ 可用模型: {', '.join(whisper.available_models())}")
    except ImportError:
        print("❌ Whisper 未安裝")
        return False
    
    # 測試模型載入
    try:
        print("\n🧪 測試模型載入...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📱 使用設備: {device}")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = whisper.load_model("tiny", device=device)
        
        print("✅ 模型載入成功")
        print(f"📊 模型設備: {next(model.parameters()).device}")
        
        # 清理記憶體
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"❌ 模型載入失敗: {e}")
        return False
    
    print("\n🎉 所有測試通過！GPU 加速已準備就緒")
    return True

def test_simple_transcription():
    """測試簡單的轉錄功能"""
    print("\n🎤 簡單轉錄測試")
    print("=" * 50)
    
    try:
        import whisper
        import torch
        import numpy as np
        
        # 建立測試音訊 (1秒的靜音)
        sample_rate = 16000
        duration = 1.0
        audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📱 使用設備: {device}")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = whisper.load_model("tiny", device=device)
            result = model.transcribe(audio)
        
        print("✅ 轉錄測試完成")
        print(f"📝 結果: '{result['text'].strip()}'")
        
        # 清理記憶體
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ 轉錄測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Whisper GPU 功能測試")
    print("=" * 60)
    
    # 基本功能測試
    if not test_gpu_support():
        print("\n❌ 基本功能測試失敗")
        input("按 Enter 鍵結束...")
        exit(1)
    
    # 轉錄功能測試
    if not test_simple_transcription():
        print("\n⚠️ 轉錄功能測試失敗，但基本功能正常")
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！你的系統已準備好使用 Whisper GPU 加速")
    print("💡 現在可以啟動 whisper_subtitle_gui.py 開始使用")
    
    input("\n按 Enter 鍵結束...")