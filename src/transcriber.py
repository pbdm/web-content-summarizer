from faster_whisper import WhisperModel
from pathlib import Path
from .config import DEFAULT_MODEL_SIZE, DEFAULT_DEVICE, DEFAULT_COMPUTE_TYPE

class Transcriber:
    def __init__(self, model_size=DEFAULT_MODEL_SIZE, device=DEFAULT_DEVICE, compute_type=DEFAULT_COMPUTE_TYPE):
        print(f"Loading Whisper model '{model_size}' on {device} ({compute_type})...")
        print("Note: If this is the first time, it might take a few minutes to download the model.")
        # local_files_only=False 允许首次运行时下载模型
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: Path):
        """
        转录音频文件，返回生成器。
        """
        print(f"Transcribing {audio_path.name}...")
        
        # beam_size=5 是官方推荐的参数，能提高准确率
        # language='zh' 强制指定中文，或者设为 None 自动检测
        segments, info = self.model.transcribe(
            str(audio_path), 
            beam_size=5, 
            language="zh",
            vad_filter=True, # 开启语音活动检测，跳过静音片段
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        print(f"Detected language '{info.language}' with probability {info.language_probability}")
        return segments
