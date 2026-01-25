from faster_whisper import WhisperModel
from pathlib import Path
from .config import DEFAULT_MODEL_SIZE, DEFAULT_DEVICE, DEFAULT_COMPUTE_TYPE, DEFAULT_NUM_WORKERS

class Transcriber:
    def __init__(self, model_size=DEFAULT_MODEL_SIZE, device=DEFAULT_DEVICE, 
                 compute_type=DEFAULT_COMPUTE_TYPE, num_workers=DEFAULT_NUM_WORKERS):
        print(f"Loading Whisper model '{model_size}' on {device} ({compute_type}) with {num_workers} workers...")
        # num_workers 允许并行处理
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type, num_workers=num_workers)

    def transcribe(self, audio_path: Path, beam_size=5):
        """
        转录音频文件。
        beam_size: 搜索宽度，1 为最快，5 为最准。
        """
        print(f"Transcribing {audio_path.name} (beam_size={beam_size})...")
        
        segments, info = self.model.transcribe(
            str(audio_path), 
            beam_size=beam_size, 
            language="zh",
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=1000,
                speech_pad_ms=400
            )
        )

        print(f"Detected language '{info.language}' with probability {info.language_probability}")
        print(f"Total audio duration: {info.duration:.2f}s")
        return segments
