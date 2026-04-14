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

## 3. 智能降级与环境自适应

系统内置自动化回退机制，确保在任何硬件环境下都能成功完成任务。

### 硬件自适应

| 硬件环境 | 默认模型 | 默认计算类型 | 默认并行数 |
| :--- | :--- | :--- | :--- |
| **GPU (CUDA)** | `large-v3` | `float16` | 1 |
| **CPU** | `base` | `int8` | 4 |

- **GPU 优先**：若环境支持 CUDA，默认使用 GPU 加速。
- **CPU 回退**：若 CUDA 加载失败，系统自动切换到 CPU 模式。

### 模型降级链

`large-v3` → `medium` → `small` → `base` → `tiny`

若模型加载失败，系统会自动尝试更小的模型。

## 4. 环境依赖

运行此流程需要以下核心库，**必须在项目根目录的 `venv` 环境中运行**。

- `yt-dlp`: 视频抓取
- `faster-whisper`: 核心转录引擎
- `funasr` & `modelscope`: (可选) FunASR 引擎
- `ffmpeg`: 必备的媒体处理工具

## 5. 常见问题

- **ModuleNotFoundError**: 检查是否使用了 `./venv/bin/python3`
- **CUDA Error**: 确保安装了对应版本的 NVIDIA 驱动

## 6. 环境自愈 (`setup.sh`)

- **Pip 缺失修复**：自动识别并安装被剥离的 `pip` 模块
- **FFmpeg 自动化**：通过 Python 生态自动部署静态 FFmpeg 二进制文件