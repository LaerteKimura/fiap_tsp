# vrp_solver.py - VERSÃO ÚNICA E CORRETA
import random
import math
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from copy import deepcopy

from genetic_algorithm import (
    calculate_route_distance,
    calculate_route_weight,
    calculate_priority_penalty
)

from config import (
    POPULATION_SIZE, MUTATION_RATE, ELITE_PERCENTAGE,
    VRP_FIXED_COST_PER_ROUTE, VRP_MAX_GENERATIONS,
    VRP_CONVERGENCE_GENERATIONS, VRP_CONVERGENCE_THRESHOLD
)


# =========================
# PARÂMETROS CRÍTICOS
# =========================
class VRPOptions:
    def __init__(self):
        # PENALIDADES MUITO ALTAS para violações
        self.WEIGHTS = {
            'distance': 0.1,
            'priority': 50.0,
            'vehicle_count': 800,
            'vehicle_use': 300,
            'uncovered_city': 50000,
            'capacity_violation': 100000,
            'duplicate_vehicle': 1000000,
            'weight_violation': 200000,
            'distance_violation': 200000,
            'underutilization': 500.0,  # Penalidade por subutilização de capacidade (peso)
            'distance_underutilization': 100.0,  # Penalidade por subutilização de distância
        }
        
        # Threshold de utilização mínima (abaixo disso aplica penalidade)
        # Ex: 0.6 = 60% - veículos com menos de 60% de utilização são penalizados
        self.MIN_UTILIZATION_THRESHOLD = 0.6  # 60% de utilização mínima de peso
        self.MIN_DISTANCE_UTILIZATION_THRESHOLD = 0.5  # 50% de utilização mínima de distância
        
        self.MUTATION_RATES = {
            'swap_between_routes': 0.4,
            'move_city': 0.4,
            'swap_within_route': 0.5,
            'reverse_segment': 0.3,
            'split_route': 0.2,
        }


# =========================
# ESTRUTURAS
# =========================
@dataclass
class VRPRoute:
    vehicle: object
    route: List
    depot_coord: Optional[Tuple] = None
    
    def __post_init__(self):
        self.total_distance = 0.0
        self.total_weight = 0.0
        self.total_cost = 0.0
        self.max_priority = 2
        self.avg_priority = 2.0
        self.cities = set()
        self.priority_score = 0.0
        self.weight_violation = 0.0
        self.distance_violation = 0.0
        self.is_feasible = True
    
    def calculate_stats(self, coord_to_city, deliveries_by_city, distance_lookup):
        if not self.route:
            self.total_distance = 0.0
            self.total_weight = 0.0
            self.total_cost = 0.0
            self.cities = set()
            self.priority_score = 0.0
            self.weight_violation = 0.0
            self.distance_violation = 0.0
            self.is_feasible = True
            return
        
        # Distância
        if self.depot_coord:
            # [CORREÇÃO] Se o depósito já é a primeira cidade na rota, não adicionar no início
            if self.route and self.route[0] == self.depot_coord:
                # Depósito já está no início, apenas adicionar no final
                full_route = self.route + [self.depot_coord]
            else:
                # Depósito não está na rota, adicionar no início e fim
                full_route = [self.depot_coord] + self.route + [self.depot_coord]
            self.total_distance = calculate_route_distance(
                full_route, coord_to_city, distance_lookup
            )
        else:
            self.total_distance = calculate_route_distance(
                self.route, coord_to_city, distance_lookup
            )
        
        # Peso
        self.total_weight = calculate_route_weight(
            self.route, coord_to_city, deliveries_by_city
        )
        
        # Custo (usando custo fixo configurável do config)
        # [MELHORIA] Tornar custo fixo configurável - permite ajustar custo fixo por rota via config
        self.total_cost = (self.total_distance * self.vehicle.cost_per_km) + VRP_FIXED_COST_PER_ROUTE
        
        # Calcular violações
        # [CORREÇÃO] Usar pequeno epsilon para evitar problemas de precisão de ponto flutuante
        # Ex: 1200.0000001 vs 1200 pode dar falso positivo sem epsilon
        WEIGHT_EPSILON = 0.01  # 10g de tolerância para erros de arredondamento em peso
        DISTANCE_EPSILON = 0.1  # 100m de tolerância para erros de arredondamento em distância
        # Violação ocorre apenas se exceder o limite por mais que EPSILON
        weight_excess = self.total_weight - self.vehicle.max_weight
        distance_excess = self.total_distance - self.vehicle.max_distance
        # Se exceder por menos que EPSILON, considera dentro da margem de tolerância
        self.weight_violation = max(0, weight_excess - WEIGHT_EPSILON) if weight_excess > WEIGHT_EPSILON else 0
        self.distance_violation = max(0, distance_excess - DISTANCE_EPSILON) if distance_excess > DISTANCE_EPSILON else 0
        self.is_feasible = (self.weight_violation == 0 and self.distance_violation == 0)
        
        # Prioridades
        priorities = []
        self.cities = set()
        priority_positions = []
        
        for position, coord in enumerate(self.route):
            city = coord_to_city.get(coord)
            self.cities.add(city)
            if city and city in deliveries_by_city:
                for d in deliveries_by_city[city]:
                    priorities.append(d.priority)
                    normalized_position = position / max(1, len(self.route) - 1)
                    priority_positions.append((d.priority, normalized_position))
        
        if priorities:
            self.max_priority = min(priorities)
            self.avg_priority = sum(priorities) / len(priorities)
            
            # Score de prioridade (quanto menor, melhor)
            self.priority_score = 0.0
            for priority, position in priority_positions:
                if priority == 0:
                    self.priority_score += position * 100  # Alta penalidade se prioridade 0 estiver no final
                elif priority == 1:
                    self.priority_score += position * 30
                else:
                    self.priority_score += position * 10
        else:
            self.max_priority = 2
            self.avg_priority = 2.0
            self.priority_score = 0.0


