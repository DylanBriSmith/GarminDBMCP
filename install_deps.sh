#!/usr/bin/env bash
set -euo pipefail

# Simple dependency installer for GarminDbMcp
# Usage:
#   bash install_deps.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install fastmcp prefab-ui python-dotenv

if ! command -v deno >/dev/null 2>&1; then
  echo "Installing Deno..."
  curl -fsSL https://deno.land/install.sh | sh
  export PATH="${HOME}/.deno/bin:${PATH}"
else
  echo "Deno already installed."
fi

echo "Done."
echo "Activate with: source \"${VENV_DIR}/bin/activate\""
