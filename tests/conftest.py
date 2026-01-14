# tests/conftest.py
"""
Fixtures compartilhadas para testes do projeto.
"""
import pytest
import sys
import os
from typing import Dict, List

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_deliveries():
    """Entregas de exemplo para testes."""
    from loader_resources.delivery_loader import Delivery
    
    return [
        Delivery(1, "Paracetamol", 100, 15.5, "São Paulo", "Hospital Central", 0),
        Delivery(2, "Ibuprofeno", 50, 8.2, "Campinas", "Clínica Norte", 1),
        Delivery(3, "Dipirona", 200, 25.0, "Santos", "UBS Centro", 2),
        Delivery(4, "Amoxicilina", 80, 12.5, "São José dos Campos", "Hospital Regional", 0),
        Delivery(5, "Azitromicina", 60, 9.0, "Ribeirão Preto", "Farmácia Popular", 1),
    ]


@pytest.fixture
def sample_vehicles():
    """Veículos de exemplo para testes."""
    from loader_resources.vehicle_loader import Vehicle
    
    return [
        Vehicle("V1", 1500, 300, "van", 1500, 2.5, "Van Pequena"),
        Vehicle("V2", 3000, 600, "caminhao", 3000, 3.0, "Caminhão Médio"),
        Vehicle("V3", 5000, 800, "caminhao", 5000, 3.5, "Caminhão Grande"),
    ]


@pytest.fixture
def sample_cities():
    """Cidades de exemplo para testes."""
    return ["São Paulo", "Campinas", "Santos", "São José dos Campos", "Ribeirão Preto"]


@pytest.fixture
def sample_coords():
    """Coordenadas de exemplo para testes."""
    return [
        (100, 100),  # São Paulo
        (150, 120),  # Campinas
        (110, 180),  # Santos
        (180, 110),  # São José dos Campos
        (250, 150),  # Ribeirão Preto
    ]


@pytest.fixture
def sample_coord_to_city(sample_coords, sample_cities):
    """Mapeamento coordenadas -> cidades."""
    return dict(zip(sample_coords, sample_cities))


@pytest.fixture
def sample_city_to_coord(sample_coords, sample_cities):
    """Mapeamento cidades -> coordenadas."""
    return dict(zip(sample_cities, sample_coords))


@pytest.fixture
def sample_deliveries_by_city(sample_deliveries):
    """Mapeamento cidade -> entregas."""
    deliveries_by_city = {}
    for delivery in sample_deliveries:
        city = delivery.city
        if city not in deliveries_by_city:
            deliveries_by_city[city] = []
        deliveries_by_city[city].append(delivery)
    return deliveries_by_city


@pytest.fixture
def sample_distance_lookup(sample_cities):
    """Distâncias entre cidades (exemplo simplificado)."""
    distances = {
        ("São Paulo", "Campinas"): 92.5,
        ("Campinas", "São Paulo"): 92.5,
        ("São Paulo", "Santos"): 72.3,
        ("Santos", "São Paulo"): 72.3,
        ("São Paulo", "São José dos Campos"): 85.0,
        ("São José dos Campos", "São Paulo"): 85.0,
        ("São Paulo", "Ribeirão Preto"): 313.0,
        ("Ribeirão Preto", "São Paulo"): 313.0,
        ("Campinas", "Santos"): 150.0,
        ("Santos", "Campinas"): 150.0,
        ("Campinas", "São José dos Campos"): 120.0,
        ("São José dos Campos", "Campinas"): 120.0,
        ("Campinas", "Ribeirão Preto"): 230.0,
        ("Ribeirão Preto", "Campinas"): 230.0,
        ("Santos", "São José dos Campos"): 180.0,
        ("São José dos Campos", "Santos"): 180.0,
        ("Santos", "Ribeirão Preto"): 450.0,
        ("Ribeirão Preto", "Santos"): 450.0,
        ("São José dos Campos", "Ribeirão Preto"): 320.0,
        ("Ribeirão Preto", "São José dos Campos"): 320.0,
    }
    return distances


@pytest.fixture
def sample_route(sample_coords):
    """Rota de exemplo (lista de coordenadas)."""
    return list(sample_coords)


@pytest.fixture
def vrp_route_mock(sample_vehicles, sample_coords):
    """Mock de VRPRoute para testes."""
    from vrp_solver import VRPRoute
    
    route = VRPRoute(
        vehicle=sample_vehicles[0],
        route=list(sample_coords[:3]),
        depot_coord=sample_coords[0]
    )
    return route
