import ast
import datetime
import json
import os

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

    def environment(self, _sector_id: str) -> dict:
        """
        Get the current environment state.
        """

        return {}

    def static_data(self, _sector_id: str) -> dict:
        """
        Get the static scenario data.
        """

        sectors = {}
        for name, sector in self.state.sectors.iterrows():
            boundaries = []
            for vol in sector.airspace.vols:
                boundaries.append(vol["boundary"])
            sectors[name] = boundaries

        return {
            "scenario_name": self.scenario_name,
            "bay_names": self.state.bay_names,
            "sectors": sectors,
            "fixes": [
                {"id": i, "name": name} | self.state.fixes.loc[name].to_dict()
                for i, name in enumerate(self.state.fixes.index)
            ],
        }

    def dynamic_data(self, _sector_id: str) -> dict:
        """
        Get the volatile scenario data.
        """

        data = {
            "time": self.state.time.isoformat(sep=" "),
            "actions": [
                {"id": i, "time": f"{time}"} | self.state.actions.loc[time].to_dict()
                for i, time in enumerate(self.state.actions.index)
            ],
            "aircraft": [
                {"id": i, "callsign": callsign}
                | self.state.aircraft.loc[callsign].to_dict()
                for i, callsign in enumerate(self.state.aircraft.index)
            ],
        }

        for aircraft in data["aircraft"]:
            aircraft["route"] = ast.literal_eval(aircraft["route"])

            lats = [aircraft["lat"]]
            lons = [aircraft["lon"]]
            for n in range(5):
                lats.append(aircraft[f"lat_{n + 1}"])
                aircraft.pop(f"lat_{n + 1}")
                lons.append(aircraft[f"lon_{n + 1}"])
                aircraft.pop(f"lon_{n + 1}")
            aircraft["lats"] = lats
            aircraft["lons"] = lats

        return data

    def action(self, actions: list[dict]) -> bool:
        """
        Add actions to the queue.
        """
        self.state.queue_actions(actions)
        return True

    def update_aircraft_bay(self, _sector_id: str, callsign: str, bay_id: str) -> bool:
        """
        Move an aircraft to a different bay.
        """

        self.state.aircraft.loc[(callsign, "bay")] = bay_id
        return True
