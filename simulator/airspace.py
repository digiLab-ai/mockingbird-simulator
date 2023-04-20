import json
import pandas as pd
import shapely.geometry


class Airspace:
    """
    Region of three-dimensional airspace.
    """

    def __init__(self, vols: list):
        """
        Construct an empty airspace.
        """

        if vols is None:
            raise ValueError("Airspace must contain at least one volume.")

        self.vols = vols

    def contains(self, lat: float, lon: float, flight_level: float):
        """
        Check if a point is contained within the volume.
        Points on the boundary are considered to be contained.
        """

        for min, max, area in self.vols:
            if flight_level < min or flight_level > max:
                continue
            if area.contains(shapely.geometry.Point(lon, lat)):
                return True
        return False
