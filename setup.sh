#!/bin/bash
# Setup script for local environment

# Install Python 3.11 if not available via pyenv or system
if ! command -v python3.11 >/dev/null 2>&1; then
    echo "Python 3.11 not found. Install via pyenv or ensure system Python is 3.11" >&2
    # Example using pyenv
    if command -v pyenv >/dev/null 2>&1; then
        pyenv install 3.11.0 -s
        pyenv local 3.11.0
    fi
fi

python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt
