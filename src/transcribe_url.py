import subprocess
import sys
from pathlib import Path


def run_transcribe(url, engine="whisper", model="large-v3", fast=False):
    project_root = Path(__file__).parent.parent.absolute()
    main_py = project_root / "src" / "main.py"
    venv_python = project_root / "venv" / "bin" / "python3"

    # 优先使用项目内的虚拟环境
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    cmd = [python_exe, str(main_py), url, "--engine", engine, "--model", model]
    if fast:
        cmd.append("--fast")

    print(f"🚀 Using Python: {python_exe}")
    print(f"🚀 Starting transcription for: {url}")
    print(f"📋 Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Transcription failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python transcribe_url.py <URL> [--engine engine] [--model model] [--fast]"
        )
        sys.exit(1)

    url = sys.argv[1]
    engine = "whisper"
    model = "large-v3"
    fast = False

    if "--engine" in sys.argv:
        engine = sys.argv[sys.argv.index("--engine") + 1]
    if "--model" in sys.argv:
        model = sys.argv[sys.argv.index("--model") + 1]
    if "--fast" in sys.argv:
        fast = True

    run_transcribe(url, engine, model, fast)
