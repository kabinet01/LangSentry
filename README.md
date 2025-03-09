# LangSentry

LangSentry (Language Model Sentry) is a comprehensive security solution designed to detect and prevent prompt injection attacks in Large Language Model (LLM) applications. It consists of two main components:

1. LangSentry Package - Core security module
2. LangSentry WebApp - Interactive demonstration platform

## Features

- Input Sanitization
- Semantic Analysis
- Canary Token Detection
- Misinformation Detection
- Output Manipulation Protection
- AI-Powered Analysis

## LangSentry Package

### Installation

```bash
cd langsentry_package
pip install .
```

```bash
cd langsentry_webapp
pip install -r requirements.txt
```

## Run

1. Get an API key from https://makersuite.google.com/
2. Copy the API key into config.py and put it in the `langsentry_webapp` folder

```bash
python3 app.py
```

The langsentry_webapp imports and utlize the langsentry python
