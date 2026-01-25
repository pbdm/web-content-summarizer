import pytest
from pathlib import Path
from src.formatter import MarkdownFormatter

class MockSegment:
    def __init__(self, start, text, type="speech"):
        self.start = start
        self.text = text
        self.type = type

def test_timestamp_formatting():
    formatter = MarkdownFormatter()
    assert formatter._format_timestamp(0) == "00:00:00"
    assert formatter._format_timestamp(65) == "00:01:05"
    assert formatter._format_timestamp(3665) == "01:01:05"

def test_markdown_structure(tmp_path):
    formatter = MarkdownFormatter()
    output_file = tmp_path / "test.md"
    segments = [
        MockSegment(10, "Hello world"),
        MockSegment(20, "OCR Text", type="ocr")
    ]
    
    formatter.save(segments, output_file, "Test Title", "https://bilibili.com/video/BV123")
    
    content = output_file.read_text(encoding="utf-8")
    # 检查 YAML
    assert "source: https://bilibili.com/video/BV123" in content
    # 检查标题
    assert "# Test Title" in content
    # 检查语音时间戳链接
    assert "[00:00:10](https://bilibili.com/video/BV123?t=10) Hello world" in content
    # 检查 OCR Callout
    assert "[!abstract] 📺 画面文字 (00:00:20)" in content
    assert "OCR Text" in content
