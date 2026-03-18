# BiliTranscribe (Zero Config Agent Skill)

一个专为 **OpenCode Agent** 打造的 **Zero Config** 自动化工具。用于下载 Bilibili 视频/音频，提取高精度 ASR 文稿，并利用 Agent 的认知能力生成结构化的 Obsidian 知识笔记。

## 🚀 启动命令 (One-Liner)

复制以下命令在项目根目录下运行。它会自动配置虚拟环境、安装依赖并适配硬件。

```bash
# 一键初始化 (仅需运行一次)
chmod +x setup.sh && ./setup.sh

# 运行转录 (自动适配 GPU/CPU)
export PYTHONPATH=$PYTHONPATH:.
./venv/bin/python3 src/main.py "YOUR_BILI_URL_HERE"
```

## ✨ 核心特性

- **Zero Config (无感配置)**: 
  - 自动检测 GPU/CPU 硬件并优化模型选择（`large-v3` vs `base`）。
  - 路径自动推断，无需 `config.json`。
  - Obsidian 库路径已固化在 **Global Skill** 中。
- **Agent 驱动的智能总结**:
  - 不仅仅是转录，更通过 Agent 将原始文稿转化为结构清晰的知识笔记。
  - 内置专家级 **Global** `bili-transcribe` Skill。
- **极速 Audio-Only 模式**: 默认仅下载最佳音质音频流，极大节省带宽和时间。
- **双引擎支持**: 完美适配 `whisper` (large-v3) 和 `funasr`。

## 🧠 Agent 协作流程

⚠️ **重要：** 任何执行“视频转录”或“生成笔记”任务时，**必须**首先调用并遵循 **Global** `bili-transcribe` Skill。

1.  **激活技能**: 调用 `Skill(name="bili-transcribe")`。
2.  **执行转录**: 运行 `./venv/bin/python3 src/main.py <URL>`。
3.  **捕获信号**: 脚本输出 `🚀 [ACTION REQUIRED]` 提示时，即表示 ASR 完成。
4.  **读取总结**: 读取 `output/transcripts/` 下的原始文稿，根据 Skill 的 `PROMPT.md` 生成总结笔记。
5.  **物理落盘**: 必须使用 `write_file` 将笔记保存至 Obsidian 的 `BiliNotes/` 目录。

## 📂 目录结构

- `src/`: 核心 Python 处理引擎 (下载/提取/转录/日志)。
- `output/`: 
  - `transcripts/`: 原始 ASR 文稿存档。
  - `logs/`: 详细的执行日志。
- `bin/`: 存放 FFmpeg 等二进制工具。
- `ASR_BENCHMARK.md`: Whisper 与 FunASR 的性能对比评测。

## 🛠️ 更新日志

- **2026-03-07**:
    - **Zero Config 架构**: 彻底移除 `config.json` 依赖。所有路径配置与硬件优化实现 100% 自动化。
    - **文档合并**: 将 `README.md` 与 `GEMINI.md` 合并，确立 `GEMINI.md` 为核心指令集。
- **2026-03-05**:
    - **结构化日志与性能监控**: 引入 `logging` 模块，修复 ASR 延迟计时 BUG，集成 `tqdm` 实时进度条。
    - **硬件加速**: 完成 RTX 5070 Ti (WSL2) 深度适配，转录效率提升约 20x。
- **2026-01-31**:
    - **bili-transcribe 升级**: 集成 LLM 智能总结功能，实现从视频到 Obsidian 知识库的闭环。
- **2026-01-27**:
    - **Skill 固化**: 创建并固化全局 `bili-transcribe` 专家技能。
