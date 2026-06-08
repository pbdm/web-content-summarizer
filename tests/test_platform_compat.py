from pathlib import Path
import subprocess
import sys

import pytest

from src import logger as logger_module
from src import transcribe_url


def test_resolve_venv_python_prefers_windows_scripts(monkeypatch):
    project_root = Path(r"C:\demo\project")
    monkeypatch.setattr(transcribe_url, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(transcribe_url.sys, "executable", r"C:\Python\python.exe")

    def fake_exists(self):
        return self == project_root / "venv" / "Scripts" / "python.exe"

    monkeypatch.setattr(Path, "exists", fake_exists)

    assert transcribe_url.resolve_venv_python() == (
        project_root / "venv" / "Scripts" / "python.exe"
    )


def test_resolve_venv_python_falls_back_to_current_interpreter(monkeypatch):
    project_root = Path("/demo/project")
    monkeypatch.setattr(transcribe_url, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(transcribe_url.sys, "executable", "/usr/bin/python3")
    monkeypatch.setattr(Path, "exists", lambda self: False)

    assert transcribe_url.resolve_venv_python() == Path("/usr/bin/python3")


def test_config_uses_windows_executable_names(monkeypatch, tmp_path):
    import src.config as config

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    ffmpeg = bin_dir / "ffmpeg.exe"
    ffmpeg.write_text("stub", encoding="utf-8")

    monkeypatch.setattr(config, "BIN_DIR", bin_dir)
    monkeypatch.setattr(config.os, "name", "nt")
    monkeypatch.setattr(config.shutil, "which", lambda name: None)

    assert config.get_platform_executable_name("ffmpeg") == "ffmpeg.exe"
    assert config.find_ffmpeg("ffmpeg") == ffmpeg


def test_expand_configured_path_supports_home_directory():
    import src.config as config

    assert config.resolve_configured_path("~/notes", config.PROJECT_ROOT) == (
        Path("~/notes").expanduser()
    )


def test_transcribe_url_script_runs_without_src_import_failure():
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "src" / "transcribe_url.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Usage: python transcribe_url.py <URL> [options]" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr


def test_coerce_console_text_replaces_unencodable_characters():
    text = "🚀 [ACTION REQUIRED]"

    safe_text = logger_module.coerce_console_text(text, "gbk")

    assert safe_text != text
    assert "[ACTION REQUIRED]" in safe_text


def test_safe_print_handles_gbk_stream_without_raising():
    class FakeStream:
        encoding = "gbk"

        def __init__(self):
            self.buffer = []

        def write(self, text):
            text.encode(self.encoding)
            self.buffer.append(text)

        def flush(self):
            return None

    stream = FakeStream()

    logger_module.safe_print("🚀", "[ACTION REQUIRED]", stream=stream)

    assert "".join(stream.buffer).endswith("[ACTION REQUIRED]\n")
