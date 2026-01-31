import os
import json
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 配置文件
CONFIG_FILE = PROJECT_ROOT / "config.json"
OBSIDIAN_VAULT_PATH = None

# 尝试加载配置
if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            OBSIDIAN_VAULT_PATH = config_data.get("obsidian_vault_path")
    except Exception as e:
        print(f"Warning: Failed to load config.json: {e}")

# 目录配置
BIN_DIR = PROJECT_ROOT / "bin"
TEMP_DIR = PROJECT_ROOT / "temp"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOCAL_TRANSCRIPT_DIR = OUTPUT_DIR / "transcripts"  # 本地 ASR 存档

# FFmpeg 路径
FFMPEG_PATH = BIN_DIR / "ffmpeg"
FFPROBE_PATH = BIN_DIR / "ffprobe"

# 确保目录存在
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOCAL_TRANSCRIPT_DIR.mkdir(exist_ok=True)

# 检查 FFmpeg 是否存在
if not FFMPEG_PATH.exists():
    raise FileNotFoundError(f"FFmpeg binary not found at {FFMPEG_PATH}")

# 模型配置
DEFAULT_MODEL_SIZE = "large-v3"
DEFAULT_DEVICE = "cuda"  # 用户有 NVIDIA GPU
DEFAULT_COMPUTE_TYPE = "float16" # 或者 'int8_float16' 
DEFAULT_NUM_WORKERS = 1
