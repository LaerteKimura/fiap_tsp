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
    [CORREÇÃO] Evita contar peso duplicado se uma cidade aparecer múltiplas vezes na rota.
    """
    total = 0.0
    cities_seen = set()  # Evitar contar peso duplicado se cidade aparecer múltiplas vezes
    for coord in route:
        city = coord_to_city.get(coord)
        if city and city in deliveries_by_city and city not in cities_seen:
            cities_seen.add(city)
            for d in deliveries_by_city[city]:
                total += d.total_weight
    return total


def calculate_route_distance(route: List[Tuple[int, int]],
                             coord_to_city: Dict[Tuple[int, int], str],
                             distance_lookup: Dict[Tuple[str, str], float]) -> float:
    """
    Calcula a distância total de uma rota em km.
    [CORREÇÃO] Evita calcular distância de cidade para ela mesma (ex: depósito->depósito)
    """
    if len(route) < 2:
        return 0.0
    
    dist = 0.0
    for i in range(len(route) - 1):  # Não usar % para evitar loop fechado desnecessário
        coord1 = route[i]
        coord2 = route[i + 1]
        
        # Se são as mesmas coordenadas, distância é 0 (ex: depósito->depósito)
        if coord1 == coord2:
            continue
            
        city1 = coord_to_city.get(coord1)
        city2 = coord_to_city.get(coord2)
        
        if city1 and city2:
            # Tenta ambas as direções (A->B ou B->A)
            distance = distance_lookup.get((city1, city2))
            if distance is None:
                distance = distance_lookup.get((city2, city1), 0.0)
            dist += distance
    
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