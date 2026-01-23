# 项目备忘录 (Gemini Context)

## 🚀 快速启动命令 (One-Liner)

复制以下命令在项目根目录下运行，它会自动处理环境变量（PYTHONPATH 和 CUDA 库路径），确保 Whisper 和 FunASR 都能正常工作。

```bash
export PYTHONPATH=$PYTHONPATH:.
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/venv/lib/python3.12/site-packages/nvidia/cublas/lib:$(pwd)/venv/lib/python3.12/site-packages/nvidia/cudnn/lib

# 运行 Whisper (默认, GPU加速)
./venv/bin/python src/main.py "YOUR_BILI_URL_HERE" --engine whisper

# 运行 FunASR (CPU模式, 适合中文实体识别)
./venv/bin/python src/main.py "YOUR_BILI_URL_HERE" --engine funasr
```

## 📊 引擎对比结论

基于对财经类视频的测试对比：

| 特性 | **Whisper (Large-v3)** | **FunASR (Paraformer)** | 推荐场景 |
| :--- | :--- | :--- | :--- |
| **数字格式化** | ✅ **优秀** (自动转 10%, 2024年) | ❌ 较差 (中文汉字直录) | 财经、数据报告、年份密集的视频 |
| **专有名词** | ⚠️ 一般 (GIC, ETF 较好，国内机构易错) | ✅ **优秀** (博时、集思录识别准) | 包含大量国内机构、人名的视频 |
| **排版/断句** | ✅ **舒适** (按语义分段，适合阅读) | ⚠️ 细碎 (按停顿分行，行数极多) | 需要做笔记、生成文章 |
| **运行速度** | ✅ 极快 (GPU) | ⚡ 尚可 (CPU 非自回归) | 通用 |

**💡 最佳实践**: 默认使用 **Whisper** 生成笔记。如果发现关键人名错误严重，再使用 FunASR 作为辅助校对。

## 📁 目录结构说明
- `src/`: 源代码
- `bin/`: 本地 FFmpeg 二进制文件 (无需系统安装)
- `output/`: 结果目录 (Markdown + MP4)
- `venv/`: Python 虚拟环境

## 🛠️ 维护记录
- **2026-01-23**: 集成 FunASR，解决 NVIDIA 库路径问题，添加双引擎输出支持。
