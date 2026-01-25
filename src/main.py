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
from src.config import OUTPUT_DIR, TEMP_DIR, OBSIDIAN_VAULT_PATH

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
    parser.add_argument("--obsidian-vault", default=OBSIDIAN_VAULT_PATH, help=f"Path to Obsidian vault (default: {OBSIDIAN_VAULT_PATH})")
    parser.add_argument("--fast", action="store_true", help="Speed mode: uses lower beam size and quantization")
    
    args = parser.parse_args()

    # 初始化模块
    downloader = VideoDownloader()
    extractor = AudioExtractor()
    transcriber = None 
    formatter = MarkdownFormatter()

    try:
        # 1. 下载视频
        video_path = downloader.download(args.url)
        video_title = video_path.stem

        # 2. 提取音频
        audio_path = extractor.extract(video_path)

        # 3. 加载模型并转录 (动态加载引擎)
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
            # Whisper 模式：根据 --fast 决定硬件加速参数，但不降低搜索精度
            # 保持 beam_size=5 以确保极致准确
            # 经测试 int8_float16 在部分环境中不被支持，这里改回 float16
            compute_type = "float16" 
            num_workers = 4 if args.fast else 1
            beam_size = 5 # 始终保持最高精度
            
            print(f"Engine: Whisper ({args.model}) | High-Perf Mode: {args.fast} | Beam Size: {beam_size}")
            transcriber = Transcriber(
                model_size=args.model, 
                compute_type=compute_type,
                num_workers=num_workers
            )
            
        asr_segments = transcriber.transcribe(audio_path, beam_size=beam_size if args.engine != "funasr" else 5)
        
        # 封装结果并显示进度
        content_items = []
        count = 0
        for seg in asr_segments:
            content_items.append(ContentItem(seg.start, seg.text, "speech"))
            count += 1
            if count % 20 == 0:
                print(f"[Progress] Transcribed up to {seg.start:.1f}s...")

        # 4. 生成 Markdown
        md_filename = f"{video_title}_{args.engine}.md"
        
        if args.obsidian_vault:
            vault_path = Path(args.obsidian_vault)
            if vault_path.exists():
                inbox_dir = vault_path / "BiliInbox"
                inbox_dir.mkdir(exist_ok=True)
                md_path = inbox_dir / md_filename
                print(f"📂 Obsidian Mode: Saving note to {md_path}")
            else:
                md_path = OUTPUT_DIR / md_filename
        else:
            md_path = OUTPUT_DIR / md_filename
        
        formatter.save(content_items, md_path, title=video_title, source_url=args.url)

        # 5. 整理文件 (Finalize)
        final_video_path = OUTPUT_DIR / video_path.name
        if video_path.resolve() != final_video_path.resolve():
            shutil.move(str(video_path), str(final_video_path))
            print(f"Video moved to: {final_video_path}")

        # 清理音频
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