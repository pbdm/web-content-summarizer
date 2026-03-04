import subprocess
from pathlib import Path
from .config import FFMPEG_PATH
from .logger import logger
from .utils import time_it

class AudioExtractor:
    @time_it
    def extract(self, video_path: Path) -> Path:
        """
        从视频中提取音频并转换为 Whisper 友好的格式 (16k wav mono).
        返回音频文件的路径.
        """
        # 输出音频路径 (同名，但后缀为 .wav)
        output_path = video_path.with_suffix('.wav')
        
        # 检查是否已存在
        if output_path.exists() and output_path.stat().st_size > 0:
            logger.info(f"♻️  Using existing audio file: {output_path.name}")
            return output_path
        
        logger.info(f"🎵 Extracting audio to: {output_path.name}...")

        # 构建 ffmpeg 命令
        # -i: 输入
        # -vn: 不包含视频
        # -ar 16000: 采样率 16k (Whisper 训练时的采样率)
        # -ac 1: 单声道
        # -c:a pcm_s16le: 编码格式
        # -y: 覆盖已存在文件
        cmd = [
            str(FFMPEG_PATH),
            '-i', str(video_path),
            '-vn',
            '-ar', '16000',
            '-ac', '1',
            '-c:a', 'pcm_s16le',
            str(output_path),
            '-y'
        ]

        try:
            subprocess.run(
                cmd, 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg audio extraction failed: {e.stderr.decode()}")

        if not output_path.exists():
             raise FileNotFoundError(f"Audio file extraction failed: {output_path}")

        return output_path
