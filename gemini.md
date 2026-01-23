# 项目备忘录 (Gemini Context)

## 🚀 启动命令 (One-Liner)

复制以下命令在项目根目录下运行。它会自动处理环境变量，并优先读取 `config.json` 中的配置。

```bash
export PYTHONPATH=$PYTHONPATH:.
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/venv/lib/python3.12/site-packages/nvidia/cublas/lib:$(pwd)/venv/lib/python3.12/site-packages/nvidia/cudnn/lib

# 运行 Whisper (默认, 推荐)
./venv/bin/python src/main.py "YOUR_BILI_URL_HERE"
```

## ⚙️ 配置文件 (config.json)

在根目录创建此文件以启用 Obsidian 自动归档：

```json
{
    "obsidian_vault_path": "/mnt/c/Users/Administrator/Documents/others/content"
}
```

## 📁 目录结构
- `src/`: 源代码
- `output/`: 视频归档 & 默认 Markdown 输出
- `config.json`: 用户配置 (被 git 忽略)
- `ASR_BENCHMARK.md`: Whisper 与 FunASR 的详细对比评测

## 🛠️ 更新日志
- **2026-01-23**: 
    - 集成 **Obsidian** (Frontmatter + 时间戳跳转)。
    - 实现 **智能去重** (跳过已存在的下载/音频提取)。
    - 添加 `config.json` 支持。
