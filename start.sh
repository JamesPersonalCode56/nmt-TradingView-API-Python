#!/usr/bin/env bash
set -e

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate

if ! command -v poetry >/dev/null 2>&1; then
  python -m pip install --upgrade pip
  python -m pip install poetry
fi

poetry install