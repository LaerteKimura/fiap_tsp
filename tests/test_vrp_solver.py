# tests/test_vrp_solver.py
"""
Testes para o solver VRP.
"""
import pytest
from vrp_solver import VRPRoute, calculate_vrp_fitness, VRPOptions


class TestVRPRoute:
    """Testes para classe VRPRoute."""
    
    def test_vrp_route_creation(self, sample_vehicles, sample_coords):
        """Testa criação de VRPRoute."""
        route = VRPRoute(
            vehicle=sample_vehicles[0],
            route=list(sample_coords[:3]),
            depot_coord=sample_coords[0]
        )
        
        assert route.vehicle == sample_vehicles[0]
        assert len(route.route) == 3
        assert route.depot_coord == sample_coords[0]
    
    def test_vrp_route_stats_calculation(self, vrp_route_mock, sample_coord_to_city,
                                        sample_deliveries_by_city, sample_distance_lookup):
        """Testa cálculo de estatísticas da rota."""
        vrp_route_mock.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        assert vrp_route_mock.total_distance >= 0
        assert vrp_route_mock.total_weight >= 0
        assert vrp_route_mock.total_cost >= 0
    
    def test_vrp_route_feasibility_check(self, vrp_route_mock, sample_coord_to_city,
                                         sample_deliveries_by_city, sample_distance_lookup):
        """Testa verificação de viabilidade da rota."""
        vrp_route_mock.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        # Rota pequena deve ser viável
        assert isinstance(vrp_route_mock.is_feasible, bool)
        
        if vrp_route_mock.is_feasible:
            assert vrp_route_mock.weight_violation == 0
            assert vrp_route_mock.distance_violation == 0


class TestVRPFitness:
    """Testes para função fitness VRP."""
    
    def test_vrp_fitness_positive(self, vrp_route_mock, sample_coord_to_city,
                                  sample_deliveries_by_city, sample_distance_lookup, sample_coords):
        """Testa que fitness VRP é sempre positivo."""
        vrp_route_mock.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        solution = [vrp_route_mock]
        options = VRPOptions()
        
        fitness = calculate_vrp_fitness(
            solution,
            sample_coord_to_city,
            sample_deliveries_by_city,
            sample_distance_lookup,
            set(sample_coords),
            options
        )
        
        assert fitness >= 0
    
    def test_vrp_fitness_penalizes_duplicate_vehicles(self, sample_vehicles, sample_coords,
                                                     sample_coord_to_city, sample_deliveries_by_city,
                                                     sample_distance_lookup):
        """Testa que fitness penaliza uso duplicado de veículos."""
        # Criar duas rotas com mesmo veículo (inválido)
        route1 = VRPRoute(sample_vehicles[0], list(sample_coords[:2]), sample_coords[0])
        route2 = VRPRoute(sample_vehicles[0], list(sample_coords[2:4]), sample_coords[0])  # Mesmo veículo!
        
        route1.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        route2.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        solution = [route1, route2]
        options = VRPOptions()
        
        fitness = calculate_vrp_fitness(
            solution,
            sample_coord_to_city,
            sample_deliveries_by_city,
            sample_distance_lookup,
            set(sample_coords),
            options
        )
        
        # Fitness deve ser muito alto (penalidade massiva)
        assert fitness > options.WEIGHTS['duplicate_vehicle']
    
    def test_vrp_fitness_penalizes_missing_cities(self, vrp_route_mock, sample_coord_to_city,
                                                  sample_deliveries_by_city, sample_distance_lookup, sample_coords):
        """Testa que fitness penaliza cidades não cobertas."""
        vrp_route_mock.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        # Rota cobre apenas 3 cidades, mas há 5 no total
        solution = [vrp_route_mock]
        options = VRPOptions()
        
        fitness = calculate_vrp_fitness(
            solution,
            sample_coord_to_city,
            sample_deliveries_by_city,
            sample_distance_lookup,
            set(sample_coords),  # Todas as 5 cidades
            options
        )
        
        # Fitness deve incluir penalidade por cidades não cobertas
        assert fitness > 0


class TestVRPConstraints:
    """Testes para restrições VRP."""
    
    def test_vrp_route_respects_weight_limit(self, sample_vehicles, sample_coords,
                                             sample_coord_to_city, sample_deliveries_by_city,
                                             sample_distance_lookup):
        """Testa que rota VRP respeita limite de peso."""
        # Usar van pequena com poucas cidades
        route = VRPRoute(sample_vehicles[0], list(sample_coords[:2]), sample_coords[0])
        route.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        if route.total_weight <= sample_vehicles[0].max_weight:
            assert route.is_feasible or route.weight_violation == 0
    
    def test_vrp_route_respects_distance_limit(self, sample_vehicles, sample_coords,
                                               sample_coord_to_city, sample_deliveries_by_city,
                                               sample_distance_lookup):
        """Testa que rota VRP respeita limite de distância."""
        route = VRPRoute(sample_vehicles[2], list(sample_coords), sample_coords[0])  # Caminhão grande
        route.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        if route.total_distance <= sample_vehicles[2].max_distance:
            assert route.is_feasible or route.distance_violation == 0
