---
name: web-content-summarizer
description: 自动提取互联网内容（B站视频、网页文章、PDF）并生成带有时间戳和元数据的 Markdown 知识笔记。
---

# Web Content Summarizer

本 Skill 封装了从任意 URL 到结构化知识笔记的完整处理流程。支持：

- Bilibili 视频 ASR 转录
- 网页文章提取
- PDF 文档解析

## 内容类型检测

| URL 类型 | 处理方式 |
| :--- | :--- |
| bilibili.com/* | B站视频 → ASR 转录 + 总结 |
| *.pdf | PDF 解析 + 总结 |
| 其他网页 | defuddle/web_fetch + 总结 |

## 输出路径

- B站视频笔记 → `/mnt/c/code/others/content/BiliNotes/`
- 网页/PDF 笔记 → `/mnt/c/code/others/content/WebNotes/`

## B站视频处理流程

本 Skill 封装了从视频 URL 到原始 ASR 文稿（Markdown 格式）的完整处理流程。

### 1. 媒体下载 (Downloader)

使用 `src/downloader.py` 中的 `VideoDownloader` 类。

- **功能**：通过 `yt-dlp` 下载资源。默认启用 **Audio-Only** 模式（仅下载最佳音质）。
- **输出**：下载到临时目录，并自动转换为 16k wav 用于转录。

### 2. 音频提取 (Audio Extraction)

使用 `src/audio.py` 中的 `AudioExtractor` 类。

- **功能**：调用 `ffmpeg` 将下载的媒体文件标准化为 16kHz、单声道、WAV 格式。

### 3. ASR 转录 (Transcription)

根据配置选择引擎（优先使用 GPU 加速）：

- **Whisper (默认)**：基于 `faster-whisper`，支持 `large-v3` 等模型。
- **FunASR**：适用于特定中文场景。
- **输出**：带有时间戳的 Segment 列表。

### 4. 格式化输出 (Formatting)

使用 `src/formatter.py` 生成包含元数据（来源 URL、UP 主、日期）的原始文稿，保存到本地 `output/transcripts/`。

### 5. 智能总结 (Agentic Summarization)

- **触发机制**：脚本输出 `🚀 [ACTION REQUIRED]` 提示后，Agent 必须启动总结流程。
- **创作指令**：严格遵循项目根目录 `PROMPT.md` 模版和提取原则。
- **校验规范**：落盘前**必须**从原始文稿读取 `author` 字段，并在回复中显式向用户声明校验后的 UP 主名称。
- **强制落盘**：Agent 在回复中展示总结的同时，**必须**同步执行 `write_file` 物理保存。

### 6. 资源清理 (Cleanup)

- 转录完成后，自动删除临时音频文件。仅保留 `output/transcripts/` 下的 Markdown 原始文稿。

## 使用指南

### 快速执行

```bash
./venv/bin/python3 src/main.py <URL> --model large-v3 --device cuda --compute-type float16
```

或使用简化脚本：

```bash
./venv/bin/python3 src/transcribe_url.py <URL>
```

### 关键参数

- `--engine`: `whisper` 或 `funasr`。
- `--model`: 指定模型大小（如 `base`, `large-v3`）。
- `--fast`: 开启高性能模式（增加 worker 数量）。

### 硬件自适应

系统自动检测 GPU/CPU 并选择最优配置：
- **GPU**: 使用 `large-v3` + `float16`
- **CPU**: 自动回退到 `base` + `int8`

详见 `docs/config_guide.md`。

## 项目结构

```
WebContentSummarizer/               ← Skill 根目录
├── SKILL.md                      ← 本文件 (也是 AGENTS.md 的软链接)
├── PROMPT.md                     ← 统一的内容总结 Prompt
├── docs/                        ← 文档
│   ├── ASR_BENCHMARK.md        # Whisper vs FunASR 性能对比
│   └── config_guide.md         # 配置与环境指南（含 ASR 策略）
├── src/                         ← 源代码 (入口 + 核心模块)
├── output/
│   └── transcripts/             # 原始转录文稿
├── venv/                       # Python 虚拟环境
├── requirements.txt
└── setup.sh
```
