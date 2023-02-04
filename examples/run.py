import asyncio
import datetime
import time

from simulator import Simulator

UPDATE_PERIOD = 1.0  # Period between updates (seconds)
RATE_OF_TIME = 1.0  # Simulated seconds per wall-clock second

categories = Simulator.list_scenario_categories()
scenarios = Simulator.list_scenarios(categories[0])

sim = Simulator(categories[0], scenarios[0])


now = datetime.datetime.now()
while True:
    print(f"\n{sim.state}")

    sim.evolve(UPDATE_PERIOD * RATE_OF_TIME)

    time.sleep(
        max(
            0.0,
            UPDATE_PERIOD
            - ((datetime.datetime.now() - now).microseconds / (UPDATE_PERIOD * 1e6)),
        )
    )
