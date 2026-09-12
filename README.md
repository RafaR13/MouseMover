# Mouse Mover

Small Windows app that moves the mouse every few seconds so the session does not look idle. It has a simple window (Start / Stop, interval) and a tray icon next to the clock.

Cloning this repo does **not** add the app to the Windows Start menu. You either double-click `MouseMover.exe` or run the Python script.

## Prerequisites

- **Windows 10 or 11** (the app uses the Windows mouse APIs)
- **Python 3.10+** on `PATH` (`python --version` should work in a terminal)

  Install from [python.org](https://www.python.org/downloads/). During setup, tick **Add python.exe to PATH**.

You only need Python if you want to run from source or rebuild the `.exe`. If someone already gave you `MouseMover.exe`, skip the rest and double-click it.

## Setup (from source)

```powershell
git clone <repo-url>
cd MouseMover
python -m pip install -r requirements.txt
```

That installs:

- `pystray` — tray icon
- `pillow` — tray icon image
- `pyinstaller` — only used when you build the `.exe`

### Run without building

```powershell
python mousemover.py
```

The app starts moving the mouse (default interval: 30 seconds). Closing the window hides it in the tray. Right-click the tray icon → **Sair** to quit.

### Build the `.exe`

From the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

The script:

1. Installs the packages in `requirements.txt`
2. Packs `mousemover.py` into a single windowed executable (no console)
3. Copies the result to `MouseMover.exe` in the project root

Then double-click `MouseMover.exe`. You can copy that file anywhere; Python is not required to run it.

To pin it to the Start menu, right-click `MouseMover.exe` → **Pin to Start**, or create a shortcut under:

`%AppData%\Microsoft\Windows\Start Menu\Programs\`
