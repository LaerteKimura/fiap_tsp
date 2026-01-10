import sys
import pygame
from pygame.locals import *
import json
from datetime import datetime
import route_analyzer

from config import *
from loader_resources.data_loader import load_all_data
from route_helpers import calculate_route_weight, calculate_route_distance, select_vehicle

from views.menu_inicial import show_analyze_menu
from views.mode_selection import show_mode_selection
from views.ga_menu import show_ga_menu
from views.tsp_view import run_tsp_mode
from views.vrp_view import run_vrp_mode
from views.vrp_depot_selection import show_vrp_depot_selection

try:
    from ui_resources.ui_renderer import render_vrp_initial_search
except ImportError:
    render_vrp_initial_search = None

from vrp_solver import solve_vrp
from ui_resources.vrp_details_renderer import render_vrp_details_panel

import os
os.environ["SDL_VIDEO_CENTERED"] = "1"

def export_solution_to_json(data, solution, mode, depot_city=None, export_path="best_solution.json"):
    """
    Exporta a solução para um arquivo JSON estruturado para fácil interpretação por LLM.
    
    Estrutura:
    - metadata: informações gerais
    - constraints: restrições do problema
    - solution: detalhes da solução
    - analysis: análise e métricas
    - llm_instructions: instruções para o LLM
    """
    
    if mode == "TSP":
        best_route = solution
        coord_to_city = data['coord_to_city']
        deliveries_by_city = data['deliveries_by_city']
        distance_lookup = data['distance_lookup']
        vehicles = data['vehicles']
        
        total_weight = calculate_route_weight(best_route, coord_to_city, deliveries_by_city)
        total_distance = calculate_route_distance(best_route, coord_to_city, distance_lookup)
        vehicle = select_vehicle(total_weight, total_distance, vehicles)
        
        route_details = []
        for i, coord in enumerate(best_route):
            city = coord_to_city.get(coord)
            deliveries = deliveries_by_city.get(city, [])
            
            city_info = {
                "sequence": i + 1,
                "city": city,
                "coordinates": coord,
                "deliveries": [
                    {
                        "id": d.id,
                        "medicine": d.medicine_name,
                        "quantity": d.quantity,
                        "weight": d.total_weight,
                        "priority": d.priority,
                        "priority_label": "ALTA" if d.priority == 0 else "MÉDIA" if d.priority == 1 else "BAIXA"
                    }
                    for d in deliveries
                ]
            }
            route_details.append(city_info)
        
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "mode": "TSP",
                "description": "Melhor rota encontrada para o Problema do Caixeiro Viajante",
                "algorithm": "Genetic Algorithm",
                "total_cities": len(best_route)
            },
            "constraints": {
                "vehicles_available": [
                    {
                        "id": v.vehicle_id,
                        "name": v.name,
                        "max_weight": v.max_weight,
                        "max_distance": v.max_distance,
                        "cost_per_km": v.cost_per_km
                    }
                    for v in vehicles
                ]
            },
            "solution": {
                "selected_vehicle": {
                    "id": vehicle.vehicle_id if vehicle else None,
                    "name": vehicle.name if vehicle else None,
                    "type": vehicle.type if vehicle else None
                },
                "total_distance_km": round(total_distance, 2),
                "total_weight_kg": round(total_weight, 2),
                "total_cost": round(total_distance * vehicle.cost_per_km, 2) if vehicle else 0,
                "route": route_details
            },
            "analysis": {
                "feasibility": {
                    "weight_constraint": vehicle and total_weight <= vehicle.max_weight,
                    "distance_constraint": vehicle and total_distance <= vehicle.max_distance,
                    "is_feasible": vehicle and total_weight <= vehicle.max_weight and total_distance <= vehicle.max_distance
                },
                "priority_summary": {
                    "high_priority": sum(1 for city in route_details for d in city["deliveries"] if d["priority"] == 0),
                    "medium_priority": sum(1 for city in route_details for d in city["deliveries"] if d["priority"] == 1),
                    "low_priority": sum(1 for city in route_details for d in city["deliveries"] if d["priority"] == 2)
                },
                "performance_metrics": {
                    "weight_utilization": round((total_weight / vehicle.max_weight * 100), 2) if vehicle and vehicle.max_weight > 0 else 0,
                    "distance_utilization": round((total_distance / vehicle.max_distance * 100), 2) if vehicle and vehicle.max_distance > 0 else 0
                }
            },
            "llm_instructions": {
                "task": "Analise a rota de entrega e gere um relatório executivo em português",
                "sections_to_include": [
                    "Resumo Executivo",
                    "Análise de Viabilidade",
                    "Distribuição de Prioridades",
                    "Eficiência da Rota",
                    "Recomendações"
                ],
                "key_points_to_highlight": [
                    "Verificar se todas as restrições são atendidas",
                    "Analisar distribuição de prioridades ao longo da rota",
                    "Sugerir melhorias na ordem das cidades",
                    "Calcular custo-benefício",
                    "Identificar possíveis otimizações"
                ],
                "output_format": "Relatório em markdown com seções claras"
            }
        }
    
    else:
        vrp_routes = solution
        coord_to_city = data['coord_to_city']
        deliveries_by_city = data['deliveries_by_city']
        
        routes_details = []
        for i, route in enumerate(vrp_routes):
            route_cities = []
            for j, coord in enumerate(route.route):
                city = coord_to_city.get(coord)
                deliveries = deliveries_by_city.get(city, [])
                
                city_info = {
                    "sequence": j + 1,
                    "city": city,
                    "coordinates": coord,
                    "deliveries": [
                        {
                            "id": d.id,
                            "medicine": d.medicine_name,
                            "quantity": d.quantity,
                            "weight": d.total_weight,
                            "priority": d.priority,
                            "priority_label": "ALTA" if d.priority == 0 else "MÉDIA" if d.priority == 1 else "BAIXA"
                        }
                        for d in deliveries
                    ]
                }
                route_cities.append(city_info)
            
            route_info = {
                "route_id": i + 1,
                "vehicle": {
                    "id": route.vehicle.vehicle_id,
                    "name": route.vehicle.name,
                    "type": route.vehicle.type,
                    "max_weight": route.vehicle.max_weight,
                    "max_distance": route.vehicle.max_distance,
                    "cost_per_km": route.vehicle.cost_per_km
                },
                "stats": {
                    "total_distance_km": round(route.total_distance, 2),
                    "total_weight_kg": round(route.total_weight, 2),
                    "total_cost": round(route.total_cost, 2),
                    "max_priority": route.max_priority,
                    "average_priority": round(route.avg_priority, 2)
                },
                "cities": route_cities,
                "feasibility": {
                    "weight_constraint": route.total_weight <= route.vehicle.max_weight,
                    "distance_constraint": route.total_distance <= route.vehicle.max_distance,
                    "is_feasible": route.is_feasible
                }
            }
            routes_details.append(route_info)
        
        all_deliveries = []
        for route in routes_details:
            for city in route["cities"]:
                all_deliveries.extend(city["deliveries"])
        
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "mode": "VRP",
                "description": "Melhor solução encontrada para o Problema de Roteamento de Veículos",
                "algorithm": "Genetic Algorithm with VRP enhancements",
                "depot": depot_city,
                "total_routes": len(vrp_routes),
                "total_cities": sum(len(route.route) for route in vrp_routes)
            },
            "constraints": {
                "depot_city": depot_city,
                "vehicle_unique_constraint": True
            },
            "solution": {
                "routes": routes_details,
                "aggregate_stats": {
                    "total_cost": round(sum(r.total_cost for r in vrp_routes), 2),
                    "total_distance_km": round(sum(r.total_distance for r in vrp_routes), 2),
                    "total_weight_kg": round(sum(r.total_weight for r in vrp_routes), 2),
                    "average_vehicles_used": len(vrp_routes),
                    "cost_per_vehicle": round(sum(r.total_cost for r in vrp_routes) / len(vrp_routes), 2) if vrp_routes else 0
                }
            },
            "analysis": {
                "feasibility_summary": {
                    "feasible_routes": sum(1 for r in routes_details if r["feasibility"]["is_feasible"]),
                    "infeasible_routes": sum(1 for r in routes_details if not r["feasibility"]["is_feasible"]),
                    "all_feasible": all(r["feasibility"]["is_feasible"] for r in routes_details)
                },
                "priority_distribution": {
                    "high_priority": sum(1 for d in all_deliveries if d["priority"] == 0),
                    "medium_priority": sum(1 for d in all_deliveries if d["priority"] == 1),
                    "low_priority": sum(1 for d in all_deliveries if d["priority"] == 2)
                },
                "vehicle_utilization": [
                    {
                        "route_id": route["route_id"],
                        "vehicle": route["vehicle"]["name"],
                        "weight_utilization_percent": round((route["stats"]["total_weight_kg"] / route["vehicle"]["max_weight"] * 100), 2),
                        "distance_utilization_percent": round((route["stats"]["total_distance_km"] / route["vehicle"]["max_distance"] * 100), 2),
                        "cost_efficiency": round(route["stats"]["total_cost"] / route["stats"]["total_distance_km"], 2) if route["stats"]["total_distance_km"] > 0 else 0
                    }
                    for route in routes_details
                ],
                "route_efficiency": {
                    "cities_per_route": round(sum(len(route["cities"]) for route in routes_details) / len(routes_details), 2) if routes_details else 0,
                    "cost_per_city": round(sum(r.total_cost for r in vrp_routes) / sum(len(route.route) for route in vrp_routes), 2) if vrp_routes else 0,
                    "distance_per_route": round(sum(r.total_distance for r in vrp_routes) / len(vrp_routes), 2) if vrp_routes else 0
                }
            },
            "llm_instructions": {
                "task": "Analise a solução VRP e gere um relatório executivo detalhado em português",
                "sections_to_include": [
                    "Resumo Executivo",
                    "Análise por Rota",
                    "Viabilidade da Solução",
                    "Otimização de Recursos",
                    "Distribuição de Prioridades",
                    "Eficiência de Custos",
                    "Recomendações Específicas"
                ],
                "key_points_to_highlight": [
                    "Verificar se todas as rotas atendem às restrições",
                    "Analisar balanceamento de carga entre veículos",
                    "Avaliar distribuição de prioridades",
                    "Identificar rotas sobrecarregadas/subutilizadas",
                    "Sugerir redistribuição de cidades entre rotas",
                    "Calcular métricas de eficiência",
                    "Propor melhorias na alocação de veículos"
                ],
                "output_format": "Relatório detalhado em markdown com tabelas e análises por rota",
                "target_audience": "Gerentes de logística e operações"
            }
        }
    
    try:
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Solução exportada para: {export_path}")
        print(f"   Modo: {mode}")
        print(f"   Timestamp: {export_data['metadata']['export_timestamp']}")
        
        if mode == "TSP":
            print(f"   Cidades: {len(best_route)}")
            print(f"   Distância total: {total_distance:.2f} km")
            print(f"   Custo total: R$ {total_distance * vehicle.cost_per_km:.2f}" if vehicle else "   Custo: N/A")
        else:
            print(f"   Rotas: {len(vrp_routes)}")
            print(f"   Custo total: R$ {sum(r.total_cost for r in vrp_routes):.2f}")
            print(f"   Viabilidade: {'TODAS VIÁVEIS' if export_data['analysis']['feasibility_summary']['all_feasible'] else 'COM VIOLAÇÕES'}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro ao exportar solução: {e}")
        return False

