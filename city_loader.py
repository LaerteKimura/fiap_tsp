import csv
import numpy as np
from typing import List, Dict, Tuple


# ======================================================
# DISTÂNCIAS (continua igual)
# ======================================================

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


def build_distance_matrix(
    cities: List[str],
    distance_lookup: Dict[tuple, float]
) -> np.ndarray:
    n = len(cities)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            matrix[i, j] = distance_lookup[(cities[i], cities[j])]

    return matrix


# ======================================================
# LAT / LNG LOADER (NOVO)
# ======================================================

def load_city_coordinates_from_csv(
    path: str,
    city_names: List[str]
) -> Dict[str, Tuple[float, float]]:

    def normalize(name: str) -> str:
        return (
            name.lower()
            .replace("ã", "a")
            .replace("á", "a")
            .replace("â", "a")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ô", "o")
            .replace("ú", "u")
            .strip()
        )

    # mapa normalizado -> nome original
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



# ======================================================
# LAT/LNG → COORDENADAS DE TELA
# ======================================================

def latlng_to_screen_coordinates(
    city_latlng: Dict[str, Tuple[float, float]],
    map_width: int,
    map_height: int,
    margin_x: int = 0,
    margin_y: int = 0,
    scale: float = 0.85  # 👈 controle aqui
) -> Dict[str, Tuple[int, int]]:

    lats = [lat for lat, _ in city_latlng.values()]
    lngs = [lng for _, lng in city_latlng.values()]

    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)

    lat_range = max_lat - min_lat or 1
    lng_range = max_lng - min_lng or 1

    # área efetiva reduzida
    effective_width = map_width * scale
    effective_height = map_height * scale

    # centralização
    offset_x = margin_x + (map_width - effective_width) / 2
    offset_y = margin_y + (map_height - effective_height) / 2

    coords = {}

    for city, (lat, lng) in city_latlng.items():
        x = (lng - min_lng) / lng_range
        y = (lat - min_lat) / lat_range

        screen_x = int(offset_x + x * effective_width)
        screen_y = int(offset_y + (1 - y) * effective_height)

        coords[city] = (screen_x, screen_y)

    return coords



