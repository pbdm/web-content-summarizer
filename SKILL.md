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

## 网页文章处理流程

使用分层提取策略，确保高成功率：

### 1. 复杂性梯度提取 (Layered Extraction)

- **Step 1 (快速)**: 调用 `defuddle parse <URL> --md`
- **Step 2 (自愈)**: 若 Step 1 失败或结果过短，自动回退至 `web_fetch` 进行全量抓取
- **Step 3 (PDF)**: 检测到 PDF 后，优先尝试 `web_fetch` 的 PDF 解析模式；若失效，引导用户提供本地路径

### 2. 强制自检与元数据声明

- **元数据校验**: Agent 必须在内存中构建元数据字典：`{title, author, date}`
- **缺失处理**: 若无法通过原文判定日期，统一格式化为 `YYYY-MM-DD (Estimated)`
- **显式声明**: Agent **必须**在回复开头声明校验结果："经实时元数据校验，[标题] 来源于 [机构/作者]"

### 3. 智能总结

- **触发机制**: 成功提取内容后，Agent 必须启动总结流程
- **创作指令**: 严格遵循项目根目录 `PROMPT.md` 模版和提取原则
- **校验规范**: 落盘前**必须**从原文读取 `author` 字段
- **输出目标**:
  - **路径**: `/mnt/c/code/others/content/WebNotes/`
  - **命名规范**: `[作者/机构]-[文章标题].md`
- **强制落盘**: Agent 在回复中展示总结的同时，**必须**同步执行 `write_file` 物理保存

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

使用 `src/formatter.py` 生成包含元数据（来源 URL、UP 主、日期）的原始文稿，保存到本地 `temp/transcripts/`。

### 5. 智能总结 (Agentic Summarization)

- **触发机制**：脚本输出 `🚀 [ACTION REQUIRED]` 提示后，Agent 必须启动总结流程。
- **创作指令**：严格遵循项目根目录 `PROMPT.md` 模版和提取原则。
- **校验规范**：落盘前**必须**从原始文稿读取 `author` 字段，并在回复中显式向用户声明校验后的 UP 主名称。
- **输出目标**:
  - **路径**: `/mnt/c/code/others/content/BiliNotes/`
  - **命名规范**: `[UP主名称]-[原文件名].md`
- **强制落盘**：Agent 在回复中展示总结的同时，**必须**同步执行 `write_file` 物理保存。

### 6. 资源清理 (Cleanup)

- 转录完成后，自动删除临时音频文件。仅保留 `temp/transcripts/` 下的 Markdown 原始文稿。
