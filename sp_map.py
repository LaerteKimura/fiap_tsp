# sp_map.py
# ==========================================================
# Desenho do mapa real do estado de São Paulo (GeoJSON)
# ==========================================================

import json
import pygame
from typing import Dict


# ==========================================================
# BOUNDING BOX DO ESTADO DE SÃO PAULO
# (lat/lng reais)
# ==========================================================

SP_BOUNDS: Dict[str, float] = {
    "min_lat": -25.35,
    "max_lat": -19.75,
    "min_lng": -53.10,
    "max_lng": -44.00
}


# ==========================================================
# LOAD GEOJSON
# ==========================================================

def load_geojson(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ==========================================================
# PROJEÇÃO LAT/LNG → TELA
# ==========================================================

def project_latlng(
    lat: float,
    lng: float,
    map_rect: pygame.Rect,
    bounds: Dict[str, float],
    padding_ratio: float = 0.06
):
    """
    Converte lat/lng reais para coordenadas de tela,
    mantendo proporção e margem interna.
    """

    pad_x = map_rect.width * padding_ratio
    pad_y = map_rect.height * padding_ratio

    usable_w = map_rect.width - pad_x * 2
    usable_h = map_rect.height - pad_y * 2

    x_norm = (lng - bounds["min_lng"]) / (
        bounds["max_lng"] - bounds["min_lng"]
    )
    y_norm = (lat - bounds["min_lat"]) / (
        bounds["max_lat"] - bounds["min_lat"]
    )

    screen_x = map_rect.left + pad_x + x_norm * usable_w
    screen_y = map_rect.top + pad_y + (1 - y_norm) * usable_h

    return int(screen_x), int(screen_y)


# ==========================================================
# DRAW GEOJSON
# ==========================================================

def draw_sp_map(
    surface: pygame.Surface,
    geojson: dict,
    map_rect: pygame.Rect,
    color=(200, 200, 200),
    width=1
):
    """
    Desenha os municípios de SP no surface informado.
    """

    for feature in geojson["features"]:
        geom = feature["geometry"]
        geom_type = geom["type"]

        if geom_type == "Polygon":
            polygons = [geom["coordinates"]]

        elif geom_type == "MultiPolygon":
            polygons = geom["coordinates"]

        else:
            continue

        for poly in polygons:
            ring = poly[0]  # contorno externo
            points = []

            for lng, lat in ring:  # GeoJSON é (lng, lat)
                p = project_latlng(
                    lat,
                    lng,
                    map_rect,
                    SP_BOUNDS
                )
                points.append(p)

            if len(points) > 2:
                pygame.draw.lines(
                    surface,
                    color,
                    True,
                    points,
                    width
                )


# ==========================================================
# CACHE DO MAPA (PERFORMANCE)
# ==========================================================

def build_sp_map_surface(
    size: tuple,
    geojson_path: str,
    bg_color=(255, 255, 255),
    border_color=(190, 190, 190)
) -> pygame.Surface:
    """
    Cria uma surface com o mapa de SP já renderizado
    para ser reutilizada no loop principal.
    """

    surface = pygame.Surface(size)
    surface.fill(bg_color)

    geojson = load_geojson(geojson_path)
    rect = surface.get_rect()

    draw_sp_map(
        surface,
        geojson,
        rect,
        color=border_color,
        width=1
    )

    return surface
