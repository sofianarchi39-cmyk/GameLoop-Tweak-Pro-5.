# GameLoop Tweak Starter

A beginner-friendly, open-source Windows GUI project for people learning to build a **GameLoop / PUBG Mobile performance utility**.

## Current features
- Detects common GameLoop-related processes if they are running.
- Displays the active Windows power plan, logical CPU processor count, and installed RAM.
- Lets the user explicitly activate the **High Performance** Windows power plan, only if it already exists.
- Backs up the previous power plan and lets the user restore it.
- Uses Python standard library only (Tkinter included in standard Windows Python distributions).

**Safety:** Does not change GameLoop/PUBG files, emulator memory, Windows registry, drivers, or anti-cheat settings. It does not promise an FPS increase.

## Requirements
- Windows 10 or 11.
- Python 3.10 or later installed from https://www.python.org/downloads/ (ensure Python is on PATH).

## Run it
In PowerShell, inside the project directory:

```powershell
python app.py
```

Or double-click `run.bat` on Windows if you have the Python launcher (`py`).

## Package into an .exe (on Windows)

```powershell
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name GameLoopTweakStarter app.py
```

The executable will be in `dist/GameLoopTweakStarter.exe`.

## Upload to GitHub
1. Create a repository named `GameLoop-Tweak-Starter` at https://github.com/new.
2. Choose **Add file > Upload files**.
3. Upload `app.py`, `README.md`, `.gitignore`, and `run.bat`.
4. Commit the changes. Do **not** upload `.venv`, `build`, `dist` or private files.
5. To share a compiled `.exe`, add it as an asset in a GitHub **Release** (rather than tracking binaries in the source code repository).

## Notes
- GameLoop process names can change between emulator releases; detection is best-effort.
- Some laptops use Modern Standby and do not expose the classic High Performance power plan. In that case this app will not modify anything.
- Windows administrator permission may be required by `powercfg` on some systems.
- On laptops, High Performance may increase heat/power consumption and is best tested while plugged in.
- The tool does not change PUBG's in-game graphics settings or force unsupported FPS limits.

## Proposed next upgrades
- Guided GameLoop graphics settings (OpenGL+/DirectX+), with links to official documentation.
- GPU preference instructions for Windows Settings.
- Benchmarking with **measured** frame rate data from an external compatible monitoring tool.
- Configurable profiles: Balanced / Performance, with full backup and rollback.
