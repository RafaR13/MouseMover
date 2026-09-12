#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v powershell.exe >/dev/null 2>&1; then
  echo "This app uses Windows APIs and must be packaged with Python/PyInstaller on Windows."
  echo "From WSL, install Python on Windows and run this script again."
  exit 1
fi

if ! command -v wslpath >/dev/null 2>&1; then
  echo "Could not find wslpath. Run the build on Windows with:"
  echo "powershell -ExecutionPolicy Bypass -File .\\build.ps1"
  exit 1
fi

windows_project_path="$(wslpath -w "$PWD")"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${windows_project_path}\\build.ps1"
