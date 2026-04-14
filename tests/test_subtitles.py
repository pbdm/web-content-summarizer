import json
from pathlib import Path

from src.subtitles import SubtitleFetcher


def test_pick_language_prefers_manual_chinese_variant():
    fetcher = SubtitleFetcher()
    tracks = {"en": [{}], "zh-CN": [{}], "ja": [{}]}
    assert fetcher._pick_language(tracks) == "zh-CN"


def test_pick_track_prefers_structured_formats():
    fetcher = SubtitleFetcher()
    entries = [{"ext": "vtt", "url": "vtt"}, {"ext": "json", "url": "json"}]
    assert fetcher._pick_track(entries)["ext"] == "json"


def test_parse_bilibili_json_subtitles():
    fetcher = SubtitleFetcher()
    payload = {
        "body": [
            {"from": 0.5, "to": 1.0, "content": "第一句"},
            {"from": 1.5, "to": 2.0, "content": "第二句"},
        ]
    }
    segments = fetcher._parse_subtitle(json.dumps(payload), "json")
    assert [(segment.start, segment.text) for segment in segments] == [(0.5, "第一句"), (1.5, "第二句")]


def test_parse_vtt_subtitles():
    fetcher = SubtitleFetcher()
    raw_text = """WEBVTT

00:00:01.000 --> 00:00:03.000
hello world

00:00:04.500 --> 00:00:06.000
next line
"""
    segments = fetcher._parse_subtitle(raw_text, "vtt")
    assert [(segment.start, segment.text) for segment in segments] == [(1.0, "hello world"), (4.5, "next line")]


def test_load_cookie_header_from_single_line_file(tmp_path):
    cookie_path = tmp_path / "cookies.txt"
    cookie_path.write_text("SESSDATA=abc; bili_jct=def\n", encoding="utf-8")
    assert SubtitleFetcher._load_cookie_header(cookie_path) == "SESSDATA=abc; bili_jct=def"


def test_normalize_bilibili_tracks_converts_scheme_and_groups_language():
    fetcher = SubtitleFetcher()
    tracks = fetcher._normalize_bilibili_tracks(
        [
            {"lan": "ai-zh", "subtitle_url": "//example.com/subtitle.json"},
            {"lan": "en", "subtitle_url": "https://example.com/en.json"},
        ]
    )
    assert tracks["ai-zh"][0]["url"] == "https://example.com/subtitle.json"
    assert tracks["en"][0]["ext"] == "json"
