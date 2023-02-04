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
  - [Overview](#overview)
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

## Overview

`Mockingbird` aims to be a realistic air traffic control simulator operating over `Pandas` DataFrames.

```python
import mockingbird as mb
```

The state of a scenario is stored as a collection of `.csv` and `.json` files on disk.
You can initialise a Python `State` object by targeting a directory containing these files:

```python
state = mb.State.load("resources/scenarios/Mission_1")
```

A `State` object represents the entire physical world of the scenario at a single instance in time and can be evolved forward in time using the `State.evolve(time_delta)` method:

```python
while True:
    print(state)
    state.evolve(STEP_TIME)
```

## Testing

Run the test suite with `pytest`:

```bash
poetry run pytest
```
