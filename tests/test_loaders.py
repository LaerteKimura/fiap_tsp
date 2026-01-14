# tests/test_loaders.py
"""
Testes para os módulos de carregamento de dados.
"""
import pytest
import tempfile
import os


class TestDeliveryLoader:
    """Testes para o carregador de entregas."""
    
    def test_delivery_creation(self, sample_deliveries):
        """Testa criação de objetos Delivery."""
        delivery = sample_deliveries[0]
        
        assert delivery.id == 1
        assert delivery.medicine_name == "Paracetamol"
        assert delivery.quantity == 100
        assert delivery.total_weight == 15.5
        assert delivery.city == "São Paulo"
        assert delivery.priority == 0
    
    def test_delivery_priority_validation(self):
        """Testa que prioridades são válidas (0, 1 ou 2)."""
        from loader_resources.delivery_loader import Delivery
        
        # Prioridades válidas
        d0 = Delivery(1, "Med1", 10, 5.0, "City1", "Loc1", 0)
        d1 = Delivery(2, "Med2", 10, 5.0, "City2", "Loc2", 1)
        d2 = Delivery(3, "Med3", 10, 5.0, "City3", "Loc3", 2)
        
        assert d0.priority in [0, 1, 2]
        assert d1.priority in [0, 1, 2]
        assert d2.priority in [0, 1, 2]
    
    def test_delivery_weight_positive(self, sample_deliveries):
        """Testa que peso é positivo."""
        for delivery in sample_deliveries:
            assert delivery.total_weight > 0


class TestVehicleLoader:
    """Testes para o carregador de veículos."""
    
    def test_vehicle_creation(self, sample_vehicles):
        """Testa criação de objetos Vehicle."""
        vehicle = sample_vehicles[0]
        
        assert vehicle.vehicle_id == "V1"
        assert vehicle.name == "Van Pequena"
        assert vehicle.max_weight == 1500
        assert vehicle.max_distance == 300
        assert vehicle.cost_per_km == 2.5
    
    def test_vehicle_capacity_positive(self, sample_vehicles):
        """Testa que capacidades são positivas."""
        for vehicle in sample_vehicles:
            assert vehicle.max_weight > 0
            assert vehicle.max_distance > 0
            assert vehicle.cost_per_km > 0
    
    def test_vehicle_ordering_by_capacity(self, sample_vehicles):
        """Testa ordenação de veículos por capacidade."""
        sorted_vehicles = sorted(sample_vehicles, key=lambda v: v.max_weight)
        
        assert sorted_vehicles[0].max_weight <= sorted_vehicles[1].max_weight
        assert sorted_vehicles[1].max_weight <= sorted_vehicles[2].max_weight


class TestDataIntegrity:
    """Testes de integridade dos dados."""
    
    def test_all_deliveries_have_cities(self, sample_deliveries):
        """Testa que todas as entregas têm cidades."""
        for delivery in sample_deliveries:
            assert delivery.city is not None
            assert len(delivery.city) > 0
    
    def test_deliveries_by_city_mapping(self, sample_deliveries_by_city, sample_cities):
        """Testa mapeamento de entregas por cidade."""
        for city in sample_deliveries_by_city:
            assert city in sample_cities
            assert len(sample_deliveries_by_city[city]) > 0
    
    def test_distance_lookup_symmetry(self, sample_distance_lookup):
        """Testa que distâncias são simétricas."""
        for (city1, city2), distance in sample_distance_lookup.items():
            reverse_distance = sample_distance_lookup.get((city2, city1))
            if reverse_distance is not None:
                assert distance == reverse_distance
