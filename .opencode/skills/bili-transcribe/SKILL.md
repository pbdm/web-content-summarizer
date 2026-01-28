---
name: bili-transcribe
description: 自动下载 Bilibili 视频、提取 ASR 内容（使用 Whisper 或 FunASR）并生成带有时间戳和元数据的 Markdown 文稿。
---

# BiliTranscribe 工作流

本 Skill 封装了从视频 URL 到原始 ASR 文稿（Markdown 格式）的完整处理流程。

## 核心流程

### 1. 视频下载 (Downloader)
使用 `src/downloader.py` 中的 `VideoDownloader` 类。
- **功能**：通过 `yt-dlp` 下载最佳画质视频及音频。
- **输出**：返回本地视频文件路径及上传者（Uploader）信息。
- **优化**：会自动检查 `output/` 目录是否已存在同名文件，避免重复下载。

### 2. 音频提取 (Audio Extraction)
使用 `src/audio.py` 中的 `AudioExtractor` 类。
- **功能**：调用 `ffmpeg` 从视频中提取音频。
- **规格**：强制转换为 16kHz 采样率、单声道、pcm_s16le 编码的 WAV 格式（ASR 最优输入格式）。
- **输出**：`.wav` 音频文件。

### 3. ASR 转录 (Transcription)
根据配置选择引擎：
- **Whisper (默认)**：使用 `src/transcriber.py`。基于 `faster-whisper`，支持 `large-v3` 等模型。
- **FunASR**：使用 `src/transcriber_funasr.py`。适用于特定中文场景。
- **输出**：带有 `start`, `end`, `text` 字段的 Segment 列表。

### 4. 格式化输出 (Formatting)
使用 `src/formatter.py` 中的 `MarkdownFormatter` 类。
- **功能**：生成包含元数据（创建时间、来源 URL、标签）的原始文稿。
- **特性**：自动将秒数转换为 `HH:MM:SS` 格式，并生成指向视频对应时间点的跳转链接。

### 5. 清理与归档 (Finalize)
- 将视频文件移动至 `output/` 目录。
- 删除临时生成的 `.wav` 音频文件（除非指定 `--keep-audio`）。

## 使用指南

### 快速执行
必须使用项目自带的虚拟环境执行，以确保所有依赖正常加载：
```bash
./venv/bin/python3 src/main.py <URL> [OPTIONS]
```

### 关键参数
- `--engine`: 选择 ASR 引擎 (`whisper` 或 `funasr`)。
- `--model`: 指定 Whisper 模型大小（如 `base`, `medium`, `large-v3`）。
- `--fast`: 开启高性能模式（增加 worker 数量）。
- `--obsidian-vault`: 指定 Obsidian 库路径，自动存入 `BiliInbox` 文件夹。

## 注意事项
- 依赖 `ffmpeg` 已安装在系统路径或项目中指定的路径。
- 建议在 `venv` 虚拟环境中运行以保证依赖隔离。