# BiliTranscribe

一个基于 Python 的 CLI 工具，用于下载 Bilibili 视频，提取音频，并支持使用 **OpenAI Whisper** (默认) 或 **阿里 FunASR** 生成带时间戳的 Markdown 笔记。

专为知识管理打造，支持一键将笔记导入 **Obsidian**，并生成“点击即跳转”的时间戳链接。

## ✨ 核心特性

- **双引擎转录**: 
  - `whisper`: (默认) 数字/日期格式化完美，排版整洁，适合财经/科技类内容。
  - `funasr`: (阿里达摩院) 中文专有名词（人名、机构名）识别精准，适合国内新闻/访谈。
- **Obsidian 深度集成**: 
  - 生成包含 YAML Frontmatter 的笔记。
  - **时间戳跳转**: 点击笔记中的时间戳 `[05:30]`，浏览器自动跳转到 B 站对应秒数。
  - 自动归档到你的 Obsidian Vault 指定目录。
- **智能去重**: 自动检测已存在的视频和音频，避免重复下载和提取，极大提升重跑效率。
- **自动化工作流**: 封装 `yt-dlp` 下载 -> `ffmpeg` 提取 -> GPU 转录 -> 整理归档全流程。

## 🛠️ 安装

### 1. 基础安装

```bash
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装基础依赖
pip install -r requirements.txt
```

### 2. 进阶引擎支持 (FunASR)

如需使用 FunASR 引擎，需安装 PyTorch 和 ModelScope：

```bash
# 安装 PyTorch (根据你的 CUDA 版本选择，这里以 CUDA 12.1 为例)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装 FunASR
pip install funasr modelscope
```

### 3. NVIDIA 库配置 (解决 libcublas 错误)

如果 Whisper 报错 `Library libcublas.so.12 is not found`：

```bash
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

## 🚀 使用方法

### 快速开始

```bash
export PYTHONPATH=$PYTHONPATH:.
./venv/bin/python src/main.py "https://www.bilibili.com/video/BV1xxxxxx"
```

### 配置文件 (推荐)

在项目根目录创建 `config.json`，设置你的 Obsidian 仓库路径：

```json
{
    "obsidian_vault_path": "/Users/yourname/Documents/ObsidianVault"
}
```

设置后，程序会自动将生成的 Markdown 笔记保存到 Vault 中的 `BiliInbox` 文件夹。

### 命令行参数

```bash
# 指定引擎 (funasr) 并强制保存到特定 Obsidian 路径
./venv/bin/python src/main.py "URL" --engine funasr --obsidian-vault "/path/to/vault"

# 仅下载并保留音频文件 (方便调试)
./venv/bin/python src/main.py "URL" --keep-audio
```

## 常见问题

1.  **`ModuleNotFoundError: No module named 'src'`**:
    *   运行前请执行 `export PYTHONPATH=$PYTHONPATH:.`。
2.  **重复下载？**:
    *   程序会自动检测 `output/` 目录下的视频文件，如果存在则直接复用。
3.  **FunASR 运行慢？**:
    *   目前默认强制使用 CPU 运行 FunASR 以避免 CUDA 兼容性问题。由于其非自回归特性，CPU 速度依然尚可。

## 输出结构
- **Markdown**: 保存到配置的 Obsidian 目录（或 `output/`）。
- **Video**: 始终归档到项目的 `output/` 目录。
