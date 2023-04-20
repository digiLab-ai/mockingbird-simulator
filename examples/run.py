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
    sim.state.display(clear=True, sectors=True)

    # Increment the simulator forward in time.
    sim.evolve(update_period * rate_of_time)

    # Sleep for the remainder of the step, if possible.
    remaining_time = update_period - (
        (datetime.datetime.now() - now).microseconds / (update_period * 1e6)
    )
    if remaining_time < 0:
        print("Warning: Simulator is running slower than wall-clock!")
    time.sleep(max(0.0, remaining_time))


if __name__ == "__main__":
    # Set the parameters of the simulation
    update_period = 0.5  # Period between updates (seconds)
    rate_of_time = 1.0  # Simulated seconds per wall-clock second

    # Load the first scenario
    categories = Simulator.list_scenario_categories()
    scenarios = Simulator.list_scenarios(categories[0])
    sim = Simulator(categories[0], scenarios[0])

    import json

    print(json.dumps(sim.static_data(), indent=4))

    # # Run for 5 seconds
    # sim_start_time = sim.state.time
    # while sim.state.time < (sim_start_time + datetime.timedelta(seconds=5)):
    #     iterate_forward_one_step(sim, update_period, rate_of_time)

    # # Then send an action from an agent
    # print("Sending action")
    # sim.action(
    #     [
    #         {
    #             "time": "2019-01-01 00:00:10",
    #             "agent": "human",
    #             "callsign": "FLY456",
    #             "kind": "heading",
    #             "subkind": "absolute",
    #             "value": "45.0",
    #         }
    #     ],
    # )

    # # Then keep running until the user presses Ctrl+C
    # while True:
    #     iterate_forward_one_step(sim, update_period, rate_of_time)
