import argparse
import shutil
import sys
import os
import time
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from src.downloader import VideoDownloader
from src.audio import AudioExtractor
from src.transcriber import Transcriber
from src.formatter import MarkdownFormatter
from src.config import OUTPUT_DIR, TEMP_DIR, LOCAL_TRANSCRIPT_DIR, DEFAULT_COMPUTE_TYPE, DEFAULT_DEVICE, DEFAULT_NUM_WORKERS, DEFAULT_MODEL_SIZE
from src.logger import logger
from src.utils import time_it

class ContentItem:
    def __init__(self, start, text, type="speech"):
        self.start = start
        self.text = text
        self.type = type # "speech" or "ocr"

@time_it
def process_pipeline(args):
    """
    完整的处理流水线。
    """
    # 初始化模块 (默认为纯音频模式)
    downloader = VideoDownloader(audio_only=True)
    extractor = AudioExtractor()
    transcriber = None 
    formatter = MarkdownFormatter()

    # 1. 下载 (Audio)
    media_path, uploader, upload_date = downloader.download(args.url)
    video_title = media_path.stem

    # 2. 转换/标准化音频 (Convert to 16k wav)
    audio_path = extractor.extract(media_path)

    # 3. 加载模型并转录
    beam_size = 5 # Default beam size
    if args.engine == "funasr":
        logger.info("Engine: FunASR (Lazy Loading...)")
        try:
            from src.transcriber_funasr import FunASRTranscriber
            transcriber = FunASRTranscriber()
        except Exception as e:
            logger.error(f"❌ Error loading FunASR: {e}")
            logger.info("Hint: FunASR requires additional libraries like torchaudio. If they are broken, use 'whisper' engine instead.")
            sys.exit(1)
    else:
        # Whisper 模式
        compute_type = args.compute_type
        num_workers = 4 if args.fast else DEFAULT_NUM_WORKERS
        
        logger.info(f"Engine: Whisper ({args.model}) | Device: {args.device} | Compute: {compute_type} | Workers: {num_workers} | High-Perf Mode: {args.fast}")
        transcriber = Transcriber(
            model_size=args.model, 
            device=args.device,
            compute_type=compute_type,
            num_workers=num_workers
        )
        
    # 统一接口调用
    logger.info(f"⚡ Starting ASR inference...")
    content_items = []
    asr_segments = transcriber.transcribe(audio_path, beam_size=beam_size)
    
    # 封装结果
    for seg in asr_segments:
        content_items.append(ContentItem(seg.start, seg.text, "speech"))

    # 4. 生成原始 Markdown
    md_filename = f"{uploader}-{video_title}_{args.engine}.md"
    local_md_path = LOCAL_TRANSCRIPT_DIR / md_filename
    
    logger.info(f"📂 Saving raw transcript to local path: {local_md_path}")
    formatter.save(content_items, local_md_path, title=video_title, source_url=args.url, uploader=uploader, upload_date=upload_date)
    
    # 关键：打印特定的成功标识，供 Agent 识别
    print(f"TRANSCRIPT_SAVED: {local_md_path.absolute()}")

    # 6. 提示 Agent 进行 Obsidian 智能总结 (Anti-Omission Step)
    from src.config import OBSIDIAN_VAULT_PATH
    if OBSIDIAN_VAULT_PATH:
        obsidian_note_dir = Path(OBSIDIAN_VAULT_PATH) / "BiliNotes"
        obsidian_note_dir.mkdir(parents=True, exist_ok=True)
        target_md = obsidian_note_dir / f"{video_title}.md"
        
        logger.info(f"🤖 Agent summarizing session starting...")
        summary_start_time = time.perf_counter()
        
        print("\n" + "="*60)
        print("🚀 [ACTION REQUIRED] Agent Skill Triggered")
        print(f"Please read the transcript above and generate a summary note.")
        print(f"Target Path: {target_md}")
        print("="*60 + "\n")
        
        # 注意：Agent 的总结是在脚本运行后的对话中完成的，
        # 脚本本身在此处会结束。
    else:
        logger.info("Obsidian vault path not configured. Skipping summary prompt.")

    # 5. 清理文件
    if media_path.exists() and media_path.resolve() != audio_path.resolve():
        os.remove(media_path)

    if not args.keep_audio:
        if audio_path.exists():
            os.remove(audio_path)
            logger.info("🗑️  Temporary audio file removed.")

def main():
    parser = argparse.ArgumentParser(description="BiliTranscribe: Download and transcribe Bilibili videos to Markdown.")
    parser.add_argument("url", help="Bilibili video URL")
    parser.add_argument("--model", default=DEFAULT_MODEL_SIZE, help=f"Whisper model size (default: {DEFAULT_MODEL_SIZE})")
    parser.add_argument("--keep-audio", action="store_true", help="Keep the intermediate WAV audio file")
    parser.add_argument("--engine", choices=["whisper", "funasr"], default="whisper", help="ASR engine to use (default: whisper)")
    parser.add_argument("--fast", action="store_true", help="Speed mode: uses lower beam size and quantization")
    parser.add_argument("--device", default=DEFAULT_DEVICE, help=f"Device to use (default: {DEFAULT_DEVICE})")
    parser.add_argument("--compute-type", default=DEFAULT_COMPUTE_TYPE, help=f"Compute type (default: {DEFAULT_COMPUTE_TYPE})")
    
    args = parser.parse_args()

    try:
        process_pipeline(args)
        logger.info("✨ All processes completed successfully!")
    except Exception as e:
        logger.error(f"💥 Critical Error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
