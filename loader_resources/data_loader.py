# data_loader.py

import pygame
from collections import defaultdict
from typing import Dict, List, Tuple

from loader_resources.delivery_loader import load_deliveries
from loader_resources.vehicle_loader import load_vehicles
from loader_resources.city_loader import load_distances_from_tsv, load_city_coordinates_from_csv
from sp_map import (
    build_sp_map_surface, 
    project_latlng, 
    SP_BOUNDS,
    calculate_geojson_distances
)
from config import MAP_WIDTH, HEIGHT, INFO_WIDTH


def load_all_data(deliveries_path: str = "data_files/deliveries.csv",
                  distances_path: str = "data_files/cidades_sp.tsv",
                  vehicles_path: str = "data_files/veiculos.csv",
                  coordinates_path: str = "data_files/worldcities.csv",
                  geojson_path: str = "data_files/geojs-35-mun.json"):
    """
    Carrega todos os dados necessários para o TSP.
    Retorna um dicionário com todos os dados carregados.
    """
    
    print("\n🔄 Carregando dados...")
    
    deliveries = load_deliveries(deliveries_path)
    deliveries_by_city = defaultdict(list)
    for d in deliveries:
        deliveries_by_city[d.city].append(d)

    cities = sorted(deliveries_by_city.keys())
    print(f"✅ {len(cities)} cidades para entregas: {cities}")

    try:
        _, distance_lookup = load_distances_from_tsv(distances_path)
        
        missing_distances = []
        for city1 in cities:
            for city2 in cities:
                if city1 != city2 and (city1, city2) not in distance_lookup and (city2, city1) not in distance_lookup:
                    missing_distances.append((city1, city2))
        
        if missing_distances:
            print(f"⚠️  {len(missing_distances)} pares de cidades sem distâncias no TSV")
            
            try:
                geojson_distances = calculate_geojson_distances(geojson_path, cities)
                if geojson_distances:
                    for key, value in geojson_distances.items():
                        if key not in distance_lookup:
                            distance_lookup[key] = value
            
            except Exception as e:
                print(f"⚠️  Não foi possível usar GeoJSON: {e}")
        
        print(f"✅ {len(distance_lookup)//2} distâncias carregadas")
        
    except Exception as e:
        print(f"✗ Erro ao carregar distâncias: {e}")
        distance_lookup = {}
        for i, city1 in enumerate(cities):
            for j, city2 in enumerate(cities):
                if i == j:
                    distance_lookup[(city1, city2)] = 0.0
                else:
                    distance_lookup[(city1, city2)] = abs(i - j) * 50 + 30

    vehicles = load_vehicles(vehicles_path)
    print(f"✅ {len(vehicles)} veículos carregados")

    city_latlng = load_city_coordinates_from_csv(coordinates_path, cities)

    missing = set(cities) - set(city_latlng.keys())
    if missing:
        print(f"⚠️  {len(missing)} CIDADES SEM COORDENADAS: {missing}")
        sp_cities_approx = {
            'São Paulo': (-23.55, -46.63),
            'Campinas': (-22.90, -47.06),
            'Santos': (-23.96, -46.33),
            'São José dos Campos': (-23.18, -45.89),
            'Ribeirão Preto': (-21.18, -47.81),
            'Sorocaba': (-23.50, -47.46),
            'São José do Rio Preto': (-20.81, -49.38),
            'Piracicaba': (-22.73, -47.65),
            'Bauru': (-22.31, -49.06),
            'São Carlos': (-22.02, -47.89),
            'Adamantina': (-21.69, -51.07),
            'Presidente Prudente': (-22.13, -51.39),
            'Marília': (-22.21, -49.95)
        }
        
        for city in list(missing):
            if city in sp_cities_approx:
                city_latlng[city] = sp_cities_approx[city]
                missing.remove(city)
                print(f"  ✓ Coordenada padrão para {city}")
        
        for i, city in enumerate(missing):
            lat = -22.5 + (i % 5) * 0.5
            lng = -48.0 + (i // 5) * 0.5
            city_latlng[city] = (lat, lng)
            print(f"  ⚠️  {city}: coordenada estimada ({lat:.2f}, {lng:.2f})")

    print("\n🗺️ Posicionando cidades no mapa...")

    map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT)

    city_to_coord = {}
    for city, (lat, lng) in city_latlng.items():
        x, y = project_latlng(lat, lng, map_rect, SP_BOUNDS)
        city_to_coord[city] = (x, y)
        print(f"  ✓ {city}: ({lat:.2f}, {lng:.2f}) → ({x}, {y})")

    coords = [city_to_coord[c] for c in cities]
    coord_to_city = {coord: city for city, coord in city_to_coord.items()}

    print(f"\n✅ {len(coords)} coordenadas mapeadas usando project_latlng()")

    print("\n🗺️ Gerando mapa de São Paulo...")
    map_surface = build_sp_map_surface(
        size=(MAP_WIDTH, HEIGHT),
        geojson_path=geojson_path
    )

    return {
        'deliveries': deliveries,
        'deliveries_by_city': deliveries_by_city,
        'cities': cities,
        'distance_lookup': distance_lookup,
        'vehicles': vehicles,
        'city_latlng': city_latlng,
        'city_to_coord': city_to_coord,
        'coords': coords,
        'coord_to_city': coord_to_city,
        'map_surface': map_surface
    }