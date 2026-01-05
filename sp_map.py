# sp_map.py

import json
import math
import pygame
from typing import Dict, List, Tuple


SP_BOUNDS: Dict[str, float] = {
    "min_lat": -25.35,
    "max_lat": -19.75,
    "min_lng": -53.10,
    "max_lng": -44.00
}


def load_geojson(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def calculate_geojson_distances(geojson_path: str, city_list: List[str]) -> Dict[Tuple[str, str], float]:
    """
    Calcula distâncias entre cidades usando centroides do GeoJSON.
    Retorna dicionário de distâncias: {(cidade1, cidade2): distancia_km}
    """
    print("📊 Calculando distâncias do GeoJSON...")
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        city_coords = {}
        for feature in data['features']:
            city_name = feature['properties'].get('name', '')
            for target_city in city_list:
                if (target_city.lower() in city_name.lower() or 
                    city_name.lower() in target_city.lower()):
                    geometry = feature['geometry']
                    if geometry['type'] == 'Polygon':
                        coords = geometry['coordinates'][0]
                        lons = [c[0] for c in coords]
                        lats = [c[1] for c in coords]
                        center_lon = sum(lons) / len(lons)
                        center_lat = sum(lats) / len(lats)
                        city_coords[target_city] = (center_lat, center_lon)
                        break
        
        new_distances = {}
        for city1 in city_list:
            for city2 in city_list:
                if city1 == city2:
                    new_distances[(city1, city2)] = 0.0
                    new_distances[(city2, city1)] = 0.0
                elif city1 in city_coords and city2 in city_coords:
                    lat1, lon1 = city_coords[city1]
                    lat2, lon2 = city_coords[city2]
                    dist = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111.0
                    new_distances[(city1, city2)] = dist
                    new_distances[(city2, city1)] = dist
        
        print(f"✅ {len(new_distances)//2} distâncias calculadas do GeoJSON")
        return new_distances
        
    except Exception as e:
        print(f"✗ Erro ao calcular distâncias do GeoJSON: {e}")
        return {}


def load_city_positions_from_geojson(geojson_path: str, target_cities: List[str]) -> Tuple[Dict, Dict]:
    """
    Carrega posições das cidades a partir do GeoJSON.
    Retorna: {cidade: (x, y)} onde x,y são coordenadas normalizadas para tela
    """
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        city_positions = {}
        bounds = {
            'min_x': float('inf'),
            'max_x': float('-inf'),
            'min_y': float('inf'),
            'max_y': float('-inf')
        }
        
        print("📊 Analisando GeoJSON...")
        
        for feature in data['features']:
            city_name = feature['properties'].get('name', '')
            geometry = feature['geometry']
            
            if geometry['type'] == 'Polygon':
                for ring in geometry['coordinates']:
                    for coord in ring:
                        lng, lat = coord
                        bounds['min_x'] = min(bounds['min_x'], lng)
                        bounds['max_x'] = max(bounds['max_x'], lng)
                        bounds['min_y'] = min(bounds['min_y'], lat)
                        bounds['max_y'] = max(bounds['max_y'], lat)
        
        print(f"Limites do GeoJSON:")
        print(f"  Longitude: {bounds['min_x']:.4f} a {bounds['max_x']:.4f}")
        print(f"  Latitude: {bounds['min_y']:.4f} a {bounds['max_y']:.4f}")
        
        for feature in data['features']:
            city_name = feature['properties'].get('name', '')
            geometry = feature['geometry']
            
            normalized_target = city_name.lower().replace(' ', '')
            found_city = None
            
            for target_city in target_cities:
                normalized_city = target_city.lower().replace(' ', '')
                if (normalized_target == normalized_city or 
                    normalized_target in normalized_city or
                    normalized_city in normalized_target):
                    found_city = target_city
                    break
            
            if found_city and geometry['type'] == 'Polygon':
                all_coords = []
                for ring in geometry['coordinates']:
                    all_coords.extend(ring)
                
                lngs = [coord[0] for coord in all_coords]
                lats = [coord[1] for coord in all_coords]
                
                center_lng = sum(lngs) / len(lngs)
                center_lat = sum(lats) / len(lats)
                
                norm_x = (center_lng - bounds['min_x']) / (bounds['max_x'] - bounds['min_x'])
                norm_y = 1.0 - ((center_lat - bounds['min_y']) / (bounds['max_y'] - bounds['min_y']))
                
                city_positions[found_city] = (norm_x, norm_y)
                print(f"  ✓ {found_city} → {city_name} ({center_lng:.4f}, {center_lat:.4f})")
        
        return city_positions, bounds
        
    except Exception as e:
        print(f"✗ Erro ao processar GeoJSON: {e}")
        return {}, None


def project_latlng(lat: float,
                   lng: float,
                   map_rect: pygame.Rect,
                   bounds: Dict[str, float],
                   padding_ratio: float = 0.06) -> Tuple[int, int]:
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


def draw_sp_map(surface: pygame.Surface,
                geojson: dict,
                map_rect: pygame.Rect,
                color=(200, 200, 200),
                width=1):
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
            ring = poly[0]
            points = []

            for lng, lat in ring:
                p = project_latlng(lat, lng, map_rect, SP_BOUNDS)
                points.append(p)

            if len(points) > 2:
                pygame.draw.lines(surface, color, True, points, width)


def build_sp_map_surface(size: tuple,
                         geojson_path: str,
                         bg_color=(255, 255, 255),
                         border_color=(190, 190, 190)) -> pygame.Surface:
    """
    Cria uma surface com o mapa de SP já renderizado
    para ser reutilizada no loop principal.
    """
    surface = pygame.Surface(size)
    surface.fill(bg_color)

    geojson = load_geojson(geojson_path)
    rect = surface.get_rect()

    draw_sp_map(surface, geojson, rect, color=border_color, width=1)

    return surface