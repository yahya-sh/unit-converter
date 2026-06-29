# Units Converter

A Python library for unit conversions with CLI support.

## Module Architecture

```aiignore
                   ┌─────────────┐
                   │    USER     │
                   └──────┬──────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   CLI           │
                 │   (cli.py)      │
                 │   units-convert │
                 └────────┬────────┘
                          │
                          ▼
               ┌──────────────────────┐
               │  registry.py         │
               │  load_registry()     │
               └──────────┬───────────┘
                          │
                          ▼
               ┌──────────────────────┐
               │  converter.py        │
               │  ConversionGraph     │
               └──────────────────────┘
```

## Project Structure

```aiignore
.
├── README.md
├── pyproject.toml
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── system
│   │   ├── __init__.py
│   │   └── test_cli.py
│   ├── integration
│   │   ├── __init__.py
│   │   └── test_converter.py
│   └── unit
│       ├── __init__.py
│       ├── test_converter.py
│       ├── test_with_faker.py
│       └── test_with_hypothesis.py
└── uc
    ├── __init__.py
    ├── cli.py
    ├── converter.py
    ├── data
    │   └── <dimension>.yaml
    └── registry.py
```

new line

## Install

### Development

Install in editable mode with development dependencies

`pip install -e ".[dev]"`

### For End Users

`pip install .`

## Usage

### Command Line Interface

#### Basic unit conversion

`units-convert 100 cm m`

Output: 1.0

`units-convert 0 C F`

Output: 32.0
