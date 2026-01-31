# 项目备忘录 (OpenCode Context)

## 🚀 启动命令 (One-Liner)

复制以下命令在项目根目录下运行。它会自动配置虚拟环境、安装依赖并适配硬件。

```bash
# 一键初始化 (仅需运行一次)
chmod +x setup.sh && ./setup.sh

# 运行转录 (自动适配 GPU/CPU)
export PYTHONPATH=$PYTHONPATH:.
./venv/bin/python3 src/main.py "YOUR_BILI_URL_HERE"
```

## 🧠 Agent Skills

项目现已集成 **OpenCode Agent Skill**，可通过以下指令直接触发：

- **bili-transcribe**: 自动化下载、音频提取及高精度 ASR 转录。
  - 使用方式：直接在聊天中发送“处理 [BiliURL]”。
  - 特性：
    - **一键部署**: 支持 `setup.sh` 快速搭建，自动修复精简系统的 pip/venv 问题。
    - **硬件适配**: 自动检测 CUDA，智能切换 GPU (float16) 或 CPU (int8) 模式。
    - **智能总结**: 生成带时间戳的 Markdown 文稿并归档至 Obsidian (`BiliNotes`)。

## ⚙️ 配置文件 (config.json)

在根目录创建此文件以启用 Obsidian 自动归档：

```json
{
    "obsidian_vault_path": "/mnt/c/Users/Administrator/Documents/others/content"
}
```

## 📁 目录结构
- `src/`: 源代码
- `output/`: 视频归档及原始文稿 (`transcripts/`)
- `.opencode/skills/`: 固化的 Agent 专家技能
- `config.json`: 用户配置 (被 git 忽略)
- `ASR_BENCHMARK.md`: Whisper 与 FunASR 的详细对比评测

## 🛠️ 更新日志
- **2026-01-31**:
    - **bili-transcribe 升级**: 集成 LLM 总结功能 (Agent-driven)。
    - **架构健壮性优化**: 新增 `setup.sh` 支持一键环境初始化；实现 CUDA/CPU 自动检测与适配；通过 `imageio-ffmpeg` 解决 FFmpeg 二进制依赖问题。
    - **Workflow 调整**: 原始 ASR 文稿仅保存在本地 `output/transcripts/`，Obsidian (`BiliNotes/`) 存储由 Agent 生成的智能总结笔记。
- **2026-01-28**:
    - 完成从 **Gemini** 到 **OpenCode** 的全面迁移。
    - 迁移所有技能配置至 `.opencode/skills/`。
    - 更新 `AGENTS.md` 以反映最新的架构和命名。
- **2026-01-27**:
    - 创建并固化 **bili-transcribe** skill，实现 ASR 流程的标准化。
    - 优化 ASR 自动化脚本，支持 `venv` 自动检测。
    - 确立了笔记扁平化管理规范，移除深层目录嵌套。
- **2026-01-23**: 
    - 集成 **Obsidian** (Frontmatter + 时间戳跳转)。
    - 实现 **智能去重** (跳过已存在的下载/音频提取)。
    - 添加 `config.json` 支持。