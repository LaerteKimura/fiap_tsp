# tests/test_export.py
"""
Testes para exportação de soluções para JSON.
"""
import pytest
import json
import os
import tempfile
from infra.solution_exporter import export_solution_to_json


class TestTSPExport:
    """Testes para exportação de soluções TSP."""
    
    def test_export_tsp_creates_file(self, sample_route, sample_coord_to_city,
                                     sample_deliveries_by_city, sample_distance_lookup, sample_vehicles):
        """Testa que exportação TSP cria arquivo."""
        data = {
            "coord_to_city": sample_coord_to_city,
            "deliveries_by_city": sample_deliveries_by_city,
            "distance_lookup": sample_distance_lookup,
            "vehicles": sample_vehicles,
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            result = export_solution_to_json(data, sample_route, "TSP", export_path=temp_path)
            assert result is True
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_tsp_valid_json(self, sample_route, sample_coord_to_city,
                                   sample_deliveries_by_city, sample_distance_lookup, sample_vehicles):
        """Testa que JSON exportado é válido."""
        data = {
            "coord_to_city": sample_coord_to_city,
            "deliveries_by_city": sample_deliveries_by_city,
            "distance_lookup": sample_distance_lookup,
            "vehicles": sample_vehicles,
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            export_solution_to_json(data, sample_route, "TSP", export_path=temp_path)
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            assert "metadata" in json_data
            assert "solution" in json_data
            assert "constraints" in json_data
            assert json_data["metadata"]["mode"] == "TSP"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_tsp_includes_metrics(self, sample_route, sample_coord_to_city,
                                        sample_deliveries_by_city, sample_distance_lookup, sample_vehicles):
        """Testa que exportação inclui métricas importantes."""
        data = {
            "coord_to_city": sample_coord_to_city,
            "deliveries_by_city": sample_deliveries_by_city,
            "distance_lookup": sample_distance_lookup,
            "vehicles": sample_vehicles,
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            export_solution_to_json(data, sample_route, "TSP", export_path=temp_path)
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            solution = json_data["solution"]
            assert "total_distance_km" in solution
            assert "total_weight" in solution
            assert "route_details" in solution
            
            # Métricas devem ser numéricas
            assert isinstance(solution["total_distance_km"], (int, float))
            assert isinstance(solution["total_weight"], (int, float))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestVRPExport:
    """Testes para exportação de soluções VRP."""
    
    def test_export_vrp_creates_file(self, vrp_route_mock, sample_coord_to_city,
                                     sample_deliveries_by_city, sample_distance_lookup, sample_vehicles):
        """Testa que exportação VRP cria arquivo."""
        data = {
            "coord_to_city": sample_coord_to_city,
            "deliveries_by_city": sample_deliveries_by_city,
            "distance_lookup": sample_distance_lookup,
            "vehicles": sample_vehicles,
        }
        
        # Calcular stats da rota
        vrp_route_mock.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        
        vrp_solution = [vrp_route_mock]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            result = export_solution_to_json(data, vrp_solution, "VRP", depot_city="São Paulo", export_path=temp_path)
            assert result is True
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_vrp_includes_routes(self, vrp_route_mock, sample_coord_to_city,
                                       sample_deliveries_by_city, sample_distance_lookup, sample_vehicles):
        """Testa que exportação VRP inclui detalhes das rotas."""
        data = {
            "coord_to_city": sample_coord_to_city,
            "deliveries_by_city": sample_deliveries_by_city,
            "distance_lookup": sample_distance_lookup,
            "vehicles": sample_vehicles,
        }
        
        vrp_route_mock.calculate_stats(sample_coord_to_city, sample_deliveries_by_city, sample_distance_lookup)
        vrp_solution = [vrp_route_mock]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            export_solution_to_json(data, vrp_solution, "VRP", depot_city="São Paulo", export_path=temp_path)
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            assert "solution" in json_data
            solution = json_data["solution"]
            assert "routes" in solution
            assert len(solution["routes"]) > 0
            
            # Cada rota deve ter métricas
            for route in solution["routes"]:
                assert "metrics" in route
                assert "vehicle" in route
                assert "route_details" in route
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestExportEdgeCases:
    """Testes para casos extremos na exportação."""
    
    def test_export_empty_route(self, sample_coord_to_city, sample_deliveries_by_city,
                               sample_distance_lookup, sample_vehicles):
        """Testa exportação de rota vazia."""
        data = {
            "coord_to_city": sample_coord_to_city,
            "deliveries_by_city": sample_deliveries_by_city,
            "distance_lookup": sample_distance_lookup,
            "vehicles": sample_vehicles,
        }
        
        empty_route = []
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            result = export_solution_to_json(data, empty_route, "TSP", export_path=temp_path)
            
            # Deve lidar com rota vazia sem erro
            assert result is True or result is False  # Pode aceitar ou rejeitar
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
