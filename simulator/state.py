import datetime
import json
import os
import pandas as pd
import pathlib
import pyproj

from . import settings
from .airspace import Airspace


class State:
    """
    Complete description world state, at a single instance in time.
    """

    geod = pyproj.Geod(ellps="WGS84")

    def __init__(self, time: datetime.datetime, bay_names: list[str]):
        """
        Initialise a new simulation.
        """

        self.time = time  # Current time
        self.tick = 0  # Number of times the simulation has been ticked forward one settings.TIME_STEP_DELTA
        self.extra_time = datetime.timedelta(
            0
        )  # Difference in time between total calls to evolve, and the state that has been actually ticked forward
        self.bay_names = bay_names
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
                "airspace": pd.Series(dtype="object"),  # Agent controlling the sector
            },
            dtype="str",
        )
        self.aircraft = pd.DataFrame(  # Flying machines in the simulation
            {
                "agent": pd.Series(dtype="str"),  # Agent controlling the aircraft
                "bay": pd.Series(dtype="str"),  # Bay to hold the aircraft strip
                "lat": pd.Series(dtype="float"),  # Degrees North/South
                "lon": pd.Series(dtype="float"),  # Degrees East/West
                "alt": pd.Series(dtype="float"),  # Flight level
                "target_alt": pd.Series(dtype="float"),  # Target altitude
                "heading": pd.Series(dtype="float"),  # Degrees clockwise from North
                "target_heading": pd.Series(
                    dtype="float"
                ),  # Degrees clockwise from North
                "speed": pd.Series(dtype="float"),  # Knots
                "target_speed": pd.Series(dtype="float"),  # Knots
                "rise": pd.Series(
                    dtype="float"
                ),  # Flight levels per second (absolute value)
                "turn": pd.Series(dtype="float"),  # Degrees clockwise per second
            },
            dtype="str",
        )

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
            bay_names = meta["bay_names"]
        state = State(start_time, bay_names)

        state._load_fixes(os.path.join(scenario_dir, "fixes.csv"))
        state._load_sectors(os.path.join(scenario_dir, "sectors.json"))
        state._load_aircraft(os.path.join(scenario_dir, "aircraft.csv"))

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
                raise ValueError(f"Column headings differ to those expected")

        self.fixes = fixes

    def _load_sectors(self, file_path: str):
        """
        Load sector state from a .json file.
        Note this will replace the current sector state.
        """

        # Clear the current sectors
        self.sectors = pd.DataFrame(columns=self.sectors.columns)
        with open(file_path) as file:
            for (name, data) in json.load(file).items():
                self.sectors.loc[name] = [
                    data["agent"],
                    Airspace.from_json(json.dumps(data["vols"]), self.fixes),
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
                raise ValueError(f"Column headings differ to those expected")

        self.aircraft = aircraft

    def __str__(self):
        """
        Print the state.
        """

        width = 72
        buffer = " STATE ".center(width, "=") + "\n"
        buffer += f"{self.time} - t{self.tick}".center(width, " ") + "\n"

        # buffer += " fixes ".center(width, "-") + "\n"
        # buffer += f"{self.fixes}\n"

        # buffer += " sectors ".center(width, "-") + "\n"
        # buffer += f"{self.sectors}\n"

        buffer += " aircraft ".center(width, "-") + "\n"
        buffer += f"{self.aircraft}\n"

        buffer += "".center(width, "=")
        return buffer

    def add_aircraft(
        self,
        callsign: str,
        agent: str,
        lat: float,
        lon: float,
        alt: float,
        target_alt: float,
        heading: float,
        target_heading: float,
        speed: float,
        target_speed: float,
        rise: float,
        turn: float,
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
            alt,
            target_alt,
            heading,
            target_heading,
            speed,
            target_speed,
            rise,
            turn,
        ]

    def remove_aircraft(self, callsign: str):
        """
        Remove an aircraft from the simulation.
        """

        if callsign not in self.aircraft.index:
            raise ValueError(f"Aircraft {callsign} does not exist")

        self.aircraft.drop(callsign, inplace=True)

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
            self._rotate_aircraft(settings.TIME_STEP_DELTA)
            self._move_aircraft_laterally(settings.TIME_STEP_DELTA)
            self._move_aircraft_vertically(settings.TIME_STEP_DELTA)
            self.time += settings.TIME_STEP_DELTA
            self.tick += 1

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
        Evolve the vertical (alt) position of the aircraft.

        Once an altitude greater to or equal to the target altitude is reached,
        the rise will adjust to 0.0 in order to maintain target altitude.
        """

        dt = time_delta.total_seconds()

        self.aircraft["alt"] += self.aircraft["rise"] * dt
        # increase the altitude based on rise (absolute value speed) * change in time

        for i in range((len(self.aircraft.index))):
            # iterate through each aircraft to change each altitude to the target
            altdifference = self.aircraft["target_alt"][i] - self.aircraft["alt"][i]
            # difference between the target altitude and the altitude flight is currently at
            if altdifference == 1 or altdifference == 0 or altdifference == 2:
                # if the difference between the target and current altitude is either 0, 1, 2 flight levels (due to odd/even rise), execute:
                callsign = self.aircraft.index[i]
                self.aircraft.loc[(callsign, "rise")] = 0.0
                # change the rise in the aircraft DF for which target altitude reached to zero to prevent further increase
                # self.aircraft["rise"][i] = 0.0 also works but only iterates over the copy
            elif altdifference <= -1:
                callsign = self.aircraft.index[i]
                self.aircraft.loc[(callsign, "rise")] = 0.0
            # change the rise in the aircraft DF to zero, to prevent aircraft getting vertically further from target altitude

    def _rotate_aircraft(self, time_delta: datetime.timedelta):
        """
        Evolve the turn (heading) of the aircraft.
        """

        dt = time_delta.total_seconds()
        self.aircraft["heading"] += self.aircraft["turn"] * dt
        self.aircraft["heading"] %= 360.0
