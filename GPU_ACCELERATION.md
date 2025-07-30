# 🚀 GPU 加速指南

## 🎯 為什麼需要 GPU 加速？

CPU 處理 Whisper 可能需要幾分鐘到幾十分鐘，而 GPU 可以將處理時間縮短到幾秒到幾分鐘！

## 🔧 內建 GPU 支援

### 1. 使用程式內建的 GPU 加速
- ✅ 勾選「使用 GPU 加速」
- ✅ 設備選擇「auto」讓程式自動偵測
- ✅ 點擊「檢查 GPU」確認 CUDA 可用性

### 2. 系統需求
- **NVIDIA GPU** - 支援 CUDA
- **PyTorch** - 自動安裝 CUDA 版本
- **足夠的 GPU 記憶體** - 至少 2GB

## ⚡ 高性能替代方案：Const-me/Whisper

如果你需要極致的性能，可以使用 [Const-me/Whisper](https://github.com/Const-me/Whisper)：

### 🌟 優勢
- **極快速度** - 比官方版本快 5-10 倍
- **低記憶體使用** - 優化的 GPU 記憶體管理
- **DirectML 支援** - 支援 AMD GPU 和 Intel GPU
- **Windows 優化** - 專為 Windows 系統優化

### 📥 安裝步驟

1. **下載 Const-me/Whisper**
```bash
# 從 GitHub Releases 下載最新版本
https://github.com/Const-me/Whisper/releases
```

2. **解壓到資料夾**
```
C:\whisper-gpu\
├── main.exe
├── whisper.dll
└── models\
```

3. **下載模型**
```bash
# 下載你需要的模型到 models 資料夾
# 例如：ggml-medium.bin
```

4. **整合到 AIsub**
- 將 `main.exe` 路徑加入系統 PATH
- 或修改 AIsub 程式碼指向 `main.exe`

### 🔧 整合方法

#### 方法 1: 修改 PATH
```bash
# 將 C:\whisper-gpu 加入系統 PATH
# 然後重新啟動 AIsub
```

#### 方法 2: 直接整合
將 `main.exe` 複製到 AIsub 資料夾，程式會自動偵測並使用。

### 📊 性能對比

| 方案 | CPU (i7) | GPU (RTX 3060) | Const-me GPU |
|------|----------|----------------|---------------|
| 5分鐘影片 | ~15分鐘 | ~2分鐘 | ~30秒 |
| 記憶體使用 | 2GB | 3GB | 1.5GB |
| 支援 GPU | ❌ | NVIDIA 只 | NVIDIA/AMD/Intel |

## 🛠️ 故障排除

### GPU 不被偵測
1. **檢查 CUDA 安裝**
```bash
nvidia-smi
```

2. **檢查 PyTorch CUDA**
```python
import torch
print(torch.cuda.is_available())
```

3. **重新安裝 PyTorch**
```bash
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 記憶體不足
- 使用較小的模型 (medium → small → base)
- 關閉其他 GPU 程式
- 增加虛擬記憶體

### AMD/Intel GPU
- 使用 Const-me/Whisper 的 DirectML 版本
- 或使用 CPU 模式

## 💡 建議設定

### 🎮 遊戲級 GPU (RTX 3060+)
- 模型：large
- 設備：cuda
- 預期速度：非常快

### 💻 入門級 GPU (GTX 1660+)
- 模型：medium
- 設備：cuda
- 預期速度：快

### 🖥️ 無獨立 GPU
- 模型：small/base
- 設備：cpu
- 考慮使用 Const-me/Whisper DirectML

## 🔗 相關連結

- [Const-me/Whisper GitHub](https://github.com/Const-me/Whisper)
- [CUDA 安裝指南](https://developer.nvidia.com/cuda-downloads)
- [PyTorch GPU 版本](https://pytorch.org/get-started/locally/)
- [DirectML 支援](https://github.com/microsoft/DirectML)