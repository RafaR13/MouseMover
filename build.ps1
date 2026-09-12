$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m pip install -r requirements.txt
python make_icon.py
python -m PyInstaller --noconfirm --clean --onefile --windowed --name MouseMover --icon icon.ico --add-data "icon.ico;." --collect-all pystray mousemover.py

Copy-Item -Force "dist\MouseMover.exe" "MouseMover.exe"
Write-Host "Pronto: $PSScriptRoot\MouseMover.exe"
