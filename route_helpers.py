# route_helpers.py

from typing import List, Tuple, Dict, Optional
from config import RED, ORANGE, GREEN


def get_city_priority_info(city: str, deliveries_by_city: Dict) -> Tuple[str, int, Tuple[int, int, int]]:
    """
    Retorna informações de prioridade de uma cidade.
    Returns: (texto_prioridade, numero_prioridade, cor)
    """
    if city not in deliveries_by_city:
        return "P2", 2, GREEN
    
    priorities = [d.priority for d in deliveries_by_city[city]]
    min_priority = min(priorities)
    
    if min_priority == 0:
        return "P0 (Alta)", 0, RED
    elif min_priority == 1:
        return "P1 (Média)", 1, ORANGE
    else:
        return "P2 (Baixa)", 2, GREEN


def calculate_route_weight(route: List[Tuple[int, int]], 
                           coord_to_city: Dict[Tuple[int, int], str],
                           deliveries_by_city: Dict) -> float:
    """
    Calcula o peso total de uma rota em kg.
    """
    total = 0.0
    for coord in route:
        city = coord_to_city[coord]
        if city in deliveries_by_city:
            for d in deliveries_by_city[city]:
                total += d.total_weight
    return total


def calculate_route_distance(route: List[Tuple[int, int]],
                             coord_to_city: Dict[Tuple[int, int], str],
                             distance_lookup: Dict[Tuple[str, str], float]) -> float:
    """
    Calcula a distância total de uma rota em km.
    """
    if len(route) < 2:
        return 0.0
    
    dist = 0.0
    for i in range(len(route)):
        city1 = coord_to_city[route[i]]
        city2 = coord_to_city[route[(i + 1) % len(route)]]
        dist += distance_lookup.get((city1, city2), 
               distance_lookup.get((city2, city1), 0.0))
    
    return dist


def select_vehicle(total_weight: float, 
                  total_distance_km: float, 
                  vehicles: List) -> Optional:
    """
    Escolhe o veículo mais adequado para a rota.
    Retorna o veículo viável com menor custo por km, ou None se nenhum for viável.
    """
    viable = [
        v for v in vehicles
        if total_weight <= v.max_weight
        and total_distance_km <= v.max_distance
    ]
    if not viable:
        return None
    return min(viable, key=lambda v: v.cost_per_km)