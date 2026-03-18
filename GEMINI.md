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

⚠️ **重要：** 任何时候执行“视频转录”或“生成笔记”任务时，**必须**首先调用并遵循 **Global** `bili-transcribe` Skill。

- **bili-transcribe**: 自动化下载、音频提取及高精度 ASR 转录。
  - **触发规则**: 当用户提供 BiliBili 链接要求“总结”、“转录”或“笔记”时，**强制加载**此 Skill。
  - **使用方式**:
    1. 调用 `Skill(name="bili-transcribe")` 激活全局专家技能。
    2. 执行脚本 `./venv/bin/python3 src/main.py ...`
    3. **关键步骤**: 必须等待脚本输出 `🚀 [ACTION REQUIRED]` 提示。
    4. **关键步骤**: 必须读取脚本生成的原始文稿。
    5. **关键步骤**: 根据 `bili-transcribe` Skill 的 `PROMPT.md` 生成总结并归档至 Obsidian。

## ⚙️ 配置文件 (config.json)

> [!NOTE] 
> 本项目已不再从 `config.json` 读取 `obsidian_vault_path`。该路径已硬编码在 **Global** `bili-transcribe` Skill 中：
> `/mnt/c/Users/Administrator/Documents/others/content/BiliNotes/`

```json
{}
```

## 📁 目录结构
- `src/`: 源代码
- `output/`: 视频归档及原始文稿 (`transcripts/`)，日志 (`logs/`)
- `Global Skill`: `bili-transcribe` 已作为全局专家技能固化
- `config.json`: 用户配置 (被 git 忽略)
- `ASR_BENCHMARK.md`: Whisper 与 FunASR 的详细对比评测

## 🛠️ 更新日志
- **2026-03-05**:
    - **结构化日志与性能监控**: 引入 `logging` 模块和 `time_it` 装饰器，实现多级日志持久化及精准的步骤耗时统计（已修复 ASR 生成器延迟计时 BUG）。
    - **实时进度反馈**: 集成 `tqdm` 进度条，支持转录百分比、预计剩余时间 (ETA) 及处理速度显示。
    - **硬件加速深度适配**: 完成 **RTX 5070 Ti** (WSL2) 环境构建，优化 Python 环境至 3.12 并配置 CUDA 12.4 + cuDNN，转录效率提升约 20x。
    - **元数据增强**: 支持提取视频发布日期 (`published`) 并同步至文稿 Frontmatter，强化知识管理维度。
    - **Skill 全局化**: 迁移 `bili-transcribe` 专家技能至全局路径，实现跨项目、跨场景的认知能力复用。
- **2026-02-08**:
    - **Skill 强制性增强**: 在 `AGENTS.md` 中明确了 Skill 的强制调用规则。
    - **防御性编程**: `src/main.py` 现在会输出 `[ACTION REQUIRED]` 提示，防止 Agent 遗漏 Obsidian 归档步骤。
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