def run_analyze_flow():
    """Executa o modo análise e encerra o app."""
    pygame.quit()
    try:
        route_analyzer.main()
    except Exception as e:
        print(f"Erro ao executar análise: {e}")
    sys.exit()

def run_solver_flow(data):
    """
    Fluxo: seleção de modo -> GA -> roda TSP/VRP.
    Retorna ao menu inicial se usuário apertar 'back' no mode selection.
    """
    while True:
        mode = show_mode_selection()

        if mode == "back":
            return  # volta pro menu inicial

        ga_config = show_ga_menu()
        if ga_config == "back":
            continue  # volta pra seleção de modo

        if mode == "vrp":
            depot_city = show_vrp_depot_selection(data["cities"])
            if depot_city == "back":
                continue  # volta pra seleção de modo

            result = run_vrp_mode(data, ga_config, depot_city, export_fn=export_solution_to_json)
            if result == "back":
                continue
            sys.exit()

        if mode == "tsp":
            result = run_tsp_mode(data, ga_config, export_fn=export_solution_to_json)
            if result == "back":
                continue  # ou volta pra tela anterior
            sys.exit()

        # se veio algo inesperado, reinicia a seleção de modo
        continue

def run_main_menu_flow(data):
    """
    Fluxo: menu inicial. Decide se encerra, vai para análise ou vai para solver.
    Retorna quando o usuário quer encerrar.
    """
    while True:
        initial_choice = show_analyze_menu()

        if initial_choice == "skip":
            return

        if initial_choice == "analyze":
            run_analyze_flow()

        run_solver_flow(data)

def main():
    data = load_all_data()
    pygame.init()

    run_main_menu_flow(data)
    sys.exit()

if __name__ == "__main__":
    main()
