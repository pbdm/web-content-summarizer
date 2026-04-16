import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen
from urllib.parse import urlencode

import yt_dlp

from .config import FFMPEG_PATH, TEMP_DIR
from .logger import logger
from .utils import time_it


@dataclass
class SubtitleSegment:
    start: float
    text: str
    type: str = "speech"


class SubtitleFetcher:
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
    LANGUAGE_PRIORITY = [
        "ai-zh",
        "zh-Hans",
        "zh-CN",
        "zh",
        "zh-Hant",
        "zh-TW",
        "zh-HK",
        "ai-en",
        "en",
    ]
    FORMAT_PRIORITY = ["json3", "json", "vtt", "srt", "srv3", "ttml"]

    def __init__(self, cookie_path: Path | None = None):
        self.cookie_path = cookie_path or Path.cwd() / "cookies.txt"
        self.cookie_header = self._load_cookie_header(self.cookie_path)
        self.ydl_opts = {
            "skip_download": True,
            "ffmpeg_location": str(FFMPEG_PATH.parent),
            "outtmpl": str(TEMP_DIR / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        if self.cookie_header:
            self.ydl_opts["http_headers"] = {"Cookie": self.cookie_header}

    def _extract_bvid(self, url: str) -> str | None:
        patterns = [
            r"bv[Ii]([A-Za-z0-9]{10})",
            r"BV([A-Za-z0-9]{10})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                bvid = match.group(1) if match.group(1) else match.group(0)
                if len(bvid) == 10:
                    return f"BV{bvid}"
        return None

    def _get_bilibili_metadata(self, url: str) -> dict | None:
        bvid = self._extract_bvid(url)
        if not bvid:
            return None

        api_url = (
            f"https://api.bilibili.com/x/web-interface/view?{urlencode({'bvid': bvid})}"
        )
        headers = {
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Referer": "https://www.bilibili.com/",
        }
        if self.cookie_header:
            headers["Cookie"] = self.cookie_header

        try:
            req = Request(api_url, headers=headers)
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data.get("code") == 0:
                    return data.get("data")
        except Exception as e:
            logger.warning(f"Bilibili API metadata fetch failed: {e}")
        return None

    @staticmethod
    def _load_cookie_header(cookie_path: Path) -> str | None:
        if not cookie_path.exists():
            return None

        raw_text = cookie_path.read_text(encoding="utf-8").strip()
        if not raw_text:
            return None

        lines = [
            line.strip()
            for line in raw_text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if not lines:
            return None

        # Support a raw "Cookie" header file. Netscape cookies.txt should still be handled by yt-dlp directly.
        if len(lines) == 1 and "=" in lines[0] and "\t" not in lines[0]:
            return lines[0].removeprefix("Cookie:").strip()

        return None

    def extract_info(self, url: str):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            logger.warning(f"yt-dlp extract failed: {e}, trying Bilibili API...")
            metadata = self._get_bilibili_metadata(url)
            if metadata:
                pubdate = metadata.get("pubdate")
                if pubdate:
                    from datetime import datetime

                    upload_date = datetime.fromtimestamp(pubdate).strftime("%Y%m%d")
                else:
                    upload_date = "Unknown"
                return {
                    "id": metadata.get("aid"),
                    "title": metadata.get("title"),
                    "uploader": metadata.get("owner", {}).get("name"),
                    "upload_date": upload_date,
                    "duration": metadata.get("duration"),
                    "description": metadata.get("desc"),
                }
            raise

    @staticmethod
    def get_video_metadata(info: dict):
        uploader = info.get("uploader", "Unknown")
        upload_date = info.get("upload_date", "Unknown")
        title = info.get("title") or "Untitled"

        if upload_date != "Unknown" and len(upload_date) == 8:
            upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

        return title, uploader, upload_date

    @time_it
    def fetch(self, info: dict, prefer_subtitle: bool = False):
        manual_tracks = info.get("subtitles") or {}
        auto_tracks = info.get("automatic_captions") or {}

        if prefer_subtitle and not manual_tracks and not auto_tracks:
            manual_tracks = self._fetch_bilibili_player_subtitles(info) or {}

        enable_ai_subtitle = prefer_subtitle
        ai_segments = None

        for source_name, track_map in (
            ("manual", manual_tracks),
            ("auto", auto_tracks),
        ):
            if not enable_ai_subtitle:
                break

            language = self._pick_language(track_map)
            if not language:
                continue

            entry = self._pick_track(track_map[language])
            if not entry or not entry.get("url"):
                continue

            logger.info(
                f"📝 Using {source_name} subtitle track: {language} ({entry.get('ext', 'unknown')})"
            )

            try:
                raw_text = self._download_text(entry)
                segments = self._parse_subtitle(raw_text, entry.get("ext", ""))
            except Exception as exc:
                logger.warning(f"⚠️ Subtitle fetch failed for {language}: {exc}")
                continue

            if segments:
                ai_segments = (segments, source_name, language)
                break

        if ai_segments:
            return ai_segments

        logger.info("ℹ️ No usable subtitle track found, falling back to ASR.")
        return None, None, None

    def _fetch_bilibili_player_subtitles(
        self, info: dict, retries: int = 8, delay: float = 2.0
    ) -> dict:
        bvid = info.get("id")
        if not bvid:
            return {}

        cid = self._resolve_bilibili_cid(bvid)
        if not cid:
            return {}

        best_tracks = {}
        best_count = 0

        for attempt in range(retries):
            player_payload = self._get_json(
                "https://api.bilibili.com/x/player/v2",
                params={"bvid": bvid, "cid": cid},
            )
            subtitle_data = ((player_payload or {}).get("data") or {}).get(
                "subtitle"
            ) or {}
            subtitle_items = subtitle_data.get("subtitles") or []

            # 如果没有字幕，等待后重试
            if not subtitle_items:
                if attempt < retries - 1:
                    import time

                    logger.info(
                        f"📝 Attempt {attempt + 1}: no subtitles yet, waiting..."
                    )
                    time.sleep(delay)
                continue

            tracks = self._normalize_bilibili_tracks(subtitle_items)

            lang = "ai-zh"
            if lang in tracks:
                entry = tracks[lang][0]
                try:
                    raw = self._download_text(entry)
                    data = json.loads(raw)
                    body = data.get("body", [])
                    count = len(body)

                    logger.info(
                        f"📝 Attempt {attempt + 1}: {lang} has {count} segments"
                    )

                    if count > best_count:
                        best_count = count
                        best_tracks = tracks
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fetch subtitle: {e}")

        if best_tracks:
            logger.info(f"📝 Using best subtitle with {best_count} segments")
        return best_tracks

    def _resolve_bilibili_cid(self, bvid: str) -> int | None:
        view_payload = self._get_json(
            "https://api.bilibili.com/x/web-interface/view",
            params={"bvid": bvid},
        )
        data = (view_payload or {}).get("data") or {}
        cid = data.get("cid")
        if cid:
            return cid

        pages = data.get("pages") or []
        if pages:
            return pages[0].get("cid")

        return None

    def _normalize_bilibili_tracks(self, subtitle_items: list[dict]) -> dict:
        tracks = {}
        for item in subtitle_items:
            language = item.get("lan")
            subtitle_url = item.get("subtitle_url")
            if not language or not subtitle_url:
                continue
            if subtitle_url.startswith("//"):
                subtitle_url = f"https:{subtitle_url}"
            tracks.setdefault(language, []).append(
                {
                    "ext": "json",
                    "url": subtitle_url,
                    "http_headers": self._default_headers(),
                }
            )
        return tracks

    def _default_headers(self) -> dict:
        headers = {
            "Referer": "https://www.bilibili.com/",
            "Origin": "https://www.bilibili.com",
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if self.cookie_header:
            headers["Cookie"] = self.cookie_header
        return headers

    def _get_json(self, url: str, params: dict | None = None) -> dict:
        query = f"?{urlencode(params)}" if params else ""
        raw_text = self._download_text(
            {
                "url": f"{url}{query}",
                "http_headers": self._default_headers(),
            }
        )
        return json.loads(raw_text)

    def _pick_language(self, tracks: dict) -> str | None:
        if not tracks:
            return None

        for language in self.LANGUAGE_PRIORITY:
            if language in tracks:
                return language

        zh_candidates = sorted(lang for lang in tracks if lang.lower().startswith("zh"))
        if zh_candidates:
            return zh_candidates[0]

        return sorted(tracks)[0]

    def _pick_track(self, entries: Iterable[dict]) -> dict | None:
        if not entries:
            return None

        by_ext = {entry.get("ext", "").lower(): entry for entry in entries}
        for ext in self.FORMAT_PRIORITY:
            if ext in by_ext:
                return by_ext[ext]

        return next(iter(entries), None)

    def _download_text(self, entry: dict) -> str:
        headers = entry.get("http_headers") or {}
        if self.cookie_header and "Cookie" not in headers:
            headers = {**headers, "Cookie": self.cookie_header}
        request = Request(entry["url"], headers=headers)
        with urlopen(request) as response:
            content_type = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(content_type, errors="replace")

    def _parse_subtitle(self, raw_text: str, ext: str):
        ext = (ext or "").lower()
        if ext in {"json", "json3"}:
            return self._parse_json(raw_text)
        if ext == "vtt":
            return self._parse_vtt(raw_text)
        if ext == "srt":
            return self._parse_srt(raw_text)

        try:
            return self._parse_json(raw_text)
        except Exception:
            pass

        if "WEBVTT" in raw_text:
            return self._parse_vtt(raw_text)

        return self._parse_srt(raw_text)

    def _parse_json(self, raw_text: str):
        payload = json.loads(raw_text)
        segments = []

        if isinstance(payload, dict) and isinstance(payload.get("body"), list):
            for item in payload["body"]:
                text = (item.get("content") or "").strip()
                if text:
                    segments.append(
                        SubtitleSegment(start=float(item.get("from", 0.0)), text=text)
                    )
            return segments

        if isinstance(payload, dict) and isinstance(payload.get("events"), list):
            for event in payload["events"]:
                segs = event.get("segs") or []
                text = "".join(seg.get("utf8", "") for seg in segs).strip()
                if text:
                    segments.append(
                        SubtitleSegment(
                            start=float(event.get("tStartMs", 0)) / 1000.0, text=text
                        )
                    )
            return segments

        if isinstance(payload, list):
            for item in payload:
                text = (item.get("text") or item.get("content") or "").strip()
                if not text:
                    continue
                start = item.get("start", item.get("from", 0.0))
                segments.append(SubtitleSegment(start=float(start), text=text))
            return segments

        raise ValueError("Unsupported subtitle JSON format")

    def _parse_vtt(self, raw_text: str):
        segments = []
        blocks = re.split(r"\n\s*\n", raw_text.strip())

        for block in blocks:
            lines = [
                line.strip("\ufeff") for line in block.splitlines() if line.strip()
            ]
            if not lines or lines[0] == "WEBVTT":
                continue

            timestamp_line = next((line for line in lines if "-->" in line), None)
            if not timestamp_line:
                continue

            text_lines = [
                line
                for line in lines
                if line != timestamp_line and "-->" not in line and not line.isdigit()
            ]
            text = "\n".join(text_lines).strip()
            if not text:
                continue

            start_text = timestamp_line.split("-->", 1)[0].strip()
            segments.append(
                SubtitleSegment(start=self._parse_timestamp(start_text), text=text)
            )

        return segments

    def _parse_srt(self, raw_text: str):
        segments = []
        blocks = re.split(r"\n\s*\n", raw_text.strip())

        for block in blocks:
            lines = [
                line.strip("\ufeff") for line in block.splitlines() if line.strip()
            ]
            if len(lines) < 2:
                continue

            timestamp_line = next((line for line in lines if "-->" in line), None)
            if not timestamp_line:
                continue

            text_lines = [
                line for line in lines if line != timestamp_line and not line.isdigit()
            ]
            text = "\n".join(text_lines).strip()
            if not text:
                continue

            start_text = timestamp_line.split("-->", 1)[0].strip()
            segments.append(
                SubtitleSegment(start=self._parse_timestamp(start_text), text=text)
            )

        return segments

    def _parse_timestamp(self, value: str) -> float:
        cleaned = value.split(" ", 1)[0].replace(",", ".")
        parts = cleaned.split(":")
        if len(parts) == 2:
            parts = ["0"] + parts
        if len(parts) != 3:
            raise ValueError(f"Unsupported timestamp: {value}")

        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
