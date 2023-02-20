import datetime
import json
import os
import pandas as pd
import pathlib
import pyproj

from .airspace import Airspace


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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
                "target_alt": pd.Series(dtype="float"), # Target altitude 
                "heading": pd.Series(dtype="float"),  # Degrees clockwise from North
                "speed": pd.Series(dtype="float"),  # Knots
                "rise": pd.Series(dtype="float"),  # Flight levels per second
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
            start_time = datetime.datetime.strptime(meta["start_time"], TIME_FORMAT)
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
        buffer += f"{self.time}".center(width, " ") + "\n"

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
        speed: float,
        rise: float,
        turn: float,
    ):
        """
        Add an aircraft to the simulation.
        """

        if callsign in self.aircraft.index:
            raise ValueError(f"Aircraft {callsign} already exists")

        self.aircraft.loc[callsign] = [agent, lat, lon, alt, target_alt, heading, speed, rise, turn]

    def remove_aircraft(self, callsign: str):
        """
        Remove an aircraft from the simulation.
        """

        if callsign not in self.aircraft.index:
            raise ValueError(f"Aircraft {callsign} does not exist")

        self.aircraft.drop(callsign, inplace=True)

    def evolve(self, time_delta: datetime.timedelta):
        """
        Evolve the simulation by a given time delta.
        """

        self._move_aircraft_laterally(time_delta)
        self._move_aircraft_vertically(time_delta)
        self._rotate_aircraft(time_delta)
        self.time += time_delta

    def _move_aircraft_laterally(self, time_delta: datetime.timedelta):
        """
        Evolve the lateral (lat, lon) position of the aircraft.
        """

        dt = time_delta.total_seconds()

        distances = self.aircraft["speed"] * (1852 / 3600) * dt
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
        """

        # dt = time_delta.total_seconds()
        # self.aircraft["alt"] += self.aircraft["rise"] * dt

        self.aircraft["alt"] += self.aircraft["target_alt"]

    def _rotate_aircraft(self, time_delta: datetime.timedelta):
        """
        Evolve the turn (heading) of the aircraft.
        """

        dt = time_delta.total_seconds()
        self.aircraft["heading"] += self.aircraft["turn"] * dt
        self.aircraft["heading"] %= 360.0
