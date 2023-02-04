# Mockingbird - Example Simulator

<p align="center">
    <img src="resources/icons/mockingbird.svg" width="400" height="200" />
</p>

Python DataFrame-based ATC simulator.

## Table of Contents

- [Mockingbird - Example Simulator](#mockingbird---example-simulator)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Quickstart](#quickstart)
  - [Testing](#testing)

## Requirements

-   [Python](https://www.python.org/)
-   [Poetry](https://python-poetry.org/docs/#installation)

## Quickstart

Change to the `simulator` directory:

```bash
cd simulator
```

Install the dependencies:

```bash
poetry install
```

Run the simulator:

```bash
poetry run python examples/run.py
```

## Testing

Run the test suite with `pytest`:

```bash
poetry run pytest
```
