import argparse
import sys
import os
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from src.downloader import VideoDownloader
from src.audio import AudioExtractor
from src.subtitles import SubtitleFetcher
from src.transcriber import Transcriber
from src.formatter import MarkdownFormatter
from src.config import (
    TRANSCRIPT_DIR,
    DEFAULT_COMPUTE_TYPE,
    DEFAULT_DEVICE,
    DEFAULT_NUM_WORKERS,
    DEFAULT_MODEL_SIZE,
)
from src.logger import logger
from src.utils import time_it


class ContentItem:
    def __init__(self, start, text, type="speech"):
        self.start = start
        self.text = text
        self.type = type  # "speech" or "ocr"


@time_it
def process_pipeline(args):
    """
    完整的处理流水线。
    """
    subtitle_fetcher = SubtitleFetcher()
    # 初始化模块 (默认为纯音频模式)
    downloader = VideoDownloader(
        audio_only=True, cookie_header=subtitle_fetcher.cookie_header
    )
    extractor = AudioExtractor()
    transcriber = None
    formatter = MarkdownFormatter()
    media_path = None
    audio_path = None
    transcript_source = args.engine

    info = subtitle_fetcher.extract_info(args.url)
    video_title, uploader, upload_date = subtitle_fetcher.get_video_metadata(info)

    content_items, subtitle_source, subtitle_language = subtitle_fetcher.fetch(
        info, prefer_subtitle=True
    )

    if content_items:
        subtitle_segments = content_items
        subtitle_src = subtitle_source

        logger.info(f"🔍 Validating AI subtitle with Whisper sample...")

        # 下载音频前 30 秒用于验证
        temp_extractor = AudioExtractor()
        try:
            from src.transcriber import Transcriber

            downloader_preview = VideoDownloader(
                audio_only=True, cookie_header=subtitle_fetcher.cookie_header
            )
            temp_info = subtitle_fetcher.extract_info(args.url)
            temp_media, _, _ = downloader_preview.download(args.url, info=temp_info)
            temp_audio = temp_extractor.extract(temp_media)

            transcriber_preview = Transcriber(
                model_size="base",
                device=args.device,
                compute_type=args.compute_type,
                num_workers=2,
            )
            whisper_segments = transcriber_preview.transcribe(temp_audio, beam_size=5)

            # 清理临时文件
            os.remove(temp_media)
            if temp_audio.exists():
                os.remove(temp_audio)

            # 验证逻辑：对比前 5 个有效句子
            def extract_key_words(segments, count=5):
                words = []
                for seg in segments:
                    text = seg.text.strip()
                    # 跳过纯符号/音乐/过短的内容
                    if len(text) < 2:
                        continue
                    if text.startswith("♪") and text.endswith("♪"):
                        continue
                    words.append(text[:20])
                    if len(words) >= count:
                        break
                return words

            ai_words = extract_key_words(subtitle_segments)
            whisper_words = extract_key_words(whisper_segments)

            logger.info(f"  AI subtitle words: {ai_words[:3]}")
            logger.info(f"  Whisper words:  {whisper_words[:3]}")

            # 检查是否匹配（至少 1 个关键词匹配）
            match_count = sum(
                1 for w in whisper_words if any(w in aw or aw in w for aw in ai_words)
            )
            is_valid = match_count >= 1

            if is_valid:
                content_items = subtitle_segments
                transcript_source = "subtitle"
                logger.info(
                    f"✅ Subtitle valid ({match_count} match), using AI subtitle"
                )
            else:
                logger.info(f"⚠️ Subtitle invalid (no match), falling back to Whisper")
                content_items = None

        except Exception as e:
            logger.warning(f"⚠️ Subtitle validation failed: {e}, using Whisper")
            content_items = None

    if content_items:
        transcript_source = "subtitle"
        logger.info(
            f"✅ Subtitle pipeline selected. Source: {subtitle_source}, Language: {subtitle_language}"
        )
    else:
        # 1. 下载 (Audio)
        media_path, uploader, upload_date = downloader.download(args.url, info=info)
        video_title = media_path.stem

        # 2. 转换/标准化音频 (Convert to 16k wav)
        audio_path = extractor.extract(media_path)

        # 3. 加载模型并转录
        beam_size = 5  # Default beam size
        if args.engine == "funasr":
            logger.info("Engine: FunASR (Lazy Loading...)")
            try:
                from src.transcriber_funasr import FunASRTranscriber

                transcriber = FunASRTranscriber()
            except Exception as e:
                logger.error(f"❌ Error loading FunASR: {e}")
                logger.info(
                    "Hint: FunASR requires additional libraries like torchaudio. If they are broken, use 'whisper' engine instead."
                )
                sys.exit(1)
        else:
            # Whisper 模式
            compute_type = args.compute_type
            num_workers = 4 if args.fast else DEFAULT_NUM_WORKERS

            logger.info(
                f"Engine: Whisper ({args.model}) | Device: {args.device} | Compute: {compute_type} | Workers: {num_workers} | High-Perf Mode: {args.fast}"
            )
            transcriber = Transcriber(
                model_size=args.model,
                device=args.device,
                compute_type=compute_type,
                num_workers=num_workers,
            )

        # 统一接口调用
        logger.info(f"⚡ Starting ASR inference...")
        content_items = []
        asr_segments = transcriber.transcribe(audio_path, beam_size=beam_size)

        # 封装结果
        for seg in asr_segments:
            content_items.append(ContentItem(seg.start, seg.text, "speech"))

    # 4. 生成原始 Markdown
    md_filename = f"{uploader}-{video_title}_{transcript_source}.md"
    local_md_path = TRANSCRIPT_DIR / md_filename

    logger.info(f"📂 Saving raw transcript to local path: {local_md_path}")
    formatter.save(
        content_items,
        local_md_path,
        title=video_title,
        source_url=args.url,
        uploader=uploader,
        upload_date=upload_date,
    )

    # 关键：打印特定的成功标识，供 Agent 识别
    print(f"TRANSCRIPT_SAVED: {local_md_path.absolute()}")

    # 6. 提示 Agent 进行 Obsidian 智能总结 (Anti-Omission Step)
    logger.info(f"🤖 Agent summarizing session starting...")

    print("\n" + "=" * 60)
    print("🚀 [ACTION REQUIRED] Agent Skill Triggered")
    print("Please read the transcript above and generate a summary note.")
    print("Note: Saving to Obsidian BiliNotes/ directory.")
    print("=" * 60 + "\n")

    # 5. 清理文件
    if (
        media_path
        and media_path.exists()
        and audio_path
        and media_path.resolve() != audio_path.resolve()
    ):
        os.remove(media_path)

    if not args.keep_audio and audio_path:
        if audio_path.exists():
            os.remove(audio_path)
            logger.info("🗑️  Temporary audio file removed.")


def main():
    parser = argparse.ArgumentParser(
        description="BiliTranscribe: Download and transcribe Bilibili videos to Markdown."
    )
    parser.add_argument("url", help="Bilibili video URL")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_SIZE,
        help=f"Whisper model size (default: {DEFAULT_MODEL_SIZE})",
    )
    parser.add_argument(
        "--keep-audio", action="store_true", help="Keep the intermediate WAV audio file"
    )
    parser.add_argument(
        "--engine",
        choices=["whisper", "funasr"],
        default="whisper",
        help="ASR engine to use (default: whisper)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Speed mode: uses lower beam size and quantization",
    )
    parser.add_argument(
        "--device",
        default=DEFAULT_DEVICE,
        help=f"Device to use (default: {DEFAULT_DEVICE})",
    )
    parser.add_argument(
        "--compute-type",
        default=DEFAULT_COMPUTE_TYPE,
        help=f"Compute type (default: {DEFAULT_COMPUTE_TYPE})",
    )
    parser.add_argument(
        "--subtitle",
        action="store_true",
        help="Try to use Bilibili subtitles first (may be unstable)",
    )

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
