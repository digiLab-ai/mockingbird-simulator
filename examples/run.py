import datetime
import os
import time

from simulator import Simulator

UPDATE_PERIOD = 0.5  # Period between updates (seconds)
RATE_OF_TIME = 1.0  # Simulated seconds per wall-clock second

categories = Simulator.list_scenario_categories()
scenarios = Simulator.list_scenarios(categories[0])

sim = Simulator(categories[0], scenarios[1])
sim_start_time = sim.state.time


def iterate_forward_one_step(sim):
    """
    Increment the simulator forward in time by one UPDATE_PERIOD multiplied by the RATE_OF_TIME.
    If the calculation is performed faster than UPDATE_PERIOD, the thread will sleep for the remainder of the time.
    This means that the simulation will run at a rate of RATE_OF_TIME times wall-clock time, but may lag behind if the calculation of sim.evolve is slow.
    """
    now = datetime.datetime.now()
    state_str = sim.state.__str__()
    print("\n" * max(os.get_terminal_size().lines - state_str.count("\n"), 0))
    print(state_str)
    sim.evolve(UPDATE_PERIOD * RATE_OF_TIME)
    time.sleep(
        max(
            0.0,
            UPDATE_PERIOD
            - ((datetime.datetime.now() - now).microseconds / (UPDATE_PERIOD * 1e6)),
        )
    )


while sim.state.time < (sim_start_time + datetime.timedelta(seconds=5)):
    iterate_forward_one_step(sim)

print("Sending action")
sim.action(
    [
        {
            "time": "2019-01-01 00:00:10",
            "agent": "human",
            "callsign": "FLY456",
            "kind": "heading",
            "subkind": "absolute",
            "value": 45.0,
        }
    ],
)

while True:
    iterate_forward_one_step(sim)
