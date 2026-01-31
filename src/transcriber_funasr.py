from funasr import AutoModel
from pathlib import Path

# 定义一个简单的 Segment 类来模仿 Whisper 的输出格式
class Segment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

class FunASRTranscriber:
    def __init__(self, model_dir="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch", device="cpu"):
        print(f"Loading FunASR model '{model_dir}' on {device}...")
        
        # 自动加载 Paraformer (ASR), FSMN-VAD (语音活动检测), CT-Transformer (标点)
        self.model = AutoModel(
            model=model_dir,
            model_revision="v2.0.4",
            vad_model="fsmn-vad",
            vad_model_revision="v2.0.4",
            punc_model="ct-punc-c",
            punc_model_revision="v2.0.4",
            # spk_model="cam++", # 既然不做说话人分离，暂时不需要加载
            # spk_model_revision="v2.0.2",
            device=device
        )

    def transcribe(self, audio_path: Path, **kwargs):
        """
        转录音频文件，返回 Segment 列表。
        kwargs: 接收额外参数（如 beam_size）以保持接口统一，但在 FunASR 中可能会被忽略。
        """
        print(f"Transcribing {audio_path.name} with FunASR...")
        
        # FunASR inference
        # batch_size_s: 动态batch size
        res = self.model.generate(
            input=str(audio_path),
            batch_size_s=300, 
            sentence_timestamp=True  # 获取句级别的时间戳
        )
        
        # res 是一个列表，每个元素对应一个输入文件的结果
        # 结构通常是: [{'key': '...', 'text': '...', 'sentence_info': [{'start': ms, 'end': ms, 'text': '...'}, ...]}]
        
        segments = []
        if res and isinstance(res, list):
            item = res[0] # 因为我们只输入了一个文件
            if 'sentence_info' in item:
                for sent in item['sentence_info']:
                    # FunASR 的时间戳通常是毫秒 (ms)，需要转为秒 (s)
                    start = sent['timestamp'][0][0] / 1000.0
                    end = sent['timestamp'][-1][1] / 1000.0
                    text = sent['text']
                    segments.append(Segment(start, end, text))
            else:
                # Fallback if sentence_info is missing
                print("Warning: No detailed timestamp info found, using full text.")
                segments.append(Segment(0.0, 0.0, item.get('text', '')))
        
        return segments
