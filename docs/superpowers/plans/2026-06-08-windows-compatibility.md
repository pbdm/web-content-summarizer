# Windows Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the project runnable on Windows with a native PowerShell setup flow while preserving the existing Linux workflow.

**Architecture:** Keep the current CLI and pipeline intact, but centralize platform-specific behavior in configuration and setup entrypoints. Use a new Windows setup script for environment bootstrapping, make Python executable lookup cross-platform, and replace Linux-only documentation and path assumptions with platform-aware behavior.

**Tech Stack:** Python, PowerShell, Bash, `pathlib`, `yt-dlp`, `imageio-ffmpeg`, `pytest`

---

### Task 1: Make runtime configuration cross-platform

**Files:**
- Modify: `src/config.py`
- Modify: `src/transcribe_url.py`

- [ ] **Step 1: Add a helper in `src/config.py` that resolves executable names by platform**

```python
import os
import shutil
import sys
from pathlib import Path


def get_platform_executable_name(name: str) -> str:
    return f"{name}.exe" if os.name == "nt" else name
```

- [ ] **Step 2: Update FFmpeg discovery in `src/config.py` to check project `bin` first, then `PATH`, using the platform-specific executable name**

```python
def find_ffmpeg(name: str) -> Path:
    executable_name = get_platform_executable_name(name)
    candidate = BIN_DIR / executable_name
    if candidate.exists():
        return candidate

    system_path = shutil.which(executable_name) or shutil.which(name)
    if system_path:
        return Path(system_path)

    raise FileNotFoundError(
        f"{executable_name} not found in {BIN_DIR} or system PATH"
    )
```

- [ ] **Step 3: Add a cross-platform virtualenv Python resolver in `src/transcribe_url.py`**

```python
def resolve_venv_python() -> Path:
    candidates = [
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / "venv" / "bin" / "python3",
        PROJECT_ROOT / "venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)
```

- [ ] **Step 4: Use that resolver in `run_bilibili()` and keep the rest of the subprocess contract unchanged**

```python
python_exe = str(resolve_venv_python())
cmd = [python_exe, str(main_py), url, "--engine", engine]
```

- [ ] **Step 5: Run a narrow import/help verification**

Run: `python -c "import src.config; print(src.config.FFMPEG_PATH.name)"`
Expected: prints an FFmpeg executable name without import failure

Run: `python .\src\transcribe_url.py`
Expected: usage output, not a path resolution crash

### Task 2: Add a Windows-native setup entrypoint

**Files:**
- Create: `setup.ps1`

- [ ] **Step 1: Create `setup.ps1` to find Python, create `venv`, install dependencies, and provision FFmpeg**

```powershell
$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    foreach ($candidate in @("py", "python")) {
        try {
            & $candidate --version *> $null
            return $candidate
        } catch {}
    }
    throw "Python 3 is required and must be available as 'py' or 'python'."
}
```

- [ ] **Step 2: Add venv creation and pip bootstrapping in `setup.ps1`**

```powershell
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    & $pythonCmd -m venv venv
}

$venvPython = Resolve-Path ".\venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
```

- [ ] **Step 3: Add dependency install and FFmpeg copy logic in `setup.ps1`**

```powershell
& $venvPython -m pip install -r requirements.txt
& $venvPython -m pip install imageio-ffmpeg

$ffmpegPath = & $venvPython -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
New-Item -ItemType Directory -Force -Path ".\bin" | Out-Null
Copy-Item $ffmpegPath ".\bin\ffmpeg.exe" -Force
Copy-Item $ffmpegPath ".\bin\ffprobe.exe" -Force
```

- [ ] **Step 4: Run the setup script on this Windows checkout**

Run: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`
Expected: `venv` created or reused, dependencies installed, and `bin\ffmpeg.exe` present

### Task 3: Align Linux setup and user-facing docs with the new cross-platform model

**Files:**
- Modify: `setup.sh`
- Modify: `SKILL.md`
- Modify: `AGENTS.md`
- Modify: `PROMPT.md`
- Modify: `paths.json`

- [ ] **Step 1: Update `setup.sh` to use a more portable pip bootstrap/install flow while preserving Linux behavior**

```bash
if [ ! -d "venv" ]; then
    "$PYTHON_EXE" -m venv venv
fi

./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -m pip install imageio-ffmpeg
```

- [ ] **Step 2: Replace Linux-only command examples in docs with platform-aware examples**

```text
Linux: ./venv/bin/python src/main.py <URL>
Windows PowerShell: .\venv\Scripts\python.exe .\src\main.py <URL>
```

- [ ] **Step 3: Replace Linux-only absolute project references with project-relative wording where possible**

```text
Read `PROMPT.md` from the project root before generating notes.
```

- [ ] **Step 4: Make the sample `OUTPUT_DIR` in `paths.json` project-local by default so a fresh Windows clone does not point at a missing WSL path**

```json
{
  "OUTPUT_DIR": "output",
  "TEMP_DIR": "temp"
}
```

- [ ] **Step 5: Re-open the edited docs and confirm they no longer require Linux-only paths to understand basic setup**

Run: `rg "/mnt/c|/home/|./venv/bin/python3" SKILL.md PROMPT.md AGENTS.md setup.sh paths.json`
Expected: no remaining required Linux-only usage guidance, or only explicitly Linux-scoped examples

### Task 4: Verify the Windows workflow and guard against regressions

**Files:**
- Test: `setup.ps1`
- Test: `src/config.py`
- Test: `src/transcribe_url.py`
- Test: `setup.sh`

- [ ] **Step 1: Run the Windows setup script**

Run: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`
Expected: successful completion message

- [ ] **Step 2: Verify the new virtualenv path and CLI help**

Run: `.\venv\Scripts\python.exe .\src\main.py --help`
Expected: argparse help output

Run: `.\venv\Scripts\python.exe .\src\transcribe_url.py`
Expected: usage output

- [ ] **Step 3: Verify FFmpeg discovery from the project bin directory**

Run: `.\venv\Scripts\python.exe -c "import src.config as c; print(c.FFMPEG_PATH); print(c.FFPROBE_PATH)"`
Expected: paths under the project `bin` directory or valid system paths

- [ ] **Step 4: Verify Python sources still compile**

Run: `.\venv\Scripts\python.exe -m compileall src`
Expected: compilation completes without syntax errors

- [ ] **Step 5: Commit**

```bash
git add setup.ps1 setup.sh paths.json src/config.py src/transcribe_url.py SKILL.md AGENTS.md PROMPT.md docs/superpowers/specs/2026-06-08-windows-compatibility-design.md docs/superpowers/plans/2026-06-08-windows-compatibility.md
git commit -m "feat: add Windows setup support"
```
