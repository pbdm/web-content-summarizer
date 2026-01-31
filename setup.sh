#!/bin/bash
# BiliTranscribe 环境快速搭建脚本

set -e

echo "🔍 检查 Python 环境..."
PYTHON_EXE=$(which python3)

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_EXE -m venv venv --without-pip
    
    GET_PIP_TMP=$(mktemp)
    echo "Downloading pip to $GET_PIP_TMP..."
    curl -sL https://bootstrap.pypa.io/get-pip.py -o "$GET_PIP_TMP"
    ./venv/bin/python3 "$GET_PIP_TMP"
    rm "$GET_PIP_TMP"
fi

echo "📦 安装项目依赖..."
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install imageio-ffmpeg

echo "🎬 配置 FFmpeg..."
mkdir -p bin
FFMPEG_PATH=$(./venv/bin/python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
ln -sf "$FFMPEG_PATH" bin/ffmpeg
ln -sf "$FFMPEG_PATH" bin/ffprobe

echo "✅ 环境搭建完成！"
echo "使用说明: ./venv/bin/python3 src/main.py [URL]"
