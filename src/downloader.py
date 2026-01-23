import yt_dlp
from pathlib import Path
from .config import TEMP_DIR, FFMPEG_PATH

class VideoDownloader:
    def __init__(self):
        # 配置 yt-dlp 使用我们本地的 ffmpeg 进行可能的合并操作
        self.ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # 下载最佳画质+最佳音质
            'outtmpl': str(TEMP_DIR / '%(title)s.%(ext)s'), # 临时文件名模板
            'ffmpeg_location': str(FFMPEG_PATH.parent), # 指定 ffmpeg 目录
            'merge_output_format': 'mp4', # 最终合并为 mp4 (如果需要合并)
            'quiet': True,
            'no_warnings': True,
        }

    def download(self, url: str) -> Path:
        """
        下载视频并返回本地文件路径。
        """
        print(f"Downloading video from: {url}...")
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 获取生成的文件名
            filename = ydl.prepare_filename(info)
            
            # yt-dlp 可能会修改扩展名（例如合并后变为 mp4），我们需要找到实际存在的文件
            # 如果是合并操作，文件名后缀可能会变
            if info.get('requested_downloads'):
                # 尝试获取合并后的文件名
                filename = info['requested_downloads'][0]['filepath']
            
            # 简单的修正：如果文件名是 .webm 结尾但我们强制合并为 mp4，yt-dlp 可能会返回 .mp4
            # 这里我们直接返回 path 对象
            filepath = Path(filename)
            
            # 如果合并发生，扩展名可能已经改变，重新检查
            if not filepath.exists():
                filepath = filepath.with_suffix('.mp4')
            
            if not filepath.exists():
                 raise FileNotFoundError(f"Downloaded file not found: {filepath}")

            print(f"Download complete: {filepath.name}")
            return filepath
