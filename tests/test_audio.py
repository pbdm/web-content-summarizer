import pytest
from pathlib import Path
from src.audio import AudioExtractor

def test_audio_extraction_skip_if_exists(mocker):
    extractor = AudioExtractor()
    mock_video = Path("video.mp4")
    mock_audio = Path("video.wav")
    
    # 模拟文件已存在且不为空
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch.object(Path, "stat", return_value=mocker.Mock(st_size=100))
    
    # 确保没有调用 subprocess
    mock_run = mocker.patch("subprocess.run")
    
    res = extractor.extract(mock_video)
    assert res == mock_audio
    mock_run.assert_not_called()

def test_ffmpeg_command_generation(mocker):
    extractor = AudioExtractor()
    mock_video = Path("video.mp4")
    
    # 模拟文件不存在
    mocker.patch.object(Path, "exists", side_effect=[False, True]) # wav不存在, video存在
    mocker.patch.object(Path, "with_suffix", return_value=Path("video.wav"))
    
    mock_run = mocker.patch("subprocess.run")
    
    extractor.extract(mock_video)
    
    # 检查是否调用了 FFmpeg 且包含正确参数
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert "ffmpeg" in cmd[0]
    assert "-ar" in cmd
    assert "16000" in cmd
    assert "video.wav" in cmd
