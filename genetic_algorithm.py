import random
import math
from typing import Tuple

# =========================
# CONSTANTS
# =========================

CAPACITY_PENALTY = 10_000
DISTANCE_PENALTY = 10_000

PRIORITY_WEIGHTS = {
    0: 1000,
    1: 300,
    2: 50
}

# =========================
# POPULATION
# =========================

def generate_random_population(cities_locations, population_size):
    population = []
    for _ in range(population_size):
        individual = cities_locations[:]
        random.shuffle(individual)
        population.append(individual)
    return population


# =========================
# DISTANCE
# =========================

def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def calculate_route_distance(route, coord_to_city, distance_lookup):
    distance = 0.0
    for i in range(len(route)):
        city1 = coord_to_city[route[i]]
        city2 = coord_to_city[route[(i + 1) % len(route)]]
        distance += distance_lookup[(city1, city2)]
    return distance




# =========================
# ROUTE WEIGHT
# =========================

def calculate_route_weight(route, coord_to_city, deliveries_by_city):
    total_weight = 0.0
    for coord in route:
        city = coord_to_city[coord]
        for d in deliveries_by_city.get(city, []):
            total_weight += d.total_weight
    return total_weight


# =========================
# PRIORITY
# =========================

def calculate_priority_penalty(route, coord_to_city, deliveries_by_city):
    penalty = 0.0
    route_size = len(route)

    for position, coord in enumerate(route):
        city = coord_to_city[coord]
        for d in deliveries_by_city.get(city, []):
            lateness = position / route_size
            penalty += lateness * PRIORITY_WEIGHTS[d.priority]

    return penalty


# =========================
# FITNESS
# =========================

def calculate_fitness(
    route,
    coord_to_city,
    deliveries_by_city,
    vehicles,
    distance_lookup,
    priority_weight=1.0
):
    # -----------------------
    # DISTANCE
    # -----------------------
    route_distance = calculate_route_distance(
        route,
        coord_to_city,
        distance_lookup
    )



    # -----------------------
    # PRIORITY
    # -----------------------
    priority_cost = (
        calculate_priority_penalty(route, coord_to_city, deliveries_by_city)
        * priority_weight
    )

    # -----------------------
    # WEIGHT
    # -----------------------
    route_weight = calculate_route_weight(
        route,
        coord_to_city,
        deliveries_by_city
    )

    # -----------------------
    # VEHICLE CONSTRAINTS
    # -----------------------
    vehicle_penalty = CAPACITY_PENALTY + DISTANCE_PENALTY

    for v in vehicles:
        if (
            route_weight <= v.max_weight
            and route_distance <= v.max_distance
        ):
            vehicle_penalty = 0
            break

    # -----------------------
    # FINAL FITNESS
    # -----------------------
    return route_distance + priority_cost + vehicle_penalty


# =========================
# CROSSOVER
# =========================

def crossover_ox(parent1, parent2):
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


def crossover_pmx(parent1, parent2):
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


def crossover_cx(parent1, parent2):
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
# MUTATION
# =========================

def mutate_swap(individual, probability):
    individual = individual[:]
    for i in range(len(individual)):
        if random.random() < probability:
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]
    return individual


def mutate_inversion(individual, probability):
    individual = individual[:]
    if random.random() < probability:
        i, j = sorted(random.sample(range(len(individual)), 2))
        individual[i:j] = reversed(individual[i:j])
    return individual


def mutate_scramble(individual, probability):
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
# SELECTION
# =========================

def selection_tournament(population, fitness, k=3):
    selected = random.sample(list(zip(population, fitness)), k)
    selected.sort(key=lambda x: x[1])
    return selected[0][0], selected[1][0]


def selection_roulette(population, fitness):
    weights = [1 / f for f in fitness]
    return random.choices(population, weights=weights, k=2)


def selection_rank(population, fitness):
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
# SORT
# =========================

def sort_population(population, fitness):
    combined = list(zip(population, fitness))
    combined.sort(key=lambda x: x[1])
    pop, fit = zip(*combined)
    return list(pop), list(fit)
