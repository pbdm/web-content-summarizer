import yt_dlp
from pathlib import Path
from .config import TEMP_DIR, FFMPEG_PATH
from .logger import logger
from .utils import time_it

class VideoDownloader:
    def __init__(self, audio_only=True, cookie_header: str | None = None):
        self.audio_only = audio_only
        # 配置 yt-dlp 使用我们本地的 ffmpeg
        self.ydl_opts = {
            # 如果是 audio_only，只下载最佳音频；否则下载最佳视频+音频
            'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
            'outtmpl': str(TEMP_DIR / '%(title)s.%(ext)s'), # 临时文件名模板
            'ffmpeg_location': str(FFMPEG_PATH.parent), # 指定 ffmpeg 目录
            'quiet': True,
            'no_warnings': True,
        }
        if cookie_header:
            self.ydl_opts['http_headers'] = {'Cookie': cookie_header}
        
        # 只有在下载视频时才强制合并为 mp4
        if not audio_only:
            self.ydl_opts['merge_output_format'] = 'mp4'

    def extract_info(self, url: str):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    @time_it
    def download(self, url: str, info: dict | None = None):
        """
        下载并返回 (本地文件路径, UP主姓名, 发布日期)。
        """
        logger.info(f"🚀 Analyzing URL: {url}...")
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            # 1. 预先获取信息
            info = info or ydl.extract_info(url, download=False)
            uploader = info.get('uploader', 'Unknown')
            upload_date = info.get('upload_date', 'Unknown') # 格式通常为 YYYYMMDD
            
            # 格式化日期 (从 YYYYMMDD 变为 YYYY-MM-DD)
            if upload_date != 'Unknown' and len(upload_date) == 8:
                upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
            
            # 预测文件名
            # prepare_filename 返回的文件名通常带有扩展名
            temp_filename = ydl.prepare_filename(info)
            temp_path = Path(temp_filename)
            
            # 3. 下载
            logger.info(f"⬇️  Downloading {'audio' if self.audio_only else 'video'}...")
            ydl.download([url])
            
            # 获取实际下载的文件路径
            # yt-dlp 有时会在文件名后加一些哈希，或者合并后改名
            if info.get('requested_downloads'):
                filename = info['requested_downloads'][0]['filepath']
            else:
                # Fallback
                filename = ydl.prepare_filename(info)
            
            filepath = Path(filename)
            
            # 如果文件不存在（可能被合并或改名了），尝试寻找相关文件
            if not filepath.exists():
                # 简单的 fallback: 只要 temp 目录下有同名(不同后缀)的文件
                candidates = list(TEMP_DIR.glob(f"{temp_path.stem}.*"))
                if candidates:
                    filepath = candidates[0]
            
            logger.info(f"✅ Download complete: {filepath.name}")
            return filepath, uploader, upload_date
