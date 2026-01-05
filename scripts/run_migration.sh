#!/bin/bash
# Script to run migration

cd "$(dirname "$0")/../src"
source .venv/bin/activate
cd ..
python3 scripts/migrate_data.py


