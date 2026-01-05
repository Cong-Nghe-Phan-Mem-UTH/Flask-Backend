#!/bin/bash
# Script to fix encoding - automatically activates venv

cd "$(dirname "$0")/../src"
source .venv/bin/activate
cd ..
python3 scripts/fix_encoding.py


