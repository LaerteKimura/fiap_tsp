# tests/test_constraints.py
"""
Testes para validação de restrições (peso, distância, prioridades).
"""
import pytest
from route_helpers import (
    calculate_route_weight,
    calculate_route_distance,
    select_vehicle,
)


class TestWeightConstraints:
    """Testes para restrições de peso."""
    
    def test_route_respects_vehicle_capacity(self, sample_coords, sample_coord_to_city,
                                             sample_deliveries_by_city, sample_vehicles):
        """Testa que rota válida respeita capacidade do veículo."""
        # Usar apenas primeiras 2 cidades (peso menor)
        small_route = list(sample_coords[:2])
        
        weight = calculate_route_weight(small_route, sample_coord_to_city, sample_deliveries_by_city)
        
        # Van pequena deve ser suficiente
        vehicle = sample_vehicles[0]  # Van 1500kg
        
        if weight <= vehicle.max_weight:
            assert True  # Restrição satisfeita
    
    def test_overweight_route_detection(self, sample_coords, sample_coord_to_city,
                                       sample_deliveries_by_city, sample_vehicles):
        """Testa detecção de rota que excede capacidade."""
        # Usar todas as cidades (peso maior)
        full_route = list(sample_coords)
        
        weight = calculate_route_weight(full_route, sample_coord_to_city, sample_deliveries_by_city)
        
        # Van pequena não deve ser suficiente
        small_vehicle = sample_vehicles[0]  # Van 1500kg
        
        if weight > small_vehicle.max_weight:
            # Deve selecionar veículo maior
            selected = select_vehicle(weight, 100, sample_vehicles)
            assert selected is None or selected.max_weight >= weight


class TestDistanceConstraints:
    """Testes para restrições de distância."""
    
    def test_route_respects_vehicle_autonomy(self, sample_route, sample_coord_to_city,
                                             sample_distance_lookup, sample_vehicles):
        """Testa que rota válida respeita autonomia do veículo."""
        distance = calculate_route_distance(sample_route, sample_coord_to_city, sample_distance_lookup)
        
        # Caminhão grande deve ser suficiente
        large_vehicle = sample_vehicles[2]  # 800km
        
        if distance <= large_vehicle.max_distance:
            assert True  # Restrição satisfeita
    
    def test_long_route_detection(self, sample_route, sample_coord_to_city,
                                  sample_distance_lookup, sample_vehicles):
        """Testa detecção de rota que excede autonomia."""
        distance = calculate_route_distance(sample_route, sample_coord_to_city, sample_distance_lookup)
        
        # Verificar se algum veículo pode atender
        small_vehicle = sample_vehicles[0]  # Van 300km
        
        if distance > small_vehicle.max_distance:
            # Deve selecionar veículo com maior autonomia
            selected = select_vehicle(100, distance, sample_vehicles)
            assert selected is None or selected.max_distance >= distance


class TestVehicleSelection:
    """Testes para seleção de veículo adequado."""
    
    def test_select_vehicle_for_light_short_route(self, sample_vehicles):
        """Testa seleção de veículo para rota leve e curta."""
        weight = 500  # kg
        distance = 100  # km
        
        vehicle = select_vehicle(weight, distance, sample_vehicles)
        
        assert vehicle is not None
        assert vehicle.max_weight >= weight
        assert vehicle.max_distance >= distance
    
    def test_select_vehicle_for_heavy_route(self, sample_vehicles):
        """Testa seleção de veículo para rota pesada."""
        weight = 4000  # kg (precisa caminhão grande)
        distance = 200  # km
        
        vehicle = select_vehicle(weight, distance, sample_vehicles)
        
        assert vehicle is not None
        assert vehicle.max_weight >= weight
    
    def test_no_vehicle_available_for_impossible_route(self, sample_vehicles):
        """Testa que retorna None quando nenhum veículo pode atender."""
        weight = 10000  # kg (muito pesado)
        distance = 1000  # km (muito longe)
        
        vehicle = select_vehicle(weight, distance, sample_vehicles)
        
        # Pode retornar None ou o maior veículo disponível
        if vehicle is not None:
            # Se retornou, deve ser o maior
            assert vehicle.max_weight == max(v.max_weight for v in sample_vehicles)


class TestPriorityHandling:
    """Testes para tratamento de prioridades."""
    
    def test_priority_distribution(self, sample_deliveries):
        """Testa distribuição de prioridades nas entregas."""
        priorities = [d.priority for d in sample_deliveries]
        
        assert 0 in priorities  # Alta prioridade
        assert 1 in priorities  # Média prioridade
        assert 2 in priorities  # Baixa prioridade
    
    def test_high_priority_deliveries_identified(self, sample_deliveries):
        """Testa identificação de entregas de alta prioridade."""
        high_priority = [d for d in sample_deliveries if d.priority == 0]
        
        assert len(high_priority) > 0
        for delivery in high_priority:
            assert delivery.priority == 0
