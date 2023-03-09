# Mockingbird - Example Simulator

<p align="center">
    <img src="resources/icons/mockingbird.svg" width="400" height="200" />
</p>

![digiLab](resources/badges/digilab.svg)
[![slack](https://img.shields.io/badge/slack-@digilabglobal-purple.svg?logo=slack)](https://digilabglobal.slack.com)

Python DataFrame-based ATC simulator.

## Table of Contents

- [Mockingbird - Example Simulator](#mockingbird---example-simulator)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Quickstart](#quickstart)
  - [Testing](#testing)

## Requirements

- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/docs/#installation)

## Quickstart

Clone the repository and `cd` into it:

```bash
git clone https://github.com/digiLab-ai/mockingbird-simulator.git
cd simulator
```

Copy the `.env.example` file to `.env` and fill out any missing values:

```bash
cp .env.example .env
open .env
```

Install the dependencies:

```bash
poetry install
```

Run the simulator:

```bash
poetry run python examples/run.py
```

Run from the top-level of the repository.

## Testing

Run the test suite with `pytest`:

```bash
poetry run pytest
```
