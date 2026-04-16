import json
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 加载路径配置
PATHS_FILE = PROJECT_ROOT / "paths.json"
if PATHS_FILE.exists():
    with open(PATHS_FILE) as f:
        PATHS = json.load(f)
else:
    PATHS = {}

# 目录配置 - 从 paths.json 读取，默认为项目目录
TMP_REL = PATHS.get("TEMP_DIR", "temp")
OUTPUT_REL = PATHS.get("OUTPUT_DIR", "output")

BIN_DIR = PROJECT_ROOT / "bin"
TEMP_DIR = PROJECT_ROOT / TMP_REL
OUTPUT_DIR = (
    PROJECT_ROOT / OUTPUT_REL
    if Path(OUTPUT_REL).is_absolute()
    else PROJECT_ROOT / OUTPUT_REL
)
TRANSCRIPT_DIR = TEMP_DIR / "transcripts"  # 转录文稿存档（临时）


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
try:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"WARNING: Cannot create OUTPUT_DIR: {e}")


# 模型配置
def get_default_device():
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


DEFAULT_DEVICE = get_default_device()
DEFAULT_COMPUTE_TYPE = "float16" if DEFAULT_DEVICE == "cuda" else "int8"
DEFAULT_MODEL_SIZE = "large-v3" if DEFAULT_DEVICE == "cuda" else "base"
DEFAULT_NUM_WORKERS = 2 if DEFAULT_DEVICE == "cuda" else 4

print(
    f"DEBUG: Hardware detected: {DEFAULT_DEVICE}, using compute_type: {DEFAULT_COMPUTE_TYPE}"
)
