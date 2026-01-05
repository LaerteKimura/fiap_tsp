import csv
import numpy as np
import unicodedata
from typing import List, Dict, Tuple


def load_distances_from_tsv(path: str):
    distances = {}
    cities = set()

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            origem = row["origem"].strip()
            destino = row["destino"].strip()
            dist = float(row["distancia"])

            cities.add(origem)
            cities.add(destino)
            distances[(origem, destino)] = dist
            distances[(destino, origem)] = dist

    return sorted(cities), distances


def load_city_coordinates_from_csv(
    path: str,
    city_names: List[str]
) -> Dict[str, Tuple[float, float]]:

    def normalize(name: str) -> str:
        """
        Remove acentos e normaliza o nome para comparação.
        """
        nfkd = unicodedata.normalize('NFKD', name)
        ascii_str = nfkd.encode('ASCII', 'ignore').decode('ASCII')
        return ascii_str.lower().strip()

    wanted = {normalize(c): c for c in city_names}
    coords: Dict[str, Tuple[float, float]] = {}

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            city_raw = row["city"].strip()
            city_norm = normalize(city_raw)

            if city_norm in wanted:
                original_name = wanted[city_norm]
                lat = float(row["lat"])
                lng = float(row["lng"])
                coords[original_name] = (lat, lng)

    return coords