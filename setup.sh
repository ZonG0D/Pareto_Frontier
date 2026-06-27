#!/bin/bash
set -e

echo "[*] Setting up Pareto Frontier environment..."

# 1. Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "[*] Virtual environment already exists."
fi

# 2. Upgrade pip inside the venv
echo "[*] Upgrading pip..."
./.venv/bin/pip install --upgrade pip

# 3. Install dependencies
# We'll prioritize a requirements.txt if it exists, otherwise use defaults.
if [ -f "requirements.txt" ]; then
    echo "[*] Installing dependencies from requirements.txt..."
    ./.venv/bin/pip install -r requirements.txt
else
    echo "[*] No requirements.txt found. Installing default packages: pyyaml, python-dotenv, requests..."
    ./.venv/bin/pip install pyyaml python-dotenv requests
fi

# 4. Ensure all shell scripts are executable
if [ -d "core/runtime" ]; then
    echo "[*] Setting execution permissions for core/runtime/*.sh..."
    chmod +x core/runtime/*.sh
else
    echo "[ERROR] Directory 'core/runtime' not found!"
    exit 1
fi

# 5. Finalize setup
echo "[SUCCESS] Setup complete. To activate the environment, run: source .venv/bin/activate"
