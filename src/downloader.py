import yt_dlp
from pathlib import Path
from .config import TEMP_DIR, OUTPUT_DIR, FFMPEG_PATH

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

    def download(self, url: str):
        """
        下载视频并返回 (本地文件路径, UP主姓名)。
        如果视频已在 output/ 目录存在，则直接返回该路径。
        """
        print(f"Analyzing URL: {url}...")
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            # 1. 预先获取信息
            info = ydl.extract_info(url, download=False)
            uploader = info.get('uploader', 'Unknown')
            
            # 预测文件名
            temp_filename = ydl.prepare_filename(info)
            temp_path = Path(temp_filename)
            potential_filenames = [temp_path.name, temp_path.with_suffix('.mp4').name]
            
            # 2. 检查 Output 目录
            for fname in potential_filenames:
                final_path = OUTPUT_DIR / fname
                if final_path.exists():
                    print(f"Found existing video in output: {final_path.name}")
                    return final_path, uploader

            # 3. 下载
            print(f"Downloading video...")
            ydl.download([url])
            
            if info.get('requested_downloads'):
                filename = info['requested_downloads'][0]['filepath']
            else:
                filename = ydl.prepare_filename(info)
            
            filepath = Path(filename)
            if not filepath.exists():
                filepath = filepath.with_suffix('.mp4')
            
            print(f"Download complete: {filepath.name}")
            return filepath, uploader
