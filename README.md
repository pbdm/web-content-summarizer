# BiliTranscribe (OpenCode Agent Skill)

一个专为 **OpenCode Agent** 打造的自动化工具，用于下载 Bilibili 视频/音频，提取高精度 ASR 文稿，并利用 Agent 的认知能力生成结构化的 Obsidian 知识笔记。

## ✨ 核心特性

- **Agent 驱动的智能总结**:
  - 不仅仅是转录，更通过 LLM (Agent) 将冗长的文稿转化为结构清晰、逻辑严密的知识笔记。
  - 内置专家级 **Global** `bili-transcribe` Skill，自动提取核心观点、实操建议和风险提示。
- **极速 Audio-Only 模式**:
  - 默认仅下载最佳音质的音频流，无需下载巨大的视频文件，带宽占用极低，处理速度飞快。
- **双引擎转录**: 
  - `whisper` (默认): `large-v3` 模型加持，数字/日期格式化完美，适合泛知识类内容。
  - `funasr` (阿里达摩院): 对中文专有名词识别精准，适合特定领域。
- **Obsidian 深度集成**: 
  - **自动归档**: 总结笔记自动保存至 Obsidian 的 `BiliNotes/` 目录。
  - **时间戳跳转**: 笔记保留源视频的时间戳链接，点击即达。
  - **Frontmatter**: 自动生成符合 Obsidian 规范的元数据（Tags, Source, Created）。

## 🛠️ 安装

### 1. 一键环境搭建 (推荐)
适用于 Linux/WSL。脚本会自动创建虚拟环境、安装依赖并配置 FFmpeg。
```bash
chmod +x setup.sh
./setup.sh
```

### 2. 硬件适配
项目会自动检测 CUDA 支持情况并**主动调整默认配置**：
- **GPU (NVIDIA)**: 自动启用 `cuda` 模式 + `float16` 加速。默认模型：**`large-v3`**。
- **CPU**: 自动切换为 `cpu` 模式 + `int8` 量化。默认模型：**`base`**（平衡速度与精度，防止超时）。

如果需要手动强制指定：
```bash
./venv/bin/python3 src/main.py [URL] --model small --device cpu
```

## 🚀 使用方法

### 方式一：通过 OpenCode Agent (推荐)
直接在对话中发送指令：
> “处理 https://www.bilibili.com/video/BV1xxxxxx”

Agent 会自动：
1. 调起脚本下载音频并生成原始文稿。
2. 读取文稿并进行深度总结。
3. 将总结存入你的 Obsidian。

### 方式二：手动 CLI 运行
如果你只想生成原始 ASR 文稿：

```bash
export PYTHONPATH=$PYTHONPATH:.
# 默认 Audio-Only + Whisper large-v3
./venv/bin/python src/main.py "https://www.bilibili.com/video/BV1xxxxxx"
```

## ⚙️ 配置 (config.json)

在项目根目录创建 `config.json` 以启用 Obsidian 自动归档：

```json
{
    "obsidian_vault_path": "/Users/yourname/Documents/ObsidianVault"
}
```

## 📂 输出结构

- **原始文稿**: `output/transcripts/[UP主]-[标题]_[引擎].md` (包含详细时间戳)
- **智能笔记**: `{ObsidianVault}/BiliNotes/[UP主]-[标题].md` (由 Agent 生成的精华)

## 🧠 Skill 架构

本项目已将核心业务逻辑与 Agent 专家能力分离：
- `src/`: 核心 Python 处理引擎 (下载/提取/转录/日志)。
- **Global Skill**: `bili-transcribe` 已作为全局专家技能固化，不再占用项目局部代码空间。
