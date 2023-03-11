import datetime
import json
import os
import warnings

from interface import Simulator as SimABC

from . import settings
from .state import State


class Simulator(SimABC):
    @classmethod
    def list_scenario_categories(cls) -> list[str]:
        """
        List the available scenario categories.
        """

        scenario_categories = os.listdir(settings.SCENARIO_DIR)
        scenario_categories.sort()

        return scenario_categories

    @classmethod
    def list_scenarios(cls, category: str) -> list[str]:
        """
        List the scenarios in a given category.
        """

        scenario_names = os.listdir(os.path.join(settings.SCENARIO_DIR, category))
        scenario_names.sort()

        return scenario_names

    @classmethod
    def scenario_info(cls, category: str, scenario_name: str) -> dict:
        """
        Get information about a specific scenario.
        """

        return {
            "category": category,
            "scenario_name": scenario_name,
            "meta": json.load(
                open(
                    os.path.join(
                        settings.SCENARIO_DIR, category, scenario_name, "meta.json"
                    )
                )
            ),
        }

    def __init__(self, category: str, scenario_name: str):
        """
        Initialise a simulation instance from a given scenario.
        """

        self.scenario_name = scenario_name
        self.state = State.load(
            os.path.join(settings.SCENARIO_DIR, category, scenario_name)
        )

    def evolve(self, delta: float) -> bool:
        """
        Increment the simulation by a given time delta (seconds).
        """

        if delta <= 0:
            raise ValueError("Time delta must be positive. Received: {}.", delta)

        self.state.evolve(datetime.timedelta(seconds=delta))

        return True

    def environment(self) -> dict:
        """
        Get the current environment state.
        """

        return {}

    def static_data(self) -> dict:
        """
        Get the static scenario data.
        """

        return {
            "scenario_name": self.scenario_name,
            "bay_names": self.state.bay_names,
            "fixes": [
                {"id": i, "name": name} | self.state.fixes.loc[name].to_dict()
                for i, name in enumerate(self.state.fixes.index)
            ],
        }

    def dynamic_data(self) -> dict:
        """
        Get the volatile scenario data.
        """

        return {
            "time": self.state.time,
            "aircraft": [
                {"id": i, "callsign": callsign}
                | self.state.aircraft.loc[callsign].to_dict()
                for i, callsign in enumerate(self.state.aircraft.index)
            ],
        }

    def action(self, actions: list[dict]) -> bool:
        """
        Perform an action.
        """

        for action in actions:
            # iterate through the list of dictionaries (actions) with action

            if action["kind"] == "flight_level":
                # if you find this key in any of the action dictionaries execute if statement
                self._delta_flight_level(action)
                # execute this function on the action dictionary
            elif action["kind"] in [
                "flight_level",
                "speed",
                "alt",
                "heading",
            ]:  # TODO: Replace "flight level?"
                callsign = action["callsign"]
                new_value = action["value"]
                self.state.aircraft.loc[(callsign, action["kind"])] = new_value
            else:
                warnings.warn(
                    f"Action: {action['kind']} is not yet implemented in this simulator."
                )

        return True

    def _delta_flight_level(self, action):
        """
        Change the altitude to the target altitude when flight_level specified in the action dictionary.

        Note: altitudes will still evolve to target altitudes, but when flight_level action specified,
        user-inputted target altitude will be aimed for.
        """
        print("IMPLEMENTING FLIGHT LEVEL ACTION")
        # print(action)

        callsign = action["callsign"]
        # callsign is now the callsign of the action that has flight_level included
        new_tar_flight_level = action["value"]
        # the target altitude is now the value indicated in the action dictionary of the action where flight_level included
        self.state.aircraft.loc[(callsign, "target_alt")] = new_tar_flight_level
        # changing the target altitude to the indicated value in the action dictionary
