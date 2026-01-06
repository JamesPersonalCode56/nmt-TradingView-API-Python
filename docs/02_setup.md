# 02 - Setup

## Requirements

- Python 3.9 or newer
- Network access to TradingView endpoints

## Virtual environment + Poetry

A local venv is recommended to avoid global package conflicts.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install poetry
poetry install
```

If you already have a venv and want Poetry to use it:

```bash
POETRY_VIRTUALENVS_CREATE=false poetry install
```

## Environment variables

Some features need authentication:

- `SESSION` : sessionid cookie value
- `SIGNATURE` : sessionid_sign cookie value

You can obtain these from TradingView web login.

