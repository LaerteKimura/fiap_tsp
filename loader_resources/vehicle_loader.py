# vehicle_loader.py
import csv
from dataclasses import dataclass
from typing import List


@dataclass
class Vehicle:
    vehicle_id: str
    max_load: float
    max_distance: float
    type: str
    max_weight: float
    cost_per_km: float
    name: str


def load_vehicles(csv_path: str) -> List[Vehicle]:
    vehicles = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vehicles.append(
                Vehicle(
                    vehicle_id=row["id"],
                    name=row["name"],
                    max_load=float(row["max_capacity"]),
                    max_distance=float(row["max_distance"]),
                    type=row["name"],
                    max_weight = float(row["max_weight"]),
                    cost_per_km=float(row["cost_per_km"])
                )
            )

    return vehicles
