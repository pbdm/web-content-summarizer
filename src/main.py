import argparse
import shutil
import sys
import os
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from src.downloader import VideoDownloader
from src.audio import AudioExtractor
from src.transcriber import Transcriber
try:
    from src.transcriber_funasr import FunASRTranscriber
except ImportError:
    FunASRTranscriber = None
from src.formatter import MarkdownFormatter
from src.config import OUTPUT_DIR, TEMP_DIR

def main():
    parser = argparse.ArgumentParser(description="BiliTranscribe: Download and transcribe Bilibili videos to Markdown.")
    parser.add_argument("url", help="Bilibili video URL")
    parser.add_argument("--model", default="large-v3", help="Whisper model size (default: large-v3)")
    parser.add_argument("--keep-audio", action="store_true", help="Keep the intermediate WAV audio file")
    parser.add_argument("--engine", choices=["whisper", "funasr"], default="whisper", help="ASR engine to use (default: whisper)")
    
    args = parser.parse_args()

    if args.engine == "funasr" and FunASRTranscriber is None:
        print("Error: FunASR is not installed or failed to import.")
        sys.exit(1)

    # 初始化模块
    downloader = VideoDownloader()
    extractor = AudioExtractor()
    # 延迟加载模型，直到确认下载成功后
    transcriber = None 
    formatter = MarkdownFormatter()

    try:
        # 1. 下载视频
        video_path = downloader.download(args.url)
        video_title = video_path.stem

        # 2. 提取音频
        audio_path = extractor.extract(video_path)

        # 3. 加载模型并转录
        # 此时再加载模型，避免下载失败白白占用显存
        if transcriber is None:
            if args.engine == "funasr":
                transcriber = FunASRTranscriber()
            else:
                transcriber = Transcriber(model_size=args.model)
            
        segments = transcriber.transcribe(audio_path)

        # 4. 生成 Markdown
        # 准备输出路径
        # 在 output 目录下创建一个以视频标题命名的子文件夹，或者直接放文件？
        # 这里直接放文件到 output 目录
        md_filename = f"{video_title}_{args.engine}.md"
        md_path = OUTPUT_DIR / md_filename
        
        # 由于 segments 是生成器，我们需要遍历它写入文件
        # 为了给用户即时反馈，我们可以边读边写，或者先收集
        # 这里选择直接传给 formatter，formatter 内部遍历
        formatter.save(segments, md_path, title=video_title, source_url=args.url)

        # 5. 整理文件 (Finalize)
        # 将视频文件移动到 output 目录
        final_video_path = OUTPUT_DIR / video_path.name
        shutil.move(str(video_path), str(final_video_path))
        print(f"Video moved to: {final_video_path}")

        # 清理音频
        if not args.keep_audio:
            os.remove(audio_path)
            print("Temporary audio file removed.")
        else:
            final_audio_path = OUTPUT_DIR / audio_path.name
            shutil.move(str(audio_path), str(final_audio_path))
            print(f"Audio moved to: {final_audio_path}")

        print("\n✨ Process completed successfully!")
        print(f"📂 Output directory: {OUTPUT_DIR}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import os
    main()
