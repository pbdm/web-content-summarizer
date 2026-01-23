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

    def download(self, url: str) -> Path:
        """
        下载视频并返回本地文件路径。
        如果视频已在 output/ 目录存在，则直接返回该路径。
        """
        print(f"Analyzing URL: {url}...")
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            # 1. 预先获取信息，不下载
            info = ydl.extract_info(url, download=False)
            
            # 预测文件名
            # 注意：prepare_filename 返回的是模板生成的文件名，
            # 如果配置了 merge_output_format='mp4'，后缀最终会变成 mp4
            # 但 prepare_filename 可能返回 .webm 或 .m4a
            # 我们主要关心文件名主体 (title)
            temp_filename = ydl.prepare_filename(info)
            temp_path = Path(temp_filename)
            
            # 强制修正后缀为 mp4 (因为我们设置了 merge_output_format)
            # 同时也检查原始后缀，以防万一
            potential_filenames = [temp_path.name, temp_path.with_suffix('.mp4').name]
            
            # 2. 检查 Output 目录是否存在
            for fname in potential_filenames:
                final_path = OUTPUT_DIR / fname
                if final_path.exists():
                    print(f"Found existing video in output: {final_path.name}")
                    return final_path

            # 3. 如果没找到，开始下载
            print(f"Downloading video...")
            error_code = ydl.download([url])
            
            # 下载后的路径检查 (逻辑同上)
            if info.get('requested_downloads'):
                filename = info['requested_downloads'][0]['filepath']
            else:
                filename = ydl.prepare_filename(info)
            
            filepath = Path(filename)
            
            # 修正：如果文件不存在，可能是合并成了 mp4
            if not filepath.exists():
                filepath = filepath.with_suffix('.mp4')
            
            if not filepath.exists():
                 raise FileNotFoundError(f"Downloaded file not found: {filepath}")

            print(f"Download complete: {filepath.name}")
            return filepath