# =========================
# FUNÇÕES AUXILIARES
# =========================
def build_random_solution(cities_coords, vehicles, depot_coord):
    """Solução aleatória."""
    num_vehicles = min(len(vehicles), max(1, random.randint(1, 3)))
    selected_vehicles = vehicles[:num_vehicles]
    
    solution = [VRPRoute(v, [], depot_coord) for v in selected_vehicles]
    
    shuffled = cities_coords[:]
    random.shuffle(shuffled)
    
    for i, coord in enumerate(shuffled):
        route_idx = i % len(solution)
        solution[route_idx].route.append(coord)
    
    return solution


def build_solution_by_priority(cities_coords, vehicles, depot_coord, coord_to_city, deliveries_by_city):
    """Constrói solução agrupando por prioridade."""
    # Agrupar cidades por prioridade
    priority_groups = {0: [], 1: [], 2: []}
    
    for coord in cities_coords:
        city = coord_to_city.get(coord)
        if city and city in deliveries_by_city:
            priorities = [d.priority for d in deliveries_by_city[city]]
            min_priority = min(priorities) if priorities else 2
            priority_groups[min_priority].append(coord)
        else:
            priority_groups[2].append(coord)
    
    # Criar rotas
    solution = []
    used_vehicles = set()
    
    # Prioridade 0 primeiro
    for priority in [0, 1, 2]:
        coords = priority_groups[priority]
        if not coords:
            continue
        
        # Veículo disponível
        available_vehicles = [v for v in vehicles if v.vehicle_id not in used_vehicles]
        if not available_vehicles:
            # Sem veículos, adicionar à última rota
            if solution:
                solution[-1].route.extend(coords)
            continue
        
        # Nova rota para este grupo
        route = VRPRoute(available_vehicles[0], coords, depot_coord)
        solution.append(route)
        used_vehicles.add(available_vehicles[0].vehicle_id)
    
    return solution


