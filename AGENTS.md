# Web Content Summarizer - Agent 记忆

## 项目概述

从互联网提取内容（B站视频、网页文章、PDF）并生成知识笔记。

## 核心功能

- **B站视频转录**: Whisper/FunASR ASR 转录 + Bilibili API fallback
- **网页文章提取**: defuddle → web_fetch 回退
- **PDF 解析**: web_fetch PDF 模式

## 输出路径

- B站视频笔记 → `/mnt/c/code/others/content/BiliNotes/`
- 网页/PDF 笔记 → `/mnt/c/code/others/content/WebNotes/`

## 快速开始

```bash
# B站视频转录
./venv/bin/python3 src/transcribe_url.py <B站URL>

# 网页/PDF 总结
# 使用 defuddle 或 web_fetch 提取内容后按 PROMPT.md 模板生成笔记
```

## 关键参数

- `--engine`: whisper / funasr
- `--model`: base, large-v3 等
- `--fast`: 高性能模式

## 硬件自适应

- **GPU**: large-v3 + float16
- **CPU**: base + int8

## 目录结构

```
web-content-summarizer/
├── SKILL.md        ← Skill 定义
├── PROMPT.md       ← 总结模板
├── AGENTS.md       ← 本文件
├── src/            ← 源代码
│   ├── main.py
│   ├── transcribe_url.py
│   ├── downloader.py
│   ├── audio.py
│   ├── subtitles.py
│   └── transcriber.py
├── temp/           ← 临时文件
└── venv/           ← 虚拟环境
```
