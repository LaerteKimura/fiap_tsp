# tests/test_genetic_algorithm.py
"""
Testes para os operadores do algoritmo genético.
"""
import pytest
from genetic_algorithm import (
    generate_random_population,
    calculate_route_distance,
    calculate_route_weight,
    calculate_fitness,
    sort_population,
)


class TestPopulationGeneration:
    """Testes para geração de população."""
    
    def test_generate_random_population_size(self, sample_coords):
        """Testa que população tem tamanho correto."""
        population_size = 10
        population = generate_random_population(sample_coords, population_size)
        
        assert len(population) == population_size
    
    def test_generate_random_population_valid_routes(self, sample_coords):
        """Testa que todas as rotas contêm todas as cidades."""
        population = generate_random_population(sample_coords, 5)
        
        for individual in population:
            assert len(individual) == len(sample_coords)
            assert set(individual) == set(sample_coords)


class TestDistanceCalculation:
    """Testes para cálculo de distância."""
    
    def test_route_distance_positive(self, sample_route, sample_coord_to_city, sample_distance_lookup):
        """Testa que distância é sempre positiva."""
        distance = calculate_route_distance(sample_route, sample_coord_to_city, sample_distance_lookup)
        assert distance >= 0
    
    def test_empty_route_distance(self, sample_coord_to_city, sample_distance_lookup):
        """Testa que rota vazia tem distância zero."""
        distance = calculate_route_distance([], sample_coord_to_city, sample_distance_lookup)
        assert distance == 0
    
    def test_single_city_route_distance(self, sample_coords, sample_coord_to_city, sample_distance_lookup):
        """Testa rota com uma única cidade."""
        single_route = [sample_coords[0]]
        distance = calculate_route_distance(single_route, sample_coord_to_city, sample_distance_lookup)
        assert distance == 0


class TestWeightCalculation:
    """Testes para cálculo de peso."""
    
    def test_route_weight_positive(self, sample_route, sample_coord_to_city, sample_deliveries_by_city):
        """Testa que peso é sempre positivo."""
        weight = calculate_route_weight(sample_route, sample_coord_to_city, sample_deliveries_by_city)
        assert weight >= 0
    
    def test_route_weight_sum(self, sample_coords, sample_coord_to_city, sample_deliveries_by_city):
        """Testa que peso da rota é soma dos pesos das entregas."""
        route = list(sample_coords[:3])  # Primeiras 3 cidades
        total_weight = calculate_route_weight(route, sample_coord_to_city, sample_deliveries_by_city)
        
        # Calcular peso esperado manualmente
        expected_weight = 0
        for coord in route:
            city = sample_coord_to_city.get(coord)
            if city and city in sample_deliveries_by_city:
                for delivery in sample_deliveries_by_city[city]:
                    expected_weight += delivery.total_weight
        
        assert abs(total_weight - expected_weight) < 0.01


class TestFitnessFunction:
    """Testes para função fitness."""
    
    def test_fitness_positive(self, sample_route, sample_coord_to_city, 
                              sample_deliveries_by_city, sample_vehicles, sample_distance_lookup):
        """Testa que fitness é sempre positivo."""
        fitness = calculate_fitness(
            sample_route,
            sample_coord_to_city,
            sample_deliveries_by_city,
            sample_vehicles,
            sample_distance_lookup,
            priority_weight=20
        )
        assert fitness >= 0
    
    def test_fitness_penalizes_overweight(self, sample_coords, sample_coord_to_city,
                                         sample_deliveries_by_city, sample_vehicles, sample_distance_lookup):
        """Testa que fitness penaliza rotas que excedem peso."""
        # Criar rota com todas as cidades (muito peso)
        route = list(sample_coords)
        
        fitness = calculate_fitness(
            route,
            sample_coord_to_city,
            sample_deliveries_by_city,
            sample_vehicles,
            sample_distance_lookup,
            priority_weight=20
        )
        
        # Fitness deve ser alto (pior) devido a penalidades
        assert fitness > 0


class TestSortPopulation:
    """Testes para ordenação de população."""
    
    def test_sort_population_orders_by_fitness(self, sample_route):
        """Testa que sort_population ordena por fitness."""
        population = [sample_route.copy() for _ in range(5)]
        fitness_scores = [100, 50, 75, 25, 90]
        
        sorted_pop, sorted_fit = sort_population(population, fitness_scores)
        
        assert len(sorted_pop) == len(population)
        assert len(sorted_fit) == len(fitness_scores)
        
        # Verificar se está ordenado (menor fitness primeiro - melhor)
        for i in range(len(sorted_fit) - 1):
            assert sorted_fit[i] <= sorted_fit[i + 1]