# =========================
# FUNÇÃO FITNESS COM PENALIDADES FORTES
# =========================
def calculate_vrp_fitness(solution, coord_to_city, deliveries_by_city,
                         distance_lookup, all_cities_coords, options,
                         generation=0, max_generations=200):
    """Função fitness com penalidades EFETIVAS."""
    
    fitness = 0.0
    used_vehicle_ids = set()
    active_routes = 0
    covered_cities = set()
    total_priority_score = 0.0
    total_cost = 0.0
    
    # Contadores de violação
    weight_violations = 0
    distance_violations = 0
    
    # Avaliar cada rota
    for route in solution:
        if not route.route:
            continue
        
        active_routes += 1
        
        # 1. Veículo único - PENALIDADE MÁXIMA
        if route.vehicle.vehicle_id in used_vehicle_ids:
            return options.WEIGHTS['duplicate_vehicle'] * 100
        
        used_vehicle_ids.add(route.vehicle.vehicle_id)
        
        # 2. Violação de peso - PENALIDADE EXPONENCIAL
        if route.weight_violation > 0:
            weight_violations += 1
            weight_penalty = (route.weight_violation ** 2) * options.WEIGHTS['weight_violation']
            fitness += weight_penalty
        
        # 3. Violação de distância - PENALIDADE EXPONENCIAL
        if route.distance_violation > 0:
            distance_violations += 1
            distance_penalty = (route.distance_violation ** 2) * options.WEIGHTS['distance_violation']
            fitness += distance_penalty
        
        # 4. Custo base (somente se viável)
        if route.is_feasible:
            total_cost += route.total_cost
        
        # 5. Score de prioridade
        total_priority_score += route.priority_score
        
        # 6. Cidades cobertas
        covered_cities.update(route.cities)
        
        # 7. [MELHORIA] Penalidade por subutilização de capacidade (peso)
        # Penaliza veículos que estão muito "vazios" para incentivar melhor utilização
        # Baseado em: "Vehicle Routing Problem with Utilization Constraints" (literatura VRP)
        if route.is_feasible and route.vehicle.max_weight > 0:
            weight_utilization = route.total_weight / route.vehicle.max_weight
            if weight_utilization < options.MIN_UTILIZATION_THRESHOLD:
                # Penalidade proporcional à capacidade não utilizada
                unused_capacity_ratio = 1.0 - weight_utilization
                # Penalidade maior para veículos maiores subutilizados
                capacity_factor = route.vehicle.max_weight / 1000.0  # Normalizar por 1000kg
                underutilization_penalty = (unused_capacity_ratio ** 2) * options.WEIGHTS['underutilization'] * capacity_factor
                fitness += underutilization_penalty
        
        # 8. [MELHORIA] Penalidade por subutilização de distância
        # Penaliza veículos que percorrem muito menos distância do que podem
        # Incentiva usar veículos com alcance adequado à rota
        if route.is_feasible and route.vehicle.max_distance > 0:
            distance_utilization = route.total_distance / route.vehicle.max_distance
            if distance_utilization < options.MIN_DISTANCE_UTILIZATION_THRESHOLD:
                # Penalidade proporcional à distância não utilizada
                unused_distance_ratio = 1.0 - distance_utilization
                # Penalidade maior para veículos com maior alcance subutilizados
                distance_factor = route.vehicle.max_distance / 1000.0  # Normalizar por 1000km
                distance_underutilization_penalty = (unused_distance_ratio ** 2) * options.WEIGHTS['distance_underutilization'] * distance_factor
                fitness += distance_underutilization_penalty
    
    # Penalidade por cidades não cobertas
    expected_cities = {coord_to_city.get(c) for c in all_cities_coords if coord_to_city.get(c)}
    missing_cities = expected_cities - covered_cities
    if missing_cities:
        fitness += len(missing_cities) * options.WEIGHTS['uncovered_city']
    
    # Se tem violações, penalidade MASSIVA
    if weight_violations > 0 or distance_violations > 0:
        # Solução inviável - penalidade adicional
        fitness += (weight_violations + distance_violations) * options.WEIGHTS['capacity_violation'] * 1000
        # Custo multiplicado para garantir que é pior que qualquer solução viável
        fitness += total_cost * 100
    else:
        # Solução viável - otimizar normalmente
        fitness += total_cost
        
        # Peso de prioridade aumenta ao longo das gerações
        progress = generation / max_generations if max_generations > 0 else 0
        priority_weight = options.WEIGHTS['priority'] * (1 + progress * 2)
        fitness += total_priority_score * priority_weight
        
        # Penalidade por usar muitos veículos
        vehicle_penalty = active_routes * options.WEIGHTS['vehicle_count']
        
        # Bonificação para poucos veículos
        if active_routes == 1:
            vehicle_penalty *= 0.3
        elif active_routes == 2:
            vehicle_penalty *= 0.7
        
        fitness += vehicle_penalty
        
        # Penalidade extra por usar veículos além do mínimo
        min_vehicles_estimated = max(1, len(all_cities_coords) // 10)
        if active_routes > min_vehicles_estimated:
            extra_vehicles = active_routes - min_vehicles_estimated
            fitness += extra_vehicles * options.WEIGHTS['vehicle_use']
    
    return fitness


# =========================
# OPERADORES GENÉTICOS
# =========================
def adaptive_crossover(parent_a, parent_b, depot_coord, options, generation, max_generations):
    """Crossover adaptativo."""
    # Coletar veículos
    all_vehicles = {}
    for route in parent_a + parent_b:
        all_vehicles[route.vehicle.vehicle_id] = route.vehicle
    
    # Mapear cidades
    city_to_vehicle_a = {}
    city_to_vehicle_b = {}
    
    for route in parent_a:
        for city in route.route:
            city_to_vehicle_a[city] = route.vehicle.vehicle_id
    
    for route in parent_b:
        for city in route.route:
            city_to_vehicle_b[city] = route.vehicle.vehicle_id
    
    # Todas as cidades
    all_cities = set(city_to_vehicle_a.keys()) | set(city_to_vehicle_b.keys())
    
    # Criar rotas filhas
    child_routes = {}
    for vehicle_id, vehicle in all_vehicles.items():
        child_routes[vehicle_id] = VRPRoute(vehicle, [], depot_coord)
    
    # Atribuir cidades (50% de chance de herdar de cada pai)
    for city in all_cities:
        if city in city_to_vehicle_a and city in city_to_vehicle_b:
            if random.random() < 0.5:
                chosen_vehicle = city_to_vehicle_a[city]
            else:
                chosen_vehicle = city_to_vehicle_b[city]
        elif city in city_to_vehicle_a:
            chosen_vehicle = city_to_vehicle_a[city]
        else:
            chosen_vehicle = city_to_vehicle_b[city]
        
        if chosen_vehicle in child_routes:
            child_routes[chosen_vehicle].route.append(city)
    
    # Garantir todas as cidades
    result = [route for route in child_routes.values() if route.route]
    
    cities_in_child = set()
    for route in result:
        cities_in_child.update(route.route)
    
    missing_cities = all_cities - cities_in_child
    for city in missing_cities:
        if result:
            shortest_route = min(result, key=lambda r: len(r.route))
            shortest_route.route.append(city)
    
    # [CORREÇÃO] Garantir que depósito seja sempre a primeira cidade em cada rota
    if depot_coord:
        for route in result:
            route.route = ensure_depot_first(route.route, depot_coord)
    
    return result


def feasibility_mutation(solution, depot_coord, options, generation,
                        coord_to_city, deliveries_by_city, distance_lookup):
    """Mutação especial para corrigir violações."""
    new_solution = []
    for route in solution:
        new_route = VRPRoute(route.vehicle, route.route[:], depot_coord)
        new_route.calculate_stats(coord_to_city, deliveries_by_city, distance_lookup)
        new_solution.append(new_route)
    
    # Taxa de mutação aumentada se houver violações
    base_rate = MUTATION_RATE
    
    has_violations = any(r.weight_violation > 0 or r.distance_violation > 0 
                        for r in new_solution)
    
    if has_violations:
        base_rate = min(0.9, base_rate * 3)
    
    # 1. DIVIDIR ROTAS SOBRECARREGADAS
    if random.random() < options.MUTATION_RATES['split_route'] * base_rate:
        overloaded_routes = [r for r in new_solution if r.weight_violation > 0 or r.distance_violation > 0]
        if overloaded_routes and len(new_solution) < 10:  # Limite de rotas
            route_to_split = max(overloaded_routes,
                               key=lambda r: max(r.weight_violation, r.distance_violation))
            
            if len(route_to_split.route) >= 3:
                # [CORREÇÃO] Se depósito está na primeira posição, não dividir incluindo ele
                if depot_coord and route_to_split.route and route_to_split.route[0] == depot_coord:
                    # Depósito fica na primeira rota, dividir o resto
                    split_point = 1 + (len(route_to_split.route) - 1) // 2
                    first_half = route_to_split.route[:split_point]
                    second_half = route_to_split.route[split_point:]
                else:
                    split_point = len(route_to_split.route) // 2
                    first_half = route_to_split.route[:split_point]
                    second_half = route_to_split.route[split_point:]
                
                # Usar mesmo veículo ou encontrar outro
                route_to_split.route = first_half
                new_route = VRPRoute(route_to_split.vehicle, second_half, depot_coord)
                # [CORREÇÃO] Garantir que depósito fique no início da segunda rota se presente
                if depot_coord and depot_coord in new_route.route:
                    new_route.route = ensure_depot_first(new_route.route, depot_coord)
                new_solution.append(new_route)
    
    # 2. MOVER CIDADES PESADAS
    if random.random() < options.MUTATION_RATES['move_city'] * base_rate:
        non_empty = [r for r in new_solution if r.route]
        if len(non_empty) >= 2:
            # Encontrar rota mais pesada
            routes_with_violations = [r for r in non_empty if r.weight_violation > 0]
            if routes_with_violations:
                src = max(routes_with_violations, key=lambda r: r.weight_violation)
                dst = min(non_empty, key=lambda r: r.total_weight)
                
                if src.route and src != dst:
                    # Mover cidade mais pesada
                    city_weights = []
                    for city in src.route:
                        weight = calculate_route_weight([city], coord_to_city, deliveries_by_city)
                        city_weights.append((city, weight))
                    
                    if city_weights:
                        heaviest_city = max(city_weights, key=lambda x: x[1])[0]
                        src.route.remove(heaviest_city)
                        dst.route.append(heaviest_city)
    
    # 3. TROCAS ENTRE ROTAS
    if random.random() < options.MUTATION_RATES['swap_between_routes'] * base_rate:
        non_empty = [r for r in new_solution if r.route]
        if len(non_empty) >= 2:
            r1, r2 = random.sample(non_empty, 2)
            if r1.route and r2.route:
                # [CORREÇÃO] Não trocar o depósito se ele for a primeira cidade
                available_c1 = [c for c in r1.route if not (depot_coord and c == depot_coord and r1.route[0] == depot_coord)]
                available_c2 = [c for c in r2.route if not (depot_coord and c == depot_coord and r2.route[0] == depot_coord)]
                
                if available_c1 and available_c2:
                    c1 = random.choice(available_c1)
                    c2 = random.choice(available_c2)
                    r1.route.remove(c1)
                    r2.route.remove(c2)
                    r1.route.append(c2)
                    r2.route.append(c1)
    
    # 4. TROCAS DENTRO DA ROTA (para prioridade)
    if random.random() < options.MUTATION_RATES['swap_within_route'] * base_rate:
        for route in new_solution:
            if len(route.route) >= 2:
                # [CORREÇÃO] Não trocar a primeira posição se for o depósito
                if depot_coord and route.route and route.route[0] == depot_coord:
                    if len(route.route) >= 3:
                        i, j = random.sample(range(1, len(route.route)), 2)
                        route.route[i], route.route[j] = route.route[j], route.route[i]
                else:
                    i, j = random.sample(range(len(route.route)), 2)
                    route.route[i], route.route[j] = route.route[j], route.route[i]
    
    # 5. INVERTER SEGMENTO
    if random.random() < options.MUTATION_RATES['reverse_segment'] * base_rate:
        for route in new_solution:
            if len(route.route) >= 4:
                # [CORREÇÃO] Não inverter incluindo a primeira posição se for o depósito
                if depot_coord and route.route and route.route[0] == depot_coord:
                    i, j = sorted(random.sample(range(1, len(route.route) - 1), 2))
                    route.route[i:j] = reversed(route.route[i:j])
                else:
                    i, j = sorted(random.sample(range(1, len(route.route) - 1), 2))
                    route.route[i:j] = reversed(route.route[i:j])
    
    # [CORREÇÃO] Garantir que depósito seja sempre a primeira cidade após mutações
    if depot_coord:
        for route in new_solution:
            route.route = ensure_depot_first(route.route, depot_coord)
    
    return new_solution


# =========================
# OTIMIZAÇÃO LOCAL
# =========================
def ensure_depot_first(route_coords, depot_coord):
    """Garante que o depósito seja sempre a primeira cidade na rota se presente."""
    if not depot_coord or not route_coords:
        return route_coords
    
    if depot_coord in route_coords:
        # Remover depósito de onde estiver
        route_coords = [c for c in route_coords if c != depot_coord]
        # Colocar no início
        route_coords.insert(0, depot_coord)
    
    return route_coords


def optimize_route_order(route_coords, coord_to_city, deliveries_by_city, depot_coord=None):
    """Reordena rota para prioridades altas primeiro."""
    if len(route_coords) < 2:
        return route_coords
    
    # [CORREÇÃO] Se a cidade do depósito estiver na rota, garantir que seja a primeira
    if depot_coord and depot_coord in route_coords:
        # Remover depósito da lista temporariamente
        route_without_depot = [c for c in route_coords if c != depot_coord]
        # Ordenar o resto por prioridade
        city_priority = {}
        for coord in route_without_depot:
            city = coord_to_city.get(coord)
            if city and city in deliveries_by_city:
                priorities = [d.priority for d in deliveries_by_city[city]]
                city_priority[coord] = min(priorities) if priorities else 2
            else:
                city_priority[coord] = 2
        sorted_route = sorted(route_without_depot, key=lambda c: city_priority[c])
        # Colocar depósito no início
        return [depot_coord] + sorted_route
    
    # Calcular prioridade de cada cidade
    city_priority = {}
    for coord in route_coords:
        city = coord_to_city.get(coord)
        if city and city in deliveries_by_city:
            priorities = [d.priority for d in deliveries_by_city[city]]
            city_priority[coord] = min(priorities) if priorities else 2
        else:
            city_priority[coord] = 2
    
    # Ordenar por prioridade (0, 1, 2)
    return sorted(route_coords, key=lambda c: city_priority[c])


def force_feasibility(solution, vehicles, depot_coord, coord_to_city, deliveries_by_city, distance_lookup):
    """Força viabilidade redistribuindo cidades."""
    # print("  Aplicando correções de viabilidade...")
    
    # Coletar todas as cidades
    all_cities = []
    for route in solution:
        all_cities.extend(route.route)
    
    # Ordenar veículos por capacidade (maiores primeiro)
    vehicles_sorted = sorted(vehicles, key=lambda v: v.max_weight, reverse=True)
    
    # Algoritmo First-Fit
    new_solution = []
    remaining_cities = all_cities[:]
    
    for vehicle in vehicles_sorted:
        if not remaining_cities:
            break
        
        current_route = []
        current_weight = 0.0
        
        # Adicionar cidades que cabem
        for city in remaining_cities[:]:
            city_weight = calculate_route_weight([city], coord_to_city, deliveries_by_city)
            
            if current_weight + city_weight <= vehicle.max_weight:
                current_route.append(city)
                current_weight += city_weight
                remaining_cities.remove(city)
        
        if current_route:
            new_route = VRPRoute(vehicle, current_route, depot_coord)
            new_route.calculate_stats(coord_to_city, deliveries_by_city, distance_lookup)
            new_solution.append(new_route)
    
    # Se sobrou cidades, distribuir
    while remaining_cities and new_solution:
        city = remaining_cities.pop(0)
        # Encontrar rota com mais espaço
        best_route = None
        best_space = -1
        
        for route in new_solution:
            city_weight = calculate_route_weight([city], coord_to_city, deliveries_by_city)
            space = route.vehicle.max_weight - route.total_weight
            
            if space >= city_weight and space > best_space:
                best_space = space
                best_route = route
        
        if best_route:
            best_route.route.append(city)
            best_route.calculate_stats(coord_to_city, deliveries_by_city, distance_lookup)
        else:
            # Criar nova rota se necessário
            available_vehicles = [v for v in vehicles_sorted 
                                if v.vehicle_id not in {r.vehicle.vehicle_id for r in new_solution}]
            if available_vehicles:
                new_route = VRPRoute(available_vehicles[0], [city], depot_coord)
                new_route.calculate_stats(coord_to_city, deliveries_by_city, distance_lookup)
                new_solution.append(new_route)
    
    return new_solution


# =========================
# ALGORITMO PRINCIPAL
# =========================
# [MELHORIA] Adicionar validação de integridade - garante que todas as cidades estão presentes e sem duplicatas
def validate_vrp_solution(solution, all_cities_coords):
    """
    Valida se todas as cidades estão presentes exatamente uma vez na solução.
    Retorna (é_válida, cidades_faltando, tem_duplicatas)
    """
    cities_in_solution = []
    for route in solution:
        cities_in_solution.extend(route.route)
    
    expected_cities = set(all_cities_coords)
    cities_in_solution_set = set(cities_in_solution)
    
    missing_cities = expected_cities - cities_in_solution_set
    has_duplicates = len(cities_in_solution) != len(cities_in_solution_set)
    
    return len(missing_cities) == 0 and not has_duplicates, missing_cities, has_duplicates


def solve_vrp(cities_coords, coord_to_city, deliveries_by_city,
             distance_lookup, vehicles, ga_config,
             depot_city=None, generations_per_route=150):
    
    # Configurações
    options = VRPOptions()
    
    # Depósito
    depot_coord = None
    if depot_city:
        for coord, city in coord_to_city.items():
            if city == depot_city:
                depot_coord = coord
                break
        # print(f"🏭 Depósito: {depot_city}")
    
    # [CORREÇÃO] Se o depósito tem entregas, ele deve estar na rota mas sempre como primeira cidade
    # Não remover de cities_coords, mas garantir que seja sempre colocado no início
    all_cities_set = set(cities_coords)
    
    # Ordenar veículos por capacidade
    vehicles_sorted = sorted(vehicles, key=lambda v: v.max_weight, reverse=True)
    
    # População inicial
    population = []
    cost_history = []
    distance_history = []
    
    for i in range(POPULATION_SIZE):
        # Diversidade na população inicial
        if i < POPULATION_SIZE // 3:
            # 1 veículo grande
            route_coords = cities_coords[:]
            # [CORREÇÃO] Se depósito tem entregas, colocá-lo no início
            if depot_coord and depot_coord in route_coords:
                route_coords.remove(depot_coord)
                route_coords.insert(0, depot_coord)
            solution = [VRPRoute(vehicles_sorted[0], route_coords, depot_coord)]
        elif i < 2 * POPULATION_SIZE // 3:
            # 2 veículos
            if len(vehicles_sorted) >= 2:
                split_point = len(cities_coords) // 2
                route1 = cities_coords[:split_point]
                route2 = cities_coords[split_point:]
                # [CORREÇÃO] Se depósito tem entregas, colocá-lo no início da primeira rota
                if depot_coord and depot_coord in route1:
                    route1.remove(depot_coord)
                    route1.insert(0, depot_coord)
                elif depot_coord and depot_coord in route2:
                    route2.remove(depot_coord)
                    route2.insert(0, depot_coord)
                solution = [
                    VRPRoute(vehicles_sorted[0], route1, depot_coord),
                    VRPRoute(vehicles_sorted[1], route2, depot_coord)
                ]
            else:
                route_coords = cities_coords[:]
                if depot_coord and depot_coord in route_coords:
                    route_coords.remove(depot_coord)
                    route_coords.insert(0, depot_coord)
                solution = [VRPRoute(vehicles_sorted[0], route_coords, depot_coord)]
        else:
            # Aleatório
            solution = build_random_solution(cities_coords, vehicles_sorted, depot_coord)
        
        population.append(solution)
    
    # Evolução
    best_solution = None
    best_fitness = float('inf')
    stagnation_counter = 0
    feasible_found = False
    last_best_fitness = float('inf')
    
    # [MELHORIA] Melhorar critérios de parada - usar limite máximo configurável e detectar convergência
    max_generations = min(generations_per_route, VRP_MAX_GENERATIONS)
    
    for gen in range(max_generations):
        # 1. Avaliar população
        fitness_scores = []
        feasible_count = 0
        
        for solution in population:
            # Calcular stats
            for route in solution:
                route.calculate_stats(coord_to_city, deliveries_by_city, distance_lookup)
            
            # Fitness
            fitness = calculate_vrp_fitness(
                solution, coord_to_city, deliveries_by_city,
                distance_lookup, all_cities_set, options, gen, generations_per_route
            )
            fitness_scores.append((fitness, solution))
            
            # Contar soluções viáveis
            is_feasible = all(route.is_feasible for route in solution)
            if is_feasible:
                feasible_count += 1
        
        # Ordenar
        fitness_scores.sort(key=lambda x: x[0])
        
        # 2. Verificar melhoria
        current_best = fitness_scores[0][0]
        improvement = last_best_fitness - current_best
        
        if current_best < best_fitness:
            best_fitness = current_best
            best_solution = deepcopy(fitness_scores[0][1])
            stagnation_counter = 0
            
            # [MELHORIA] Adicionar validação de integridade - verifica se todas as cidades estão presentes
            is_valid, missing, has_dup = validate_vrp_solution(best_solution, all_cities_set)
            if not is_valid:
                # Corrigir se necessário
                if missing or has_dup:
                    best_solution = force_feasibility(best_solution, vehicles_sorted, depot_coord,
                                                    coord_to_city, deliveries_by_city, distance_lookup)
            
            # Verificar viabilidade
            is_best_feasible = all(route.is_feasible for route in best_solution)
            if is_best_feasible and not feasible_found:
                feasible_found = True
            
            if gen % 10 == 0 or gen < 20:
                active = sum(1 for r in best_solution if r.route)
                total_cities = sum(len(r.route) for r in best_solution)
                feasible_status = "✅" if is_best_feasible else "❌"
        else:
            stagnation_counter += 1
        
        # [MELHORIA] Melhorar critérios de parada - detectar convergência baseado em threshold configurável
        if improvement < VRP_CONVERGENCE_THRESHOLD:
            if stagnation_counter >= VRP_CONVERGENCE_GENERATIONS:
                # Convergência detectada - parar evolução
                break
        
        last_best_fitness = current_best
        
        # Registrar histórico
        if best_solution:
            total_cost = sum(r.total_cost for r in best_solution if r.route)
            total_distance = sum(r.total_distance for r in best_solution if r.route)
            cost_history.append(total_cost)
            distance_history.append(total_distance)
        
        # 3. Relatório periódico
        # if gen % 20 == 0:
        #     print(f"   Viáveis: {feasible_count}/{POPULATION_SIZE} | Estagnação: {stagnation_counter}")
        
        # 4. Estratégia de escape se estagnado em inviáveis
        if stagnation_counter > 30 and not feasible_found:            
            
            # Nova população mais conservadora
            new_population = []
            for i in range(POPULATION_SIZE):
                # Usar mais veículos para garantir viabilidade
                num_vehicles = min(len(vehicles_sorted), max(2, len(cities_coords) // 2))
                selected = vehicles_sorted[:num_vehicles]
                solution = [VRPRoute(v, [], depot_coord) for v in selected]
                
                # Distribuir igualmente
                cities_to_distribute = cities_coords[:]
                # [CORREÇÃO] Se depósito tem entregas, removê-lo temporariamente
                depot_in_list = False
                if depot_coord and depot_coord in cities_to_distribute:
                    cities_to_distribute.remove(depot_coord)
                    depot_in_list = True
                
                for idx, coord in enumerate(cities_to_distribute):
                    route_idx = idx % len(solution)
                    solution[route_idx].route.append(coord)
                
                # [CORREÇÃO] Colocar depósito no início da primeira rota
                if depot_in_list and solution:
                    solution[0].route.insert(0, depot_coord)
                
                new_population.append(solution)
            
            population = new_population
            stagnation_counter = 0
            continue
        
        # 5. Parada se viável e estagnado
        if feasible_found and stagnation_counter > 40:
            # print(f"🏁 Parando na geração {gen} (solução viável encontrada)")
            break
        
        # 6. Seleção
        # [MELHORIA] Tornar elitismo configurável - usar ELITE_PERCENTAGE do config em vez de valor fixo
        elite_size = max(2, int(POPULATION_SIZE * ELITE_PERCENTAGE))
        new_population = [s[1] for s in fitness_scores[:elite_size]]
        
        # 7. Cruzamento e mutação
        while len(new_population) < POPULATION_SIZE:
            # [MELHORIA] Integrar ga_config - usar operador de seleção configurado pelo usuário quando disponível
            if ga_config and "selection_fn" in ga_config:
                try:
                    # Converter para formato esperado pela seleção do ga_config
                    population_list = [s[1] for s in fitness_scores]
                    fitness_list = [s[0] for s in fitness_scores]
                    parent1, parent2 = ga_config["selection_fn"](population_list, fitness_list)
                except Exception:
                    # Fallback para torneio se houver erro na seleção configurada
                    tournament = []
                    for _ in range(5):
                        candidate = random.choice(fitness_scores[:50])
                        is_feasible = all(route.is_feasible for route in candidate[1])
                        score = candidate[0] * (0.3 if is_feasible else 1.0)
                        tournament.append((score, candidate[1]))
                    tournament.sort(key=lambda x: x[0])
                    parent1 = tournament[0][1]
                    parent2 = tournament[1][1]
            else:
                # Torneio com preferência para viáveis (fallback quando ga_config não disponível)
                tournament = []
                for _ in range(5):
                    candidate = random.choice(fitness_scores[:50])
                    is_feasible = all(route.is_feasible for route in candidate[1])
                    score = candidate[0] * (0.3 if is_feasible else 1.0)  # Bônus para viáveis
                    tournament.append((score, candidate[1]))
                
                tournament.sort(key=lambda x: x[0])
                parent1 = tournament[0][1]
                parent2 = tournament[1][1]
            
            # Cruzamento
            child = adaptive_crossover(parent1, parent2, depot_coord, options, gen, generations_per_route)
            
            # Mutação especial
            child = feasibility_mutation(child, depot_coord, options, gen,
                                        coord_to_city, deliveries_by_city, distance_lookup)
            
            new_population.append(child)
        
        population = new_population
    
    # OTIMIZAÇÃO FINAL
    # print("\n🔧 Fase final de otimização...")
    
    if best_solution:
        # Verificar viabilidade
        is_feasible = all(route.is_feasible for route in best_solution)
        
        if not is_feasible:
            # print("⚠️  Aplicando correções de viabilidade...")
            best_solution = force_feasibility(best_solution, vehicles_sorted, depot_coord,
                                            coord_to_city, deliveries_by_city, distance_lookup)
        
        # Otimizar ordem por prioridade
        for route in best_solution:
            if route.route:
                route.route = optimize_route_order(route.route, coord_to_city, deliveries_by_city, depot_coord)
                route.calculate_stats(coord_to_city, deliveries_by_city, distance_lookup)
    
    final_solution = [r for r in best_solution if r.route] if best_solution else []
    
    # [MELHORIA] Adicionar validação de cobertura - verificar antes de retornar se todas as cidades estão presentes
    if final_solution:
        is_valid, missing, has_dup = validate_vrp_solution(final_solution, all_cities_set)
        if not is_valid:
            # Corrigir se necessário antes de retornar
            final_solution = force_feasibility(final_solution, vehicles_sorted, depot_coord,
                                             coord_to_city, deliveries_by_city, distance_lookup)
    
    # RELATÓRIO FINAL
    # print_final_report(final_solution, cities_coords, coord_to_city, deliveries_by_city)
    
    return final_solution, {
        "cost_history": cost_history,
        "distance_history": distance_history,
        "attempts": []
    }


def print_final_report(solution, cities_coords, coord_to_city, deliveries_by_city):
    """Imprime relatório final."""
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*60}")
    
    if not solution:
        print("❌ NENHUMA SOLUÇÃO ENCONTRADA")
        return
    
    total_cost = sum(r.total_cost for r in solution)
    total_distance = sum(r.total_distance for r in solution)
    total_weight = sum(r.total_weight for r in solution)
    
    print(f"🚛 Veículos utilizados: {len(solution)}")
    print(f"💰 Custo total: R$ {total_cost:.2f}")
    print(f"📏 Distância total: {total_distance:.1f} km")
    print(f"⚖️  Peso total: {total_weight:.1f} kg")
    
    # Verificação de viabilidade
    print(f"\n🔍 VERIFICAÇÃO DE VIABILIDADE:")
    all_feasible = True
    
    for i, route in enumerate(solution):
        weight_ok = route.total_weight <= route.vehicle.max_weight
        distance_ok = route.total_distance <= route.vehicle.max_distance
        
        status = "✅" if weight_ok and distance_ok else "❌"
        print(f"  Rota {i+1} ({route.vehicle.name}): {status}")
        
        if not weight_ok:
            print(f"    ⚠️  Peso: {route.total_weight:.1f}/{route.vehicle.max_weight} kg")
            all_feasible = False
        
        if not distance_ok:
            print(f"    ⚠️  Distância: {route.total_distance:.1f}/{route.vehicle.max_distance} km")
            all_feasible = False
    
    if all_feasible:
        print(f"\n🎉 SOLUÇÃO COMPLETAMENTE VIÁVEL!")
    else:
        print(f"\n⚠️  SOLUÇÃO COM VIOLAÇÕES")
    
    # Análise de prioridade
    print(f"\n🎯 ANÁLISE DE PRIORIDADE:")
    for i, route in enumerate(solution):
        priorities = []
        for coord in route.route:
            city = coord_to_city.get(coord)
            if city and city in deliveries_by_city:
                priorities.extend([d.priority for d in deliveries_by_city[city]])
        
        if priorities:
            p0 = priorities.count(0)
            p1 = priorities.count(1)
            p2 = priorities.count(2)
            print(f"  Rota {i+1}: P0={p0}, P1={p1}, P2={p2}")
            
            # Verificar posição das prioridades 0
            if p0 > 0:
                positions = []
                for idx, coord in enumerate(route.route):
                    city = coord_to_city.get(coord)
                    if city and city in deliveries_by_city:
                        for d in deliveries_by_city[city]:
                            if d.priority == 0:
                                positions.append(idx / len(route.route))
                
                if positions:
                    avg_pos = sum(positions) / len(positions)
                    status = "BOA" if avg_pos < 0.3 else "RAZOÁVEL" if avg_pos < 0.6 else "RUIM"
                    print(f"    Posição média P0: {avg_pos:.2f} ({status})")
    
    print(f"\n📍 Cobertura: {sum(len(r.route) for r in solution)}/{len(cities_coords)} cidades")