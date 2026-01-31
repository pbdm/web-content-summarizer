import pytest
from pathlib import Path
from src.transcriber import Transcriber

def test_transcriber_fallback_cuda_to_cpu(mocker):
    # Mock WhisperModel to fail on first call (cuda) and succeed on second (cpu)
    mock_whisper = mocker.patch("src.transcriber.WhisperModel")
    
    def side_effect(model_size, device, compute_type, num_workers):
        if device == "cuda":
            raise RuntimeError("CUDA failed")
        return mocker.Mock()

    mock_whisper.side_effect = side_effect

    # Initialize Transcriber with cuda
    transcriber = Transcriber(model_size="tiny", device="cuda", compute_type="float16")
    
    # Check if fallback happened
    # 1. Initial call with cuda
    # 2. Recursive call with cpu
    assert mock_whisper.call_count == 2
    
    # Last call should be cpu
    args, kwargs = mock_whisper.call_args
    assert kwargs['device'] == "cpu"
    assert kwargs['compute_type'] == "int8"

def test_transcriber_fallback_model_size(mocker):
    # Mock WhisperModel to fail for 'large-v3' and succeed for 'medium'
    mock_whisper = mocker.patch("src.transcriber.WhisperModel")
    
    def side_effect(model_size, device, compute_type, num_workers):
        if model_size == "large-v3":
            raise RuntimeError("OOM")
        return mocker.Mock()

    mock_whisper.side_effect = side_effect

    # Initialize Transcriber with large-v3
    transcriber = Transcriber(model_size="large-v3", device="cpu", compute_type="int8")
    
    # Check if fallback happened
    assert mock_whisper.call_count == 2
    
    # Last call should be medium
    args, _ = mock_whisper.call_args_list[-1]
    assert args[0] == "medium"

def test_transcriber_transcribe_call(mocker):
    mock_model = mocker.Mock()
    mocker.patch("src.transcriber.WhisperModel", return_value=mock_model)
    
    # Mock segments and info
    mock_model.transcribe.return_value = ([], mocker.Mock(language="zh", duration=10.0))
    
    transcriber = Transcriber(model_size="tiny")
    transcriber.transcribe(Path("fake.wav"))
    
    assert mock_model.transcribe.called
