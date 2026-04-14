import os
import json
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 目录配置
BIN_DIR = PROJECT_ROOT / "bin"
TEMP_DIR = PROJECT_ROOT / "temp"
TRANSCRIPT_DIR = TEMP_DIR / "transcripts"  # 转录文稿存档


# FFmpeg 路径 - 优先使用项目 bin/ 目录，其次使用系统路径
def find_ffmpeg(name):
    if BIN_DIR.exists():
        path = BIN_DIR / name
        if path.exists():
            return path
    import shutil

    system_path = shutil.which(name)
    if system_path:
        return Path(system_path)
    if BIN_DIR.exists():
        return BIN_DIR / name  # 返回 bin/ 路径，让后续检查失败有明确错误
    raise FileNotFoundError(f"{name} not found in bin/ or system PATH")


FFMPEG_PATH = find_ffmpeg("ffmpeg")
FFPROBE_PATH = find_ffmpeg("ffprobe")

# 确保目录存在
TEMP_DIR.mkdir(exist_ok=True)
TRANSCRIPT_DIR.mkdir(exist_ok=True)


# 模型配置
def get_default_device():
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        # 如果没装 torch，尝试通过 faster-whisper 的方式检测 (这里简单 fallback)
        return "cpu"


DEFAULT_DEVICE = get_default_device()
# 根据设备选择最优计算类型和默认模型
DEFAULT_COMPUTE_TYPE = "float16" if DEFAULT_DEVICE == "cuda" else "int8"
DEFAULT_MODEL_SIZE = "large-v3" if DEFAULT_DEVICE == "cuda" else "base"
# 对于 RTX 5070 Ti (16GB)，2 个 worker 是平衡性能与显存的最佳选择
DEFAULT_NUM_WORKERS = 2 if DEFAULT_DEVICE == "cuda" else 4

print(
    f"DEBUG: Hardware detected: {DEFAULT_DEVICE}, using compute_type: {DEFAULT_COMPUTE_TYPE}"
)
