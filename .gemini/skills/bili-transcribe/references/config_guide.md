# 配置与环境指南

## 1. 路径配置 (`src/config.py`)
项目中所有的路径均在 `src/config.py` 中统一管理。

- **TEMP_DIR**: 临时文件存放处（下载的原始视频、提取的音频）。
- **OUTPUT_DIR**: 最终 Markdown 文档和归档视频的存放处。
- **OBSIDIAN_VAULT_PATH**: 默认的 Obsidian 库路径。
- **FFMPEG_PATH**: `ffmpeg` 执行文件路径。

## 2. ASR 引擎参数对比

### Faster-Whisper
- **优点**：多语言支持极佳，准确度高，支持 GPU 加速。
- **推荐模型**：`large-v3`（最准），`medium`（平衡）。
- **优化参数**：
  - `beam_size=5`：确保极致准确。
  - `vad_filter=True`：过滤静音，提高转录效率。

### FunASR
- **优点**：针对中文语音优化，对口音兼容性较好。
- **缺点**：依赖较多，可能存在环境兼容性问题。

## 3. 环境依赖
运行此流程需要以下核心库，**必须在项目根目录的 `venv` 环境中运行**。直接使用系统 `python3` 可能会导致 `ModuleNotFoundError`。

- `yt-dlp`: 视频抓取。
- `faster-whisper`: 核心转录引擎。
- `funasr` & `modelscope`: (可选) FunASR 引擎。
- `ffmpeg`: 必备的媒体处理工具。

## 4. 常见问题
- **ModuleNotFoundError**: 检查是否激活了 `venv` 或使用了 `./venv/bin/python3`。
- **CUDA Error**: 确保安装了对应版本的 NVIDIA 驱动，Whisper 默认尝试在 GPU 上运行。
