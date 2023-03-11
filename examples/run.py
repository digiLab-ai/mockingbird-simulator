import datetime
import time

from simulator import Simulator

UPDATE_PERIOD = 1.0  # Period between updates (seconds)
RATE_OF_TIME = 6.0  # Simulated seconds per wall-clock second

categories = Simulator.list_scenario_categories()
scenarios = Simulator.list_scenarios(categories[0])

sim = Simulator(categories[0], scenarios[0])


def iterate_forward_one_step(sim):
    """
    Increment the simulator forward one step.
    """
    now = datetime.datetime.now()
    print(f"\n> {sim.state}")
    sim.evolve(UPDATE_PERIOD * RATE_OF_TIME)
    time.sleep(
        max(
            0.0,
            UPDATE_PERIOD
            - ((datetime.datetime.now() - now).microseconds / (UPDATE_PERIOD * 1e6)),
        )
    )


for n in range(5):
    iterate_forward_one_step(sim)

print("Sending action")
sim.action(
    [
        {
            "callsign": "BAW123",
            "kind": "flight_level",
            "subkind": "absolute",
            "value": 140,
        },
        {"callsign": "FLY456", "kind": "speed", "subkind": "absolute", "value": 200},
    ]
)

while True:
    iterate_forward_one_step(sim)
