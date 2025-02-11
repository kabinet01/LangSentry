# LangSentry

## Installation

```pip install mylangsentry```

## Usage

```python
from langsentry import some_function
result = some_function()
```

## Build

```bash
# Install build tools
pip install build

# Build your package
python -m build
```

## Install

```bash
cd langsentry
pip install . 
```

## Push to PyPip

```bash
python -m build
pip install twine
twine upload dist/*
```
