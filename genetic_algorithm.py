import random
import math
from typing import Tuple, List, Dict

# =========================
# CONSTANTS
# =========================

CAPACITY_PENALTY = 10_000
DISTANCE_PENALTY = 10_000

PRIORITY_WEIGHTS = {
    0: 1000,  # Alta prioridade
    1: 300,   # Média prioridade
    2: 50     # Baixa prioridade
}

# =========================
# POPULATION
# =========================

def generate_random_population(cities_locations: List[Tuple[int, int]], 
                              population_size: int) -> List[List[Tuple[int, int]]]:
    """
    Gera população inicial aleatória.
    """
    population = []
    base_list = cities_locations[:]
    
    for _ in range(population_size):
        individual = base_list[:]
        random.shuffle(individual)
        population.append(individual)
    
    return population


# =========================
# DISTANCE CALCULATION
# =========================

def calculate_route_distance(route: List[Tuple[int, int]], 
                            coord_to_city: Dict[Tuple[int, int], str],
                            distance_lookup: Dict[Tuple[str, str], float]) -> float:
    """
    Calcula distância total da rota usando distâncias REAIS (km).
    """
    if len(route) < 2:
        return 0.0
    
    total_distance = 0.0
    
    for i in range(len(route)):
        city1 = coord_to_city[route[i]]
        city2 = coord_to_city[route[(i + 1) % len(route)]]
        
        # Tenta ambas as direções (A->B ou B->A)
        distance = distance_lookup.get((city1, city2))
        if distance is None:
            distance = distance_lookup.get((city2, city1), 0.0)
        
        total_distance += distance
    
    return total_distance


# =========================
# ROUTE WEIGHT
# =========================

def calculate_route_weight(route: List[Tuple[int, int]], 
                          coord_to_city: Dict[Tuple[int, int], str],
                          deliveries_by_city: Dict[str, List]) -> float:
    """
    Calcula peso total da rota em kg.
    """
    total_weight = 0.0
    
    for coord in route:
        city = coord_to_city[coord]
        deliveries = deliveries_by_city.get(city, [])
        for d in deliveries:
            total_weight += d.total_weight
    
    return total_weight


# =========================
# PRIORITY PENALTY
# =========================

def calculate_priority_penalty(route: List[Tuple[int, int]], 
                              coord_to_city: Dict[Tuple[int, int], str],
                              deliveries_by_city: Dict[str, List]) -> float:
    """
    Calcula penalidade por prioridade baseada na posição na rota.
    Entregas de alta prioridade devem vir primeiro.
    """
    penalty = 0.0
    route_size = len(route)
    
    if route_size == 0:
        return 0.0
    
    for position, coord in enumerate(route):
        city = coord_to_city[coord]
        deliveries = deliveries_by_city.get(city, [])
        
        for d in deliveries:
            # Quanto mais tarde na rota, maior a penalidade
            # Para prioridade 0 (alta), penalidade máxima se estiver no final
            lateness = position / route_size
            penalty_weight = PRIORITY_WEIGHTS.get(d.priority, 50)
            penalty += lateness * penalty_weight
    
    return penalty


# =========================
# VEHICLE FEASIBILITY
# =========================

def check_vehicle_feasibility(route_weight: float, 
                             route_distance: float,
                             vehicles: List) -> Tuple[bool, float]:
    """
    Verifica se algum veículo pode atender a rota.
    Retorna (viável, custo_adicional)
    """
    # Procura veículo viável
    for v in vehicles:
        if route_weight <= v.max_weight and route_distance <= v.max_distance:
            return True, 0.0
    
    # Nenhum veículo viável - calcula penalidade
    weight_penalty = 0.0
    distance_penalty = 0.0
    
    # Verifica qual restrição é violada
    min_weight_capacity = min(v.max_weight for v in vehicles)
    min_distance_capacity = min(v.max_distance for v in vehicles)
    
    if route_weight > min_weight_capacity:
        excess_weight = route_weight - min_weight_capacity
        weight_penalty = excess_weight * 100  # Penalidade por kg excedente
    
    if route_distance > min_distance_capacity:
        excess_distance = route_distance - min_distance_capacity
        distance_penalty = excess_distance * 10  # Penalidade por km excedente
    
    return False, weight_penalty + distance_penalty


# =========================
# FITNESS FUNCTION
# =========================

def calculate_fitness(route: List[Tuple[int, int]],
                     coord_to_city: Dict[Tuple[int, int], str],
                     deliveries_by_city: Dict[str, List],
                     vehicles: List,
                     distance_lookup: Dict[Tuple[str, str], float],
                     priority_weight: float = 1.0,
                     distance_weight: float = 1.0) -> float:
    """
    Calcula fitness de uma rota.
    Menor fitness é melhor.
    """
    # -----------------------
    # DISTÂNCIA REAL
    # -----------------------
    route_distance = calculate_route_distance(
        route,
        coord_to_city,
        distance_lookup
    )
    
    # -----------------------
    # PESO TOTAL
    # -----------------------
    route_weight = calculate_route_weight(
        route,
        coord_to_city,
        deliveries_by_city
    )
    
    # -----------------------
    # PRIORIDADE
    # -----------------------
    priority_cost = calculate_priority_penalty(
        route,
        coord_to_city,
        deliveries_by_city
    )
    
    # -----------------------
    # VIABILIDADE DO VEÍCULO
    # -----------------------
    is_feasible, vehicle_penalty = check_vehicle_feasibility(
        route_weight,
        route_distance,
        vehicles
    )
    
    # -----------------------
    # FITNESS FINAL
    # -----------------------
    fitness = (
        route_distance * distance_weight +
        priority_cost * priority_weight +
        vehicle_penalty
    )
    
    # Adiciona penalidade grande se não for viável
    if not is_feasible:
        fitness += CAPACITY_PENALTY + DISTANCE_PENALTY
    
    return fitness


