import datetime
import os
import time

from simulator import Simulator


def iterate_forward_one_step(sim, update_period, rate_of_time):
    """
    Increment the `sim` forward in time by one `update_period` multiplied by the `rate_of_time`.
    If the calculation is performed faster than `update_period`, the thread will sleep for the remainder of the time.
    This means that the simulation will run at a rate of `rate_of_time` times wall-clock time, but may lag behind if the calculation of `sim.evolve` is slow.
    """

    # We must time this function so we can run with wall clock time.
    now = datetime.datetime.now()

    # Display the current state of the simulator.
    display_state(sim.state)

    # Increment the simulator forward in time.
    sim.evolve(update_period * rate_of_time)

    # Sleep for the remainder of the step, if possible.
    remaining_time = update_period - (
        (datetime.datetime.now() - now).microseconds / (update_period * 1e6)
    )
    if remaining_time < 0:
        print("Warning: Simulator is running slower than wall-clock!")
    time.sleep(max(0.0, remaining_time))


def display_state(state, **kwargs):
    """
    Display the `state` of a simulator in a human-readable data tables.
    """

    # Flags for which parts of the state to display. Change default values here.
    time = kwargs.get("time", True)
    fixes = kwargs.get("fixes", False)
    sectors = kwargs.get("sectors", False)
    aircraft = kwargs.get("aircraft", True)
    actions = kwargs.get("actions", True)
    tick = kwargs.get("tick", True)
    all = kwargs.get("all", False)  # If True, display the complete state.
    clear = kwargs.get("clear", True)  # If True, clear the screen before printing.

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

    # Clear the screen and print the buffer.
    if clear:
        print("\n" * max(os.get_terminal_size().lines - buffer.count("\n"), 0))
    print(buffer)


if __name__ == "__main__":
    update_period = 0.5  # Period between updates (seconds)
    rate_of_time = 1.0  # Simulated seconds per wall-clock second

    categories = Simulator.list_scenario_categories()
    scenarios = Simulator.list_scenarios(categories[0])

    sim = Simulator(categories[0], scenarios[0])
    sim_start_time = sim.state.time

    # Run for 5 seconds
    while sim.state.time < (sim_start_time + datetime.timedelta(seconds=5)):
        iterate_forward_one_step(sim, update_period, rate_of_time)

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
                "value": "45.0",
            }
        ],
    )

    # Then keep running until the user presses Ctrl+C
    while True:
        iterate_forward_one_step(sim, update_period, rate_of_time)
