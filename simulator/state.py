import datetime
import json
import os
import pathlib

# import numpy as np # TODO: Remove because not used
import pandas as pd
import pyproj

from . import settings
from .airspace import Airspace


class State:
    """
    Complete description world state, at a single instance in time.
    """

    geod = pyproj.Geod(ellps="WGS84")

    def __init__(self, time: datetime.datetime):
        """
        Initialise a new simulation.
        """

        self.time = time  # Current time
        self.tick = 0  # Number of times the simulation has been ticked forward one settings.TIME_STEP_DELTA
        self.extra_time = datetime.timedelta(
            0
        )  # Difference in time between total calls to evolve, and the state that has been actually ticked forward
        self.bay_names = ["INCOMM", "OUTCOMM"]
        self.fixes = pd.DataFrame(  # Names locations in the simulation
            {
                "lat": pd.Series(dtype="float"),  # Degrees North/South
                "lon": pd.Series(dtype="float"),  # Degrees East/West
            },
            dtype="str",
        )
        self.sectors = pd.DataFrame(  # Regions of controlled airspace
            {
                "agent": pd.Series(dtype="str"),  # Agent controlling the sector
                "airspace": pd.Series(dtype="object"),  # Airspace boundary
            },
            dtype="str",
        )
        self.aircraft = pd.DataFrame(  # Flying machines in the simulation
            {
                "type": pd.Series(dtype="str"),  # Vortex type of aircraft
                "agent": pd.Series(dtype="str"),  # Agent controlling the aircraft
                "bay": pd.Series(dtype="str"),  # Bay to hold the aircraft strip
                "lat": pd.Series(dtype="float"),  # Degrees North/South
                "lon": pd.Series(dtype="float"),  # Degrees East/West
                "flight_level": pd.Series(dtype="float"),  # Flight level
                "target_flight_level": pd.Series(dtype="float"),  # Target flight level
                "heading": pd.Series(dtype="float"),  # Degrees clockwise from North
                "target_heading": pd.Series(
                    dtype="float"
                ),  # Degrees clockwise from North
                "speed": pd.Series(dtype="float"),  # Knots
                "target_speed": pd.Series(dtype="float"),  # Knots
                "rise": pd.Series(
                    dtype="float"
                ),  # Flight levels per second (absolute value)
                "max_rise_rate": pd.Series(
                    dtype="float"
                ),  # Maximum rate of rise and fall (flight_levels per second)
                "turn": pd.Series(dtype="float"),  # Degrees clockwise per second
                "max_turn_rate": pd.Series(
                    dtype="float"
                ),  # Maximum rate of turn (degrees per second)
                "acceleration": pd.Series(dtype="float"),  # Knots
                "max_acceleration": pd.Series(dtype="float"),  # Knots
                "route": pd.Series(dtype="object"),  # List of fixes to route through
            },
            dtype="str",
        )
        self.actions = pd.DataFrame(
            columns=["time", "agent", "callsign", "kind", "subkind", "value"],
            index=pd.to_datetime([]),
        )

    def display(self, **kwargs):
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
            buffer += f"{self.time}".center(width, " ") + "\n"

        if fixes or all:
            buffer += " fixes ".center(width, "-") + "\n"
            buffer += f"{self.fixes}\n"

        if sectors or all:
            buffer += " sectors ".center(width, "-") + "\n"
            buffer += f"{self.sectors}\n"

        if actions or all:
            buffer += " actions ".center(width, "-") + "\n"
            buffer += f"{self.actions}\n"

        if aircraft or all:
            buffer += " aircraft ".center(width, "-") + "\n"
            buffer += f"{self.aircraft}\n"

        if tick or all:
            buffer += "".center(width, "-") + "\n"
            buffer += f"{self.tick}".center(width, " ") + "\n"

        buffer += "".center(width, "=")

        # Clear the screen and print the buffer.
        if clear:
            print("\n" * max(os.get_terminal_size().lines - buffer.count("\n"), 0))
        print(buffer)

    @staticmethod
    def load(scenario_dir: str):
        """
        Initialise a simulation from a saved state.
        """

        scenario_dir = pathlib.Path(scenario_dir)

        with open(os.path.join(scenario_dir, "meta.json")) as file:
            meta = json.load(file)
            start_time = datetime.datetime.strptime(
                meta["start_time"], settings.TIME_FORMAT
            )
        state = State(start_time)

        state._load_fixes(os.path.join(scenario_dir, "fixes.csv"))
        state._load_sectors(os.path.join(scenario_dir, "sectors.json"))
        state._load_aircraft(os.path.join(scenario_dir, "aircraft.csv"))
        state._load_actions(os.path.join(scenario_dir, "actions.csv"))

        return state

    def _load_fixes(self, file_path: str):
        """
        Load fixes state from a .csv file.
        Note this will replace the current fixes state.
        """

        with open(file_path) as file:
            fixes = pd.read_csv(file, index_col=0, skipinitialspace=True)

            # Check column headings match
            if set(self.fixes.columns) != set(fixes.columns):
                print(f"Expected headings: {self.fixes.columns}")
                print(f"Given headings: {fixes.columns}")
                raise ValueError(
                    f"Column headings for fixes dataframe differ to those expected"
                )

        self.fixes = fixes
        self.bay_names = ["INCOMM"] + fixes.index.tolist() + ["OFFCOMM"]

    def _load_sectors(self, file_path: str):
        """
        Load sector state from a .json file.
        Note this will replace the current sector state.
        """

        # Clear the current sectors
        self.sectors = pd.DataFrame(columns=self.sectors.columns)
        with open(file_path) as file:
            for name, data in json.load(file).items():
                self.sectors.loc[name] = [
                    data["agent"],
                    Airspace(data["vols"]),
                ]

    def _load_aircraft(self, file_path: str):
        """
        Load aircraft state from a .csv file.
        Note this will replace the current aircraft state.
        """

        with open(file_path) as file:
            aircraft = pd.read_csv(file, index_col=0, skipinitialspace=True)

            # Check column headings match
            if set(self.aircraft.columns) != set(aircraft.columns):
                print(f"Expected headings: {self.aircraft.columns}")
                print(f"Given headings: {aircraft.columns}")
                raise ValueError(
                    f"Column headings for aircraft dataframe differ to those expected"
                )

        self.aircraft = aircraft

    def _load_actions(self, file_path: str):
        """
        Load action state from a .csv file.
        Note this will replace the current action state.
        """

        with open(file_path) as file:
            actions = pd.read_csv(file, skipinitialspace=True)

        # Check column headings match
        if set(self.actions.columns) != set(actions.columns):
            print(f"Expected headings: {self.actions.columns}")
            print(f"Given headings: {actions.columns}")
            raise ValueError(
                f"Column headings for actions dataframe differ to those expected"
            )
        actions["time"] = pd.to_datetime(actions["time"], format=settings.TIME_FORMAT)
        actions = actions.set_index("time")

        self.actions = actions

    def add_aircraft(
        self,
        callsign: str,
        agent: str,
        lat: float,
        lon: float,
        flight_level: float,
        target_flight_level: float,
        heading: float,
        target_heading: float,
        speed: float,
        target_speed: float,
        rise: float,
        max_rise_rate: float,
        turn: float,
        max_turn_rate: float,
        acceleration: float,
        max_acceleration: float,
    ):
        """
        Add an aircraft to the simulation.
        """

        if callsign in self.aircraft.index:
            raise ValueError(f"Aircraft {callsign} already exists")

        self.aircraft.loc[callsign] = [
            agent,
            lat,
            lon,
            flight_level,
            target_flight_level,
            heading,
            target_heading,
            speed,
            target_speed,
            rise,
            max_rise_rate,
            turn,
            max_turn_rate,
            acceleration,
            max_acceleration,
        ]

    def remove_aircraft(self, callsign: str):
        """
        Remove an aircraft from the simulation.
        """

        if callsign not in self.aircraft.index:
            raise ValueError(f"Aircraft {callsign} does not exist")

        self.aircraft.drop(callsign, inplace=True)

    def queue_actions(self, actions: list[dict]):
        """
        Add a list of actions to the the queue.
        """

        for action in actions:
            # Remove time from action and convert to datetime for indexing
            time = datetime.datetime.strptime(action.pop("time"), settings.TIME_FORMAT)

            # Convert values to correct types
            if action["kind"] in ["flight_level", "heading", "speed"]:
                if action["subkind"] == "absolute":
                    action["value"] = float(action["value"])

            # Add action to queue
            self.actions = pd.concat([self.actions, pd.DataFrame(action, index=[time])])

    def evolve(self, evolve_delta: datetime.timedelta):
        """
        Evolve the simulation by a given time delta.
        """

        if evolve_delta < datetime.timedelta(seconds=0):
            raise ValueError(f"Evolve delta must be positive")

        evolve_delta -= self.extra_time
        num_steps = int(evolve_delta / settings.TIME_STEP_DELTA)
        if (num_steps * settings.TIME_STEP_DELTA) < evolve_delta:
            num_steps += 1
        self.extra_time = (num_steps * settings.TIME_STEP_DELTA) - evolve_delta

        for _ in range(num_steps):
            self._process_action_queue(settings.TIME_STEP_DELTA)
            self._rotate_aircraft(settings.TIME_STEP_DELTA)
            self._accelerate_aircraft(settings.TIME_STEP_DELTA)
            self._move_aircraft_laterally(settings.TIME_STEP_DELTA)
            self._move_aircraft_vertically(settings.TIME_STEP_DELTA)
            self.time += settings.TIME_STEP_DELTA
            self.tick += 1

    def _process_action_queue(self, time_delta: datetime.timedelta):
        """
        Find the actions in the queue that are due to be processed.
        """

        actions = self.actions.loc[
            (self.actions.index >= self.time)
            & (self.actions.index < (self.time + settings.TIME_STEP_DELTA))
        ]

        for _, action in actions.iterrows():
            self._handle_action(action)

    def _handle_action(self, action: dict):
        """
        Perform the given action.
        """

        kind = action["kind"]
        subkind = action["subkind"]
        callsign = action["callsign"]
        value = action["value"]

        if kind in [
            "flight_level",
            "speed",
            "heading",
        ]:
            if subkind == "absolute":
                new_target = float(value)
                self.aircraft.loc[(callsign, f"target_{kind}")] = new_target
                return
            elif subkind == "relative":
                new_target = self.aircraft.loc[(callsign, f"target_{kind}")] + float(
                    value
                )
                if kind == "bearing" and new_target < 0.0:
                    new_target += 360.0
                self.aircraft.loc[(callsign, f"target_{kind}")] = new_target
                return

        if kind == "bay":
            if subkind == "move":
                self.aircraft.loc[(callsign, "bay")] = action["value"]
                return

        if kind == "select_aircraft":
            return

        raise ValueError(
            f"Don't know how to handle {action['kind']}-{action['subkind']} action."
        )

    def _accelerate_aircraft(self, time_delta: datetime.timedelta):
        """
        Evolve the speed of the aircraft.
        """

        dt = time_delta.total_seconds()

        def accelerate_aircraft_helper(aircraft):
            aircraft["acceleration"] = (
                calc_sign(aircraft["speed"], aircraft["target_speed"], 10.0)
                * aircraft["max_acceleration"]
            )
            return pd.Series(aircraft)

        self.aircraft = self.aircraft.apply(accelerate_aircraft_helper, axis=1)

        self.aircraft["speed"] += (
            self.aircraft["acceleration"] * time_delta.total_seconds()
        )

    def _move_aircraft_laterally(self, time_delta: datetime.timedelta):
        """
        Evolve the lateral (lat, lon) position of the aircraft.
        """

        dt = time_delta.total_seconds()
        distances = self.aircraft["speed"] * (1852.0 / 3600.0) * dt
        proj_lon, proj_lat, _ = self.geod.fwd(
            self.aircraft["lon"],
            self.aircraft["lat"],
            self.aircraft["heading"],
            distances,
        )

        self.aircraft["lat"] = proj_lat
        self.aircraft["lon"] = proj_lon

    def _move_aircraft_vertically(self, time_delta: datetime.timedelta):
        """
        Evolve the altitude (flight_level) of the aircraft forward in time.
        """

        def move_aircraft_vertically_helper(aircraft):
            aircraft["rise"] = (
                calc_sign(
                    aircraft["flight_level"], aircraft["target_flight_level"], 10.0
                )
                * aircraft["max_rise_rate"]
            )
            return pd.Series(aircraft)

        self.aircraft = self.aircraft.apply(move_aircraft_vertically_helper, axis=1)

        dt = time_delta.total_seconds()
        self.aircraft["flight_level"] += self.aircraft["rise"] * dt

    def _rotate_aircraft(self, time_delta: datetime.timedelta):
        """
        Evolve the turn (heading) of the aircraft forward in time.
        """

        def rotate_aircraft_helper(aircraft):
            delta = aircraft["target_heading"] - aircraft["heading"]
            if delta < -180.0:
                delta += 360.0
            aircraft["turn"] = calc_sign(0, delta, 5.0) * aircraft["max_turn_rate"]
            return pd.Series(aircraft)

        self.aircraft = self.aircraft.apply(rotate_aircraft_helper, axis=1)

        dt = time_delta.total_seconds()
        self.aircraft["heading"] += self.aircraft["turn"] * dt
        self.aircraft["heading"] %= 360.0


def calc_sign(x, target_x, length_scale):
    n = (target_x - x) / length_scale
    return clamp(n, -1.0, 1.0)


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)
