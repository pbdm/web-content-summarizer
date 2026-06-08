$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    foreach ($candidate in @("py", "python")) {
        try {
            & $candidate --version *> $null
            return $candidate
        } catch {
        }
    }

    throw "Python 3 is required and must be available as 'py' or 'python' in PATH."
}

Write-Host "Checking Python environment..."
$pythonCmd = Get-PythonCommand

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    & $pythonCmd -m venv venv
}

$venvPython = (Resolve-Path ".\venv\Scripts\python.exe").Path

Write-Host "Installing project dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
& $venvPython -m pip install imageio-ffmpeg

Write-Host "Configuring FFmpeg..."
New-Item -ItemType Directory -Force -Path ".\bin" | Out-Null
$ffmpegPath = (& $venvPython -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())").Trim()
Copy-Item $ffmpegPath ".\bin\ffmpeg.exe" -Force
Copy-Item $ffmpegPath ".\bin\ffprobe.exe" -Force

Write-Host "Setup complete."
Write-Host "PowerShell usage: .\venv\Scripts\python.exe .\src\main.py [URL]"
