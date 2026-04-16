import subprocess
import sys
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.absolute()
BILINOTES_DIR = Path("/mnt/c/code/others/content/BiliNotes")
WEBNOTES_DIR = Path("/mnt/c/code/others/content/WebNotes")


def detect_url_type(url: str) -> str:
    """检测 URL 类型：bilibili, pdf, web"""
    if "bilibili.com" in url:
        return "bilibili"
    if url.lower().endswith(".pdf"):
        return "pdf"
    return "web"


def extract_bvid(url: str) -> str | None:
    match = re.search(r"BV[\w]{10}", url, re.IGNORECASE)
    return match.group(0).upper() if match else None


def run_bilibili(url, engine="whisper", model="large-v3", fast=False):
    """B站视频转录"""
    venv_python = PROJECT_ROOT / "venv" / "bin" / "python3"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable
    main_py = PROJECT_ROOT / "src" / "main.py"

    cmd = [python_exe, str(main_py), url, "--engine", engine]
    if model:
        cmd.extend(["--model", model])
    if fast:
        cmd.append("--fast")

    print(f"🚀 Using Python: {python_exe}")
    print(f"📋 Command: {' '.join(cmd)}")

    subprocess.run(cmd, check=True)


def run_web_fetch(url: str):
    """网页/PDF 内容提取"""
    import urllib.request
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from utils import sanitize_filename

    BILINOTES_DIR.mkdir(parents=True, exist_ok=True)
    WEBNOTES_DIR.mkdir(parents=True, exist_ok=True)

    if url.lower().endswith(".pdf"):
        print(f"📄 Processing PDF: {url}")
        # PDF 模式
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()
                output = WEBNOTES_DIR / f"downloaded_{Path(url).name}"
                output.write_bytes(content)
                print(f"✅ PDF saved to: {output}")
        except Exception as e:
            print(f"❌ PDF fetch failed: {e}")
    else:
        print(f"🌐 Processing web page: {url}")
        # 使用 defuddle 或 web_fetch
        from defuddle import main as defuddle_main

        try:
            result = defuddle_main.parse_url(url, format="markdown")
            if result and len(result) > 500:
                title_match = re.search(r"<title>(.*?)</title>", result, re.I)
                title = title_match.group(1)[:50] if title_match else "untitled"
                safe_title = sanitize_filename(title)
                output = WEBNOTES_DIR / f"{safe_title}.md"
                output.write_text(result)
                print(f"✅ Web page saved to: {output}")
            else:
                print("⚠️ defuddle failed, trying web_fetch...")
                raise Exception("Need fallback")
        except Exception:
            # 回退到 web_fetch
            from webfetch import main as wf

            result = wf.fetch_url(url, format="markdown")
            if result:
                title_match = re.search(r"<title>(.*?)</title>", result, re.I)
                title = title_match.group(1)[:50] if title_match else "untitled"
                safe_title = sanitize_filename(title)
                output = WEBNOTES_DIR / f"{safe_title}.md"
                output.write_text(result)
                print(f"✅ Web page saved to: {output}")
            else:
                print("❌ Both defuddle and web_fetch failed")


def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe_url.py <URL> [options]")
        print("Options:")
        print("  --engine whisper|funasr  (default: whisper)")
        print("  --model MODEL        (default: large-v3)")
        print("  --fast              high performance mode")
        sys.exit(1)

    url = sys.argv[1]
    engine = "whisper"
    model = "large-v3"
    fast = False

    if "--engine" in sys.argv:
        idx = sys.argv.index("--engine") + 1
        if idx < len(sys.argv):
            engine = sys.argv[idx]
    if "--model" in sys.argv:
        idx = sys.argv.index("--model") + 1
        if idx < len(sys.argv):
            model = sys.argv[idx]
    if "--fast" in sys.argv:
        fast = True

    url_type = detect_url_type(url)
    print(f"🔍 Detected URL type: {url_type}")

    if url_type == "bilibili":
        run_bilibili(url, engine, model, fast)
    else:
        run_web_fetch(url)


if __name__ == "__main__":
    main()
