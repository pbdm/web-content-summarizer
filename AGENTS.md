# Web Content Summarizer - Agent 记忆

## 项目概述

这是一个用于从互联网提取内容并生成知识笔记的工具。

## 核心功能

- **B站视频转录**: 使用 Whisper/FunASR 进行 ASR 转录
- **网页文章提取**: 使用 defuddle 或 web_fetch
- **PDF 解析**: 支持 PDF 文档提取

## 输出路径

- B站视频笔记 → `/mnt/c/code/others/content/BiliNotes/`
- 网页/PDF 笔记 → `/mnt/c/code/others/content/WebNotes/`

## 快速开始

```bash
# 初始化 (仅需一次)
chmod +x setup.sh && ./setup.sh

# 转录 B站视频
./venv/bin/python3 src/main.py <URL>

# 或使用简化脚本
./venv/bin/python3 src/transcribe_url.py <URL>
```

## 关键参数

- `--engine`: `whisper` 或 `funasr`
- `--model`: 指定模型大小（如 `base`, `large-v3`）
- `--fast`: 开启高性能模式

## 硬件自适应

系统自动检测 GPU/CPU 并选择最优配置：
- **GPU**: 使用 `large-v3` + `float16`
- **CPU**: 自动回退到 `base` + `int8`

详见 `docs/config_guide.md`

## 目录结构

```
WebContentSummarizer/
├── SKILL.md        ← Skill 定义
├── PROMPT.md       ← 总结模板
├── AGENTS.md       ← 本文件
├── docs/           ← 文档
│   └── config_guide.md
├── src/            ← 源代码
├── temp/           ← 临时文件
└── venv/           ← 虚拟环境
```

## 相关文件

- `SKILL.md` - Skill 定义（加载时使用）
- `PROMPT.md` - 总结模板
- `docs/config_guide.md` - 配置指南