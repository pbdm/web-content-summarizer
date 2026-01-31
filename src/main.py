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
from src.formatter import MarkdownFormatter
from src.config import OUTPUT_DIR, TEMP_DIR, LOCAL_TRANSCRIPT_DIR, DEFAULT_COMPUTE_TYPE, DEFAULT_DEVICE, DEFAULT_NUM_WORKERS

class ContentItem:
    def __init__(self, start, text, type="speech"):
        self.start = start
        self.text = text
        self.type = type # "speech" or "ocr"

def main():
    parser = argparse.ArgumentParser(description="BiliTranscribe: Download and transcribe Bilibili videos to Markdown.")
    parser.add_argument("url", help="Bilibili video URL")
    parser.add_argument("--model", default="large-v3", help="Whisper model size (default: large-v3)")
    parser.add_argument("--keep-audio", action="store_true", help="Keep the intermediate WAV audio file")
    parser.add_argument("--engine", choices=["whisper", "funasr"], default="whisper", help="ASR engine to use (default: whisper)")
    parser.add_argument("--fast", action="store_true", help="Speed mode: uses lower beam size and quantization")
    parser.add_argument("--device", default=DEFAULT_DEVICE, help=f"Device to use (default: {DEFAULT_DEVICE})")
    parser.add_argument("--compute-type", default=DEFAULT_COMPUTE_TYPE, help=f"Compute type (default: {DEFAULT_COMPUTE_TYPE})")
    
    args = parser.parse_args()

    # 初始化模块 (默认为纯音频模式)
    downloader = VideoDownloader(audio_only=True)
    extractor = AudioExtractor()
    transcriber = None 
    formatter = MarkdownFormatter()

    try:
        # 1. 下载 (Audio)
        media_path, uploader = downloader.download(args.url)
        video_title = media_path.stem

        # 2. 转换/标准化音频 (Convert to 16k wav)
        # 即使下载的是音频，我们也通过这一步将其统一为 Whisper 最佳的 16k mono wav
        audio_path = extractor.extract(media_path)

        # 3. 加载模型并转录
        beam_size = 5 # Default beam size
        if args.engine == "funasr":
            print("Engine: FunASR (Lazy Loading...)")
            try:
                from src.transcriber_funasr import FunASRTranscriber
                transcriber = FunASRTranscriber()
            except Exception as e:
                print(f"❌ Error loading FunASR: {e}")
                print("Hint: FunASR requires additional libraries like torchaudio. If they are broken, use 'whisper' engine instead.")
                sys.exit(1)
        else:
            # Whisper 模式
            compute_type = args.compute_type
            num_workers = 4 if args.fast else DEFAULT_NUM_WORKERS
            beam_size = 5 
            
            print(f"Engine: Whisper ({args.model}) | Device: {args.device} | Compute: {compute_type} | High-Perf Mode: {args.fast}")
            transcriber = Transcriber(
                model_size=args.model, 
                device=args.device,
                compute_type=compute_type,
                num_workers=num_workers
            )
            
        # 统一接口调用
        asr_segments = transcriber.transcribe(audio_path, beam_size=beam_size)
        
        # 封装结果
        content_items = []
        count = 0
        for seg in asr_segments:
            content_items.append(ContentItem(seg.start, seg.text, "speech"))
            count += 1
            if count % 20 == 0:
                print(f"[Progress] Transcribed up to {seg.start:.1f}s...")

        # 4. 生成原始 Markdown
        md_filename = f"{uploader}-{video_title}_{args.engine}.md"
        local_md_path = LOCAL_TRANSCRIPT_DIR / md_filename
        
        print(f"📂 Saving raw transcript to local path: {local_md_path}")
        formatter.save(content_items, local_md_path, title=video_title, source_url=args.url)
        
        # 关键：打印特定的成功标识，供 Agent 识别
        print(f"TRANSCRIPT_SAVED: {local_md_path.absolute()}")

        # 5. 清理文件
        # 清理下载的源文件 (通常是 .m4a 或 .webm)
        if media_path.exists() and media_path.resolve() != audio_path.resolve():
            os.remove(media_path)
            # print("Source media file removed.")

        # 清理转换后的 wav 文件 (除非指定保留)
        if not args.keep_audio:
            if audio_path.exists():
                os.remove(audio_path)
                print("Temporary audio file removed.")

        print("\n✨ Process completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
