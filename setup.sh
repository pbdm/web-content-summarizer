#!/bin/bash
# BiliTranscribe 环境快速搭建脚本

set -e

echo "🔍 检查 Python 环境..."
PYTHON_EXE=$(which python3)

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON_EXE" -m venv venv
fi

echo "📦 安装项目依赖..."
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -m pip install imageio-ffmpeg

echo "🎬 配置 FFmpeg..."
mkdir -p bin
FFMPEG_PATH=$(./venv/bin/python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
ln -sf "$FFMPEG_PATH" bin/ffmpeg
ln -sf "$FFMPEG_PATH" bin/ffprobe

echo "✅ 环境搭建完成！"
echo "Linux 使用说明: ./venv/bin/python src/main.py [URL]"
