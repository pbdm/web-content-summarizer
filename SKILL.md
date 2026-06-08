---
name: web-content-summarizer
description: 自动提取互联网内容（B站视频、网页文章、PDF）并生成带时间戳和元数据的 Markdown 知识笔记。
---

# Web Content Summarizer

将任意 URL 转化为结构化知识笔记。

## 核心模板

> **所有内容类型的笔记生成都必须严格遵循 `PROMPT.md` 模板。**
>
> - **路径**：项目根目录下的 `PROMPT.md`
> - **作用**：定义输出格式、frontmatter 结构、内容组织规范
> - **调用时机**：在生成任何笔记前，必须先读取此文件

## 支持内容

| URL 类型 | 处理方式 |
|----------|----------|
| bilibili.com/* | B站视频 → ASR 转录 + 总结 |
| *.pdf | PDF 解析 + 总结 |
| 其他网页 | defuddle/web_fetch + 总结 |

## 输出路径

- 所有内容（B站视频/网页/PDF）默认输出至 → 项目根目录下的 `output/`
- 如需自定义输出目录，可修改项目根目录下的 `paths.json`
- 每个生成的 Markdown 文件都必须在前言 (`---`) 的 `tags` 中包含 `- WebNotes`

## 使用方式

```bash
# Linux / macOS
./venv/bin/python src/main.py <B站URL>

# Windows PowerShell
.\venv\Scripts\python.exe .\src\main.py <B站URL>

# 简化脚本
./venv/bin/python src/transcribe_url.py <URL>
# 或
.\venv\Scripts\python.exe .\src\transcribe_url.py <URL>
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--engine` | 转录引擎 (whisper/funasr) | whisper |
| `--model` | Whisper 模型大小 | large-v3 (GPU) / base (CPU) |
| `--fast` | 启用高性能模式 | - |
| `--device` | 运行设备 | cuda/cpu 自动检测 |
| `--keep-audio` | 保留中间音频文件 | - |

## 核心模块

| 模块 | 功能 |
|------|------|
| `downloader.py` | 视频/音频下载（含 API fallback） |
| `audio.py` | 音频提取（16kHz WAV） |
| `subtitles.py` | B站字幕获取 |
| `transcriber.py` | Whisper 转录 |
| `formatter.py` | Markdown 格式化 |

## 处理流程

### B站视频
1. 下载音频 → 2. 提取 16k WAV → 3. Whisper 转录 → 4. 读取 `PROMPT.md` → 5. 生成笔记

### 网页文章
1. defuddle 提取 → 2. 失败则 web_fetch 回退 → 3. 读取 `PROMPT.md` → 4. 生成笔记

### PDF
1. web_fetch PDF 解析 → 2. 读取 `PROMPT.md` → 3. 生成笔记