# =========================
# CROSSOVER OPERATORS
# =========================

def crossover_ox(parent1: List, parent2: List) -> List:
    """
    Order Crossover (OX)
    """
    size = len(parent1)
    a, b = sorted(random.sample(range(size), 2))
    
    child = [None] * size
    child[a:b] = parent1[a:b]
    
    idx = b
    for gene in parent2:
        if gene not in child:
            if idx >= size:
                idx = 0
            child[idx] = gene
            idx += 1
    
    return child


def crossover_pmx(parent1: List, parent2: List) -> List:
    """
    Partially Mapped Crossover (PMX)
    """
    size = len(parent1)
    a, b = sorted(random.sample(range(size), 2))
    
    child = [None] * size
    child[a:b] = parent1[a:b]
    
    for i in range(a, b):
        if parent2[i] not in child:
            val = parent2[i]
            idx = i
            
            while True:
                mapped = parent1[idx]
                idx = parent2.index(mapped)
                if child[idx] is None:
                    child[idx] = val
                    break
    
    for i in range(size):
        if child[i] is None:
            child[i] = parent2[i]
    
    return child


def crossover_cx(parent1: List, parent2: List) -> List:
    """
    Cycle Crossover (CX)
    """
    size = len(parent1)
    child = [None] * size
    index = 0
    
    while None in child:
        if child[index] is not None:
            index += 1
            continue
        
        start = index
        while True:
            child[index] = parent1[index]
            val = parent2[index]
            index = parent1.index(val)
            if index == start:
                break
    
    for i in range(size):
        if child[i] is None:
            child[i] = parent2[i]
    
    return child


CROSSOVER_TYPES = {
    "ox": crossover_ox,
    "pmx": crossover_pmx,
    "cx": crossover_cx
}


# =========================
# MUTATION OPERATORS
# =========================

def mutate_swap(individual: List, probability: float) -> List:
    """
    Swap Mutation: Troca duas posições aleatórias.
    """
    individual = individual[:]
    
    for i in range(len(individual)):
        if random.random() < probability:
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]
    
    return individual


def mutate_inversion(individual: List, probability: float) -> List:
    """
    Inversion Mutation: Inverte um segmento aleatório.
    """
    individual = individual[:]
    
    if random.random() < probability:
        i, j = sorted(random.sample(range(len(individual)), 2))
        individual[i:j] = reversed(individual[i:j])
    
    return individual


def mutate_scramble(individual: List, probability: float) -> List:
    """
    Scramble Mutation: Embaralha um segmento aleatório.
    """
    individual = individual[:]
    
    if random.random() < probability:
        i, j = sorted(random.sample(range(len(individual)), 2))
        subset = individual[i:j]
        random.shuffle(subset)
        individual[i:j] = subset
    
    return individual


MUTATION_TYPES = {
    "swap": mutate_swap,
    "inversion": mutate_inversion,
    "scramble": mutate_scramble
}


# =========================
# SELECTION OPERATORS
# =========================

def selection_tournament(population: List, fitness: List, k: int = 3) -> Tuple:
    """
    Tournament Selection.
    """
    selected = random.sample(list(zip(population, fitness)), k)
    selected.sort(key=lambda x: x[1])  # Ordena por fitness (menor é melhor)
    return selected[0][0], selected[1][0]


def selection_roulette(population: List, fitness: List) -> Tuple:
    """
    Roulette Wheel Selection.
    Converte fitness para probabilidade (menor fitness = maior chance).
    """
    # Inverte o fitness (porque menor é melhor)
    max_fitness = max(fitness) + 1
    inverted_fitness = [max_fitness - f for f in fitness]
    
    # Normaliza
    total = sum(inverted_fitness)
    if total == 0:
        weights = [1] * len(population)
    else:
        weights = [f / total for f in inverted_fitness]
    
    return random.choices(population, weights=weights, k=2)


def selection_rank(population: List, fitness: List) -> Tuple:
    """
    Rank Selection.
    """
    ranked = sorted(zip(population, fitness), key=lambda x: x[1])
    ranks = list(range(1, len(ranked) + 1))
    
    return random.choices(
        [r[0] for r in ranked],
        weights=ranks,
        k=2
    )


SELECTION_TYPES = {
    "tournament": selection_tournament,
    "roulette": selection_roulette,
    "rank": selection_rank
}


# =========================
# POPULATION MANAGEMENT
# =========================

def sort_population(population: List, fitness: List) -> Tuple:
    """
    Ordena população por fitness (ascendente - menor é melhor).
    """
    combined = list(zip(population, fitness))
    combined.sort(key=lambda x: x[1])
    
    sorted_pop = [ind for ind, _ in combined]
    sorted_fit = [fit for _, fit in combined]
    
    return sorted_pop, sorted_fit


