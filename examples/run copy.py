import asyncio
import datetime
import time

from simulator import Simulator

UPDATE_PERIOD = 1.0  # Period between updates (seconds)
RATE_OF_TIME = 1.0  # Simulated seconds per wall-clock second

categories = Simulator.list_scenario_categories()
print(categories)
scenarios = Simulator.list_scenarios(categories[0])
print(scenarios)

sim = Simulator(categories[0], scenarios[0])


now = datetime.datetime.now()
for n in range(5):
    print(f"\n> {sim.state}")

    sim.evolve(UPDATE_PERIOD * RATE_OF_TIME)

    time.sleep(
        max(
            0.0,
            UPDATE_PERIOD
            - ((datetime.datetime.now() - now).microseconds / (UPDATE_PERIOD * 1e6)),
        )
    )

sim.action([
    {
        "callsign": "BAW123",
        "type": "flight_level",
        "subtype": "absolute",
        "value": 400
    },
    {
        "callsign": "BAW123",
        "type": "speed",
        "subtype": "absolute",
        "value": 200
    },
])

# while True:
#     print(f"\n< {sim.state}")

#     sim.evolve(UPDATE_PERIOD * RATE_OF_TIME)

#     time.sleep(
#         max(
#             0.0,
#             UPDATE_PERIOD
#             - ((datetime.datetime.now() - now).microseconds / (UPDATE_PERIOD * 1e6)),
#         )
#     )
