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


def display_state(state, **kwargs):
    """
    Display the state of the simulator in a human-readable data tables.
    """

    time = kwargs.get("time", True)
    fixes = kwargs.get("fixes", False)
    sectors = kwargs.get("sectors", False)
    aircraft = kwargs.get("aircraft", True)
    actions = kwargs.get("actions", True)
    tick = kwargs.get("tick", True)
    all = kwargs.get("all", False)

    width = os.get_terminal_size().columns
    buffer = " STATE ".center(width, "=") + "\n"

    if time or all:
        buffer += f"{state.time}".center(width, " ") + "\n"

    if fixes or all:
        buffer += " fixes ".center(width, "-") + "\n"
        buffer += f"{state.fixes}\n"

    if sectors or all:
        buffer += " sectors ".center(width, "-") + "\n"
        buffer += f"{state.sectors}\n"

    if actions or all:
        buffer += " actions ".center(width, "-") + "\n"
        buffer += f"{state.actions}\n"

    if aircraft or all:
        buffer += " aircraft ".center(width, "-") + "\n"
        buffer += f"{state.aircraft}\n"

    if tick or all:
        buffer += "".center(width, "-") + "\n"
        buffer += f"{state.tick}".center(width, " ") + "\n"

    buffer += "".center(width, "=")

    print("\n" * max(os.get_terminal_size().lines - buffer.count("\n"), 0))
    print(buffer)


def iterate_forward_one_step(sim):
    """
    Increment the simulator forward in time by one UPDATE_PERIOD multiplied by the RATE_OF_TIME.
    If the calculation is performed faster than UPDATE_PERIOD, the thread will sleep for the remainder of the time.
    This means that the simulation will run at a rate of RATE_OF_TIME times wall-clock time, but may lag behind if the calculation of sim.evolve is slow.
    """
    now = datetime.datetime.now()
    display_state(sim.state)
    sim.evolve(UPDATE_PERIOD * RATE_OF_TIME)
    time.sleep(
        max(
            0.0,
            UPDATE_PERIOD
            - ((datetime.datetime.now() - now).microseconds / (UPDATE_PERIOD * 1e6)),
        )
    )


if __name__ == "__main__":
    # Run for 5 seconds
    while sim.state.time < (sim_start_time + datetime.timedelta(seconds=5)):
        iterate_forward_one_step(sim)

    # Then send an action from an agent
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

    # Then keep running until the user presses Ctrl+C
    while True:
        iterate_forward_one_step(sim)
