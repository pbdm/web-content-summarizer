---
name: bili-transcribe
description: 自动下载 Bilibili 视频、提取 ASR 内容（使用 Whisper 或 FunASR）并生成带有时间戳和元数据的 Markdown 文稿。
---

# BiliTranscribe 工作流

本 Skill 封装了从视频 URL 到原始 ASR 文稿（Markdown 格式）的完整处理流程。

## 核心流程

### 1. 媒体下载 (Downloader)
使用 `src/downloader.py` 中的 `VideoDownloader` 类。
- **功能**：通过 `yt-dlp` 下载资源。默认启用 **Audio-Only** 模式（仅下载最佳音质），极大节省带宽和时间。
- **输出**：下载到临时目录，并自动转换为 16k wav 用于转录。

### 2. 音频提取 (Audio Extraction)
使用 `src/audio.py` 中的 `AudioExtractor` 类。
- **功能**：调用 `ffmpeg` 将下载的媒体文件标准化为 Whisper 友好的格式。
- **规格**：强制转换为 16kHz 采样率、单声道、pcm_s16le 编码的 WAV 格式。

### 3. ASR 转录 (Transcription)
根据配置选择引擎：
- **Whisper (默认)**：使用 `src/transcriber.py`。基于 `faster-whisper`，支持 `large-v3` 等模型。
- **FunASR**：使用 `src/transcriber_funasr.py`。适用于特定中文场景。
- **输出**：带有 `start`, `end`, `text` 字段的 Segment 列表。

### 4. 格式化输出 (Formatting)
使用 `src/formatter.py` 中的 `MarkdownFormatter` 类。
- **功能**：生成包含元数据（创建时间、来源 URL、标签）的原始文稿。
- **输出**：保存到本地 `output/transcripts/` 目录。
- **特性**：自动将秒数转换为 `HH:MM:SS` 格式，并生成指向视频对应时间点的跳转链接。

### 5. 智能总结 (Agentic Summarization)
- **强制校验**：Agent 必须先从原始文稿读取 `author` 字段，并在生成文件名和总结前明确向用户报告校验后的 UP 主名称。
- **命名规范**：生成的文件必须严格遵守 `[UP主名称]-[原文件名].md` 格式。严禁凭借上下文惯性或记忆来命名。
- **机制**：脚本执行完毕后，Agent 会自动读取生成的原始文稿。
- **处理**：Agent 使用自身的 LLM 能力，根据 `.opencode/skills/bili-transcribe/PROMPT.md` 模板生成结构化笔记。
- **输出**：总结文件将保存至 Obsidian 的 `BiliNotes/` 目录。

### 6. 资源清理 (Cleanup)
- **临时文件**：转录完成后，自动删除下载的源音频/视频文件及转换后的 `.wav` 文件（除非指定 `--keep-audio`）。
- **产物保留**：仅保留最终的 Markdown 原始文稿在 `output/transcripts/`。

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
- `--obsidian-vault`: 指定 Obsidian 库路径（用于定位 BiliNotes 输出位置）。

## 注意事项
- 依赖 `ffmpeg` 已安装在系统路径或项目中指定的路径。
- 建议在 `venv` 虚拟环境中运行以保证依赖隔离。