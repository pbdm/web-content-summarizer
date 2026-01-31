# BiliTranscribe 智能降级与环境自适应策略

本项目内置了一套自动化的回退机制，旨在确保在任何硬件环境下都能“优先保证任务成功”。

## 1. 硬件层级自适应 (Hardware Fallback)

系统加载模型时遵循“最优尝试，稳健回退”原则：

- **GPU 优先**：若环境支持 CUDA（驱动匹配且显存充足），默认使用 GPU 加速。
- **CPU 回退**：若 CUDA 加载失败（报错 `RuntimeError` 或驱动不兼容），系统会自动执行以下操作：
  - 切换 `device` 为 `cpu`。
  - 强制将 `compute_type` 设为 `int8`（CPU 下性能最平衡）。
  - 将并发数 `num_workers` 设为 4。

## 2. 模型容量降级 (Model Size Fallback)

针对内存溢出或模型加载异常，系统支持递归降级：

**降级链条：**
`large-v3` ➔ `medium` ➔ `small` ➔ `base` ➔ `tiny`

- **逻辑**：若当前模型加载失败，系统会查找降级表并尝试更小的一级模型，直到成功。
- **反馈**：控制台将实时显示 `🔄 Downgrading model size...`。

## 3. 计算类型自动选择

| 设备类型 | 默认 Compute Type | 优势 |
| :--- | :--- | :--- |
| **CUDA (GPU)** | `float16` | 精度高，利用 GPU 核心加速。 |
| **CPU** | `int8` | 显著降低内存占用（约 50%），提升推理速度。 |

## 4. 环境自愈策略 (`setup.sh`)

- **Pip 缺失修复**：自动识别并安装被剥离的 `pip` 模块。
- **FFmpeg 自动化**：通过 Python 生态自动部署静态 FFmpeg 二进制文件，消除系统级依赖。

---
*注：本策略由 OpenCode Agent 结合实际部署阻碍于 2026-01-31 固化至代码。*
