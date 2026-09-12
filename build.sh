#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v powershell.exe >/dev/null 2>&1; then
  echo "Esta app usa APIs do Windows e deve ser empacotada com Python/PyInstaller no Windows."
  echo "Em WSL, instala o Python no Windows e corre este script novamente."
  exit 1
fi

if ! command -v wslpath >/dev/null 2>&1; then
  echo "Nao encontrei wslpath. Corre o build no Windows com:"
  echo "powershell -ExecutionPolicy Bypass -File .\\build.ps1"
  exit 1
fi

windows_project_path="$(wslpath -w "$PWD")"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${windows_project_path}\\build.ps1"
