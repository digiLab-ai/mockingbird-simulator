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

    @staticmethod
    def from_json(s: str, fixes: pd.DataFrame):
        """
        Create an airspace from a JSON string.
        """

        vols = []
        for volume in json.loads(s):
            lats = []
            lons = []
            for fix in volume["boundary"]:
                lats.append(fixes.loc[fix, "lat"])
                lons.append(fixes.loc[fix, "lon"])
            vols.append(
                [
                    volume["min"],
                    volume["max"],
                    shapely.geometry.Polygon(zip(lons, lats)),
                ]
            )

        return Airspace(vols)

    def contains(self, lat: float, lon: float, alt: float):
        """
        Check if a point is contained within the volume.
        Points on the boundary are considered to be contained.
        """

        for (min, max, area) in self.vols:
            if alt < min or alt > max:
                continue
            if area.contains(shapely.geometry.Point(lon, lat)):
                return True
        return False
