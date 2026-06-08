# Windows Compatibility Design

## Goal

Make the project usable on Windows without breaking the existing Linux workflow.

## Scope

This change covers:

- a native Windows setup entrypoint via `setup.ps1`
- cross-platform Python execution guidance
- cross-platform FFmpeg executable discovery
- path handling that works on both Windows and Linux

This change does not cover:

- replacing the current CLI shape
- changing the summarization pipeline behavior
- packaging the project as an installable Python distribution

## Design

### 1. Setup entrypoints

Keep `setup.sh` for Linux users.

Add `setup.ps1` for Windows users. It will:

- find a usable Python interpreter
- create `venv` if it does not exist
- bootstrap or upgrade `pip` inside the virtual environment
- install `requirements.txt`
- install `imageio-ffmpeg`
- copy or link FFmpeg and FFprobe from `imageio_ffmpeg` into the local `bin` directory using Windows-friendly executable names

The Windows script should prefer straightforward file copying over symlink-only behavior because symlink creation is less reliable on default Windows setups.

### 2. Runtime command compatibility

The codebase and docs should stop assuming `./venv/bin/python3`.

Runtime guidance will become platform-aware:

- Linux: `./venv/bin/python3 src/main.py <URL>`
- Windows PowerShell: `.\venv\Scripts\python.exe .\src\main.py <URL>`

Python code should not depend on shell-specific path conventions.

### 3. FFmpeg resolution

The config layer should resolve executable names by platform:

- Linux/macOS: `ffmpeg`, `ffprobe`
- Windows: `ffmpeg.exe`, `ffprobe.exe`

Resolution order:

1. project-local `bin`
2. system `PATH`
3. fail with a clear error mentioning both locations

This keeps the behavior stable while removing the Linux-only filename assumption.

### 4. Path handling

Continue using `pathlib.Path` as the primary path abstraction.

Where prompts or docs currently hard-code Linux paths, switch to project-relative wording where possible so the instructions remain valid on both operating systems.

### 5. Verification

Verify these behaviors after implementation:

- `src/config.py` loads successfully on Windows
- FFmpeg lookup works with Windows executable names
- the CLI help command runs from the Windows virtual environment path
- Linux setup script remains present and aligned with the updated assumptions

## Risks and mitigations

- `setup.ps1` may fail on machines without Python in `PATH`.
  - Mitigation: emit a clear error with the expected install prerequisite.
- FFmpeg linking behavior differs across filesystems and shells.
  - Mitigation: Windows uses copy-first behavior; Linux keeps symlink behavior.
- Existing docs may still mention Linux-only commands.
  - Mitigation: update the main setup and usage surfaces in this change.

## Recommended implementation order

1. update config and runtime assumptions in Python
2. add `setup.ps1`
3. refresh setup and usage documentation
4. run Windows-oriented verification
