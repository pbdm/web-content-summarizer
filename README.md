# BiliTranscribe

一个基于 Python 的 CLI 工具，用于下载 Bilibili 视频，提取音频，并支持使用 **OpenAI Whisper** (默认) 或 **阿里 FunASR** 生成带时间戳的 Markdown 笔记。

## 功能特性
- **双引擎支持**: 
  - `whisper`: (默认) 擅长数字、日期格式化，排版整洁，适合财经/科技类视频。
  - `funasr`: (阿里达摩院) 对中文专有名词（人名、地名、机构名）识别更精准。
- **自动下载**: 封装 `yt-dlp` 下载 Bilibili 视频。
- **本地 FFmpeg**: 项目内置静态 FFmpeg 二进制文件，无需系统安装。
- **GPU 加速**: 默认使用 CUDA 加速转录（需 NVIDIA 显卡）。
- **Markdown 输出**: 生成包含精确时间戳的笔记文件，支持双引擎结果文件名区分。

## 安装

### 1. 基础安装 (Whisper)

```bash
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装基础依赖
pip install -r requirements.txt
```

### 2. 进阶安装 (FunASR 支持)

如果你想使用 FunASR 引擎，需要安装额外的深度学习库：

```bash
# 安装 PyTorch (根据你的 CUDA 版本选择，这里以 CUDA 12.1 为例)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装 FunASR 和 ModelScope
pip install funasr modelscope
```

### 3. NVIDIA 库配置 (解决 libcublas 错误)

如果运行 Whisper 时遇到 `Library libcublas.so.12 is not found`，请执行：

```bash
# 安装 NVIDIA 官方运行时库
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

运行程序前，你需要设置 `LD_LIBRARY_PATH` 环境变量（详见下文“运行”部分）。

## 使用方法

**基本用法 (使用 Whisper)**:
```bash
# 推荐使用提供的运行脚本(见 gemini.md)或手动设置环境变量
export PYTHONPATH=$PYTHONPATH:.
./venv/bin/python src/main.py "https://www.bilibili.com/video/BV1xxxxxx"
```

**切换引擎**:
```bash
# 使用 FunASR (目前强制使用 CPU 模式以兼容更多环境)
./venv/bin/python src/main.py "https://www.bilibili.com/video/BV1xxxxxx" --engine funasr
```

**可选参数**:
- `--engine`: 选择转录引擎，可选 `whisper` (默认) 或 `funasr`。
- `--model`: 指定 Whisper 模型大小 (默认: `large-v3`, 可选: `medium`, `small` 等)。
- `--keep-audio`: 保留中间生成的 `.wav` 音频文件。

## 常见问题 (Troubleshooting)

1.  **`ModuleNotFoundError: No module named 'src'`**:
    *   原因：Python 找不到项目根目录。
    *   解决：运行命令前添加 `export PYTHONPATH=$PYTHONPATH:.`。

2.  **`Library libcublas.so.12 is not found`**:
    *   原因：系统缺少 CUDA 库或 Python 找不到 pip 安装的 NVIDIA 库。
    *   解决：确保安装了 `nvidia-cublas-cu12`，并在运行命令前正确设置 `LD_LIBRARY_PATH`（参考 `gemini.md` 中的启动命令）。

3.  **FunASR `CUDA error: no kernel image`**:
    *   原因：PyTorch 版本与显卡算力不匹配。
    *   解决：目前代码已默认将 FunASR 降级为 CPU 运行，虽然速度稍慢但能保证兼容性。

## 输出
结果将保存在 `output/` 目录下，文件名包含引擎后缀：
- `output/视频标题_whisper.md`
- `output/视频标题_funasr.md`