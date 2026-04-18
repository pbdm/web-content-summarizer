---
name: web-content-summarizer
description: 自动提取互联网内容（B站视频、网页文章、PDF）并生成带时间戳和元数据的 Markdown 知识笔记。
---

# Web Content Summarizer

将任意 URL 转化为结构化知识笔记。

## 支持内容

| URL 类型 | 处理方式 |
|----------|----------|
| bilibili.com/* | B站视频 → ASR 转录 + 总结 |
| *.pdf | PDF 解析 + 总结 |
| 其他网页 | defuddle/web_fetch + 总结 |

## 输出路径

- 所有内容（B站视频/网页/PDF）统一输出至 → `/mnt/c/code/others/content/WebNotes/`

## 使用方式

```bash
# 转录 B站视频
./venv/bin/python3 src/main.py <B站URL>

# 或使用简化脚本
./venv/bin/python3 src/transcribe_url.py <URL>
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

1. **下载音频** → 2. **提取 16k WAV** → 3. **Whisper 转录** → 4. **生成笔记（严格按照当前目录下的 `PROMPT.md` 模板生成最终 Markdown 文件）**

### 网页文章

1. **defuddle 提取** → 2. **失败则 web_fetch 回退** → 3. **生成笔记（严格按照当前目录下的 `PROMPT.md` 模板生成最终 Markdown 文件）**

### PDF

1. **web_fetch PDF 解析** → 2. **生成笔记（严格按照当前目录下的 `PROMPT.md` 模板生成最终 Markdown 文件）**
