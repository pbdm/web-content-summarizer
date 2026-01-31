from faster_whisper import WhisperModel
from pathlib import Path
from .config import DEFAULT_MODEL_SIZE, DEFAULT_DEVICE, DEFAULT_COMPUTE_TYPE, DEFAULT_NUM_WORKERS

class Transcriber:
    def __init__(self, model_size=DEFAULT_MODEL_SIZE, device=DEFAULT_DEVICE, 
                 compute_type=DEFAULT_COMPUTE_TYPE, num_workers=DEFAULT_NUM_WORKERS):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.num_workers = num_workers
        self.model = self._load_model_with_fallback(model_size, device, compute_type, num_workers)

    def _load_model_with_fallback(self, model_size, device, compute_type, num_workers):
        """带有回退机制的模型加载"""
        try:
            print(f"Loading Whisper model '{model_size}' on {device} ({compute_type})...")
            return WhisperModel(model_size, device=device, compute_type=compute_type, num_workers=num_workers)
        except Exception as e:
            print(f"⚠️ Failed to load model on {device}: {e}")
            
            # 策略 1: 如果是 CUDA 失败，尝试回退到 CPU
            if device == "cuda":
                print("🔄 Falling back to CPU and 'int8'...")
                return self._load_model_with_fallback(model_size, "cpu", "int8", 4)
            
            # 策略 2: 如果是模型太大加载失败，尝试降级模型大小
            fallbacks = {
                "large-v3": "medium",
                "large-v2": "medium",
                "medium": "small",
                "small": "base",
                "base": "tiny"
            }
            if model_size in fallbacks:
                next_model = fallbacks[model_size]
                print(f"🔄 Downgrading model size: {model_size} -> {next_model}...")
                return self._load_model_with_fallback(next_model, device, compute_type, num_workers)
            
            raise e

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
