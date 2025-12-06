# CUDA Setup Guide for NVIDIA GPU

Enable GPU acceleration for Whisper speech recognition.

## Requirements

- NVIDIA GPU (GTX 1060+ recommended)
- NVIDIA Driver 450.80.02+
- Windows 10/11

## Quick Setup

### 1. Check Your GPU

```powershell
nvidia-smi
```

If this works, drivers are installed.

### 2. Install CUDA Toolkit

Download from: https://developer.nvidia.com/cuda-downloads

**Recommended**: CUDA 11.8 or 12.1

### 3. Install PyTorch with CUDA

```bash
# Uninstall CPU-only PyTorch first
pip uninstall torch torchvision torchaudio

# Install CUDA version (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# OR for CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 4. Verify CUDA Works

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `CUDA not available` | Reinstall PyTorch with CUDA |
| `nvidia-smi` not found | Install NVIDIA drivers |
| Out of memory | Use smaller Whisper model (`tiny`/`base`) |

## Performance Comparison

| Model | CPU Time | GPU Time | Speedup |
|-------|----------|----------|---------|
| tiny | ~2s | ~0.3s | 6x |
| base | ~5s | ~0.5s | 10x |
| small | ~12s | ~1s | 12x |
| medium | ~30s | ~2s | 15x |

## Atom AI GPU Check

The voice assistant auto-detects GPU:
```
INFO - Loading Whisper small on CUDA  # GPU enabled
INFO - Loading Whisper small on CPU   # CPU fallback
```
