# -*- coding: utf-8 -*-

import sys
import itertools
import pygame
from pygame.locals import *
import json
from datetime import datetime

from config import *
from loader_resources.data_loader import load_all_data
from route_helpers import calculate_route_weight, calculate_route_distance, select_vehicle
from ui_resources.ui_renderer import (
    render_evolution_plots,
    render_vrp_evolution_plots,
    render_route_list,
    render_vrp_routes_list,
    render_vehicle_info,
    render_vrp_summary,
    render_footer,
    render_map_with_routes,
    render_map_with_vrp_routes
)

try:
    from ui_resources.ui_renderer import render_vrp_initial_search
except ImportError:
    render_vrp_initial_search = None
from vrp_menu_gui import show_mode_selection, show_vrp_depot_selection
from ui_resources.ga_menu_gui import show_ga_menu
from genetic_algorithm import (
    generate_random_population,
    calculate_fitness,
    sort_population
)
from vrp_solver import solve_vrp
from vrp_details_renderer import render_vrp_details_panel


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
        # Para modo TSP
        best_route = solution
        coord_to_city = data['coord_to_city']
        deliveries_by_city = data['deliveries_by_city']
        distance_lookup = data['distance_lookup']
        vehicles = data['vehicles']
        
        total_weight = calculate_route_weight(best_route, coord_to_city, deliveries_by_city)
        total_distance = calculate_route_distance(best_route, coord_to_city, distance_lookup)
        vehicle = select_vehicle(total_weight, total_distance, vehicles)
        
        # Detalhes da rota
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
    
    else:  # Modo VRP
        vrp_routes = solution
        coord_to_city = data['coord_to_city']
        deliveries_by_city = data['deliveries_by_city']
        
        # Processar todas as rotas VRP
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
        
        # Análise agregada
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
    
    # Salvar em arquivo
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


def run_tsp_mode(data, ga_config):
    deliveries = data['deliveries']
    deliveries_by_city = data['deliveries_by_city']
    cities = data['cities']
    distance_lookup = data['distance_lookup']
    vehicles = data['vehicles']
    city_latlng = data['city_latlng']
    city_to_coord = data['city_to_coord']
    coords = data['coords']
    coord_to_city = data['coord_to_city']
    map_surface = data['map_surface']
    
    population = generate_random_population(coords, POPULATION_SIZE)
    best_history = []
    distance_history = []
    best_solution = None
    best_solution_fitness = float('inf')
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSP para Cidades de São Paulo - Algoritmo Genético (Pressione E para Exportar)")
    clock = pygame.time.Clock()
    
    show_plot = DEFAULT_SHOW_PLOT
    show_list = DEFAULT_SHOW_LIST
    show_attempts = DEFAULT_SHOW_ATTEMPTS
    show_coordinates = DEFAULT_SHOW_COORDINATES
    
    gen = itertools.count(1)
    running = True
    paused = False
    
    while running:
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_q:
                    running = False
                elif e.key == K_g:
                    show_plot = not show_plot
                elif e.key == K_l:
                    show_list = not show_list
                elif e.key == K_t:
                    show_attempts = not show_attempts
                elif e.key == K_c:
                    show_coordinates = not show_coordinates
                elif e.key == K_p:
                    paused = not paused
                elif e.key == K_r:
                    population = generate_random_population(coords, POPULATION_SIZE)
                    best_history = []
                    distance_history = []
                    best_solution = None
                    best_solution_fitness = float('inf')
                    gen = itertools.count(1)
                    print("↻ População reiniciada")
                elif e.key == K_e:
                    if best_solution:
                        filename = f"tsp_solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        export_solution_to_json(data, best_solution, "TSP", export_path=filename)
                    else:
                        print("⚠️  Nenhuma solução disponível para exportar")
        
        if paused:
            screen.fill(WHITE)
            font = pygame.font.SysFont("Arial", 14)
            pause_text = font.render("PAUSADO - Pressione P para continuar", True, RED)
            screen.blit(pause_text, (WIDTH//2 - 150, HEIGHT//2))
            pygame.display.flip()
            clock.tick(5)
            continue
        
        generation = next(gen)
        
        screen.fill(WHITE)
        pygame.draw.rect(screen, GRAY, (0, 0, INFO_WIDTH, HEIGHT))
        pygame.draw.line(screen, BLACK, (INFO_WIDTH, 0), (INFO_WIDTH, HEIGHT), 2)
        
        fitness = [
            calculate_fitness(
                ind,
                coord_to_city,
                deliveries_by_city,
                vehicles,
                distance_lookup,
                priority_weight=PRIORITY_WEIGHT
            )
            for ind in population
        ]
        
        population, fitness = sort_population(population, fitness)
        best = population[0]
        best_fitness = fitness[0]
        best_history.append(best_fitness)
        
        total_weight = calculate_route_weight(best, coord_to_city, deliveries_by_city)
        total_distance_km = calculate_route_distance(best, coord_to_city, distance_lookup)
        vehicle = select_vehicle(total_weight, total_distance_km, vehicles)
        distance_history.append(total_distance_km)
        
        # Atualizar melhor solução
        if best_fitness < best_solution_fitness:
            best_solution = best[:]
            best_solution_fitness = best_fitness
        
        render_evolution_plots(screen, best_history, distance_history, show_plot)
        
        render_route_list(
            screen, 
            best, 
            coord_to_city, 
            deliveries_by_city, 
            distance_lookup, 
            show_list
        )
        
        render_vehicle_info(screen, total_weight, total_distance_km, vehicle, vehicles)
        
        render_footer(screen, generation, best_fitness, POPULATION_SIZE, fitness, len(best), "TSP")
        
        render_map_with_routes(
            screen,
            map_surface,
            best,
            population,
            coords,
            cities,
            coord_to_city,
            city_latlng,
            deliveries_by_city,
            show_attempts,
            show_coordinates
        )
        
        new_pop = [population[0]]
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = ga_config["selection_fn"](population, fitness)
            child = ga_config["crossover_fn"](p1, p2)
            child = ga_config["mutation_fn"](child, MUTATION_RATE)
            new_pop.append(child)
        
        population = new_pop
        
        pygame.display.flip()
        
        if generation % 50 == 0:
            print(f"Geração {generation}: Fitness={best_fitness:.2f}, Distância={total_distance_km:.1f}km, Veículo={vehicle.name if vehicle else 'Nenhum'}")
        
        clock.tick(30)
    
    # Exportar automaticamente ao finalizar
    if best_solution:
        filename = f"tsp_final_solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_solution_to_json(data, best_solution, "TSP", export_path=filename)
    
    pygame.quit()


def run_vrp_mode(data, ga_config, depot_city):
    deliveries_by_city = data['deliveries_by_city']
    cities = data['cities']
    distance_lookup = data['distance_lookup']
    vehicles = data['vehicles']
    city_latlng = data['city_latlng']
    city_to_coord = data['city_to_coord']
    coords = data['coords']
    coord_to_city = data['coord_to_city']
    map_surface = data['map_surface']
    
    depot_coord = None
    if depot_city:
        depot_coord = city_to_coord.get(depot_city)
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("VRP - Calculando solução inicial... (Pressione E para Exportar)")
    
    font = pygame.font.SysFont("Arial", 16, bold=True)
    small_font = pygame.font.SysFont("Arial", 14)
    
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, (0, 0, INFO_WIDTH, HEIGHT))
    
    title = font.render("🚚 Calculando Solução VRP...", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
    
    msg1 = small_font.render("Analisando cidades e veículos", True, DARK_GRAY)
    screen.blit(msg1, (WIDTH//2 - msg1.get_width()//2, HEIGHT//2))
    
    msg2 = small_font.render("Isso pode levar alguns segundos...", True, DARK_GRAY)
    screen.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2 + 25))
    
    pygame.display.flip()
    
    print("\n🚚 Resolvendo VRP...")
    vrp_routes, initial_history = solve_vrp(
        coords,
        coord_to_city,
        deliveries_by_city,
        distance_lookup,
        vehicles,
        ga_config,
        depot_city,
        VRP_GENERATIONS_PER_ROUTE
    )
    
    pygame.display.set_caption("VRP - São Paulo (Pressione D para Detalhes, E para Exportar)")
    clock = pygame.time.Clock()
    
    show_list = DEFAULT_SHOW_LIST
    show_coordinates = DEFAULT_SHOW_COORDINATES
    show_plot = DEFAULT_SHOW_PLOT
    show_route_cities = False
    show_initial_search = False
    show_details = False
    
    cost_history = initial_history['cost_history'][:]
    distance_history = initial_history['distance_history'][:]
    attempts_history = initial_history['attempts'][:]
    
    iteration = 0
    
    running = True
    paused = False
    
    while running:
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_q:
                    running = False
                elif e.key == K_l:
                    show_list = not show_list
                elif e.key == K_c:
                    show_coordinates = not show_coordinates
                elif e.key == K_g:
                    show_plot = not show_plot
                elif e.key == K_p:
                    paused = not paused
                elif e.key == K_d:
                    show_details = not show_details
                    current_width = WIDTH_WITH_DETAILS if show_details else WIDTH
                    screen = pygame.display.set_mode((current_width, HEIGHT))
                    print(f"{'✅' if show_details else '❌'} Painel de detalhes: {'ATIVADO' if show_details else 'DESATIVADO'}")
                elif e.key == K_v:
                    show_route_cities = not show_route_cities
                    print(f"{'✅' if show_route_cities else '❌'} Visualização de cidades: {'ATIVADA' if show_route_cities else 'DESATIVADA'}")
                elif e.key == K_i:
                    show_initial_search = not show_initial_search
                    print(f"{'✅' if show_initial_search else '❌'} Visualização busca inicial: {'ATIVADA' if show_initial_search else 'DESATIVADA'}")
                elif e.key == K_r:
                    print("\n🔄 Recalculando solução VRP do zero...")
                    screen.fill(WHITE)
                    pygame.draw.rect(screen, GRAY, (0, 0, INFO_WIDTH, HEIGHT))
                    title = font.render("🚚 Recalculando Solução...", True, BLACK)
                    current_width = WIDTH_WITH_DETAILS if show_details else WIDTH
                    screen.blit(title, (current_width//2 - title.get_width()//2, HEIGHT//2))
                    pygame.display.flip()
                    
                    vrp_routes, initial_history = solve_vrp(
                        coords,
                        coord_to_city,
                        deliveries_by_city,
                        distance_lookup,
                        vehicles,
                        ga_config,
                        depot_city,
                        VRP_GENERATIONS_PER_ROUTE
                    )
                    cost_history = initial_history['cost_history'][:]
                    distance_history = initial_history['distance_history'][:]
                    attempts_history = initial_history['attempts'][:]
                    iteration = 0
                elif e.key == K_e:
                    if vrp_routes:
                        filename = f"vrp_solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        export_solution_to_json(data, vrp_routes, "VRP", depot_city, export_path=filename)
                    else:
                        print("⚠️  Nenhuma solução disponível para exportar")
        
        if paused:
            screen.fill(WHITE)
            pause_font = pygame.font.SysFont("Arial", 14)
            pause_text = pause_font.render("PAUSADO - Pressione P para continuar", True, RED)
            current_width = WIDTH_WITH_DETAILS if show_details else WIDTH
            screen.blit(pause_text, (current_width//2 - 150, HEIGHT//2))
            pygame.display.flip()
            clock.tick(5)
            continue
        
        iteration += 1
        
        if iteration % 30 == 0:
            print(f"\n🔄 Re-otimizando rotas (iteração {iteration // 30})...")
            
            new_routes, new_history = solve_vrp(
                coords,
                coord_to_city,
                deliveries_by_city,
                distance_lookup,
                vehicles,
                ga_config,
                depot_city,
                VRP_GENERATIONS_PER_ROUTE // 3
            )
            
            new_cost = sum(r.total_cost for r in new_routes)
            new_distance = sum(r.total_distance for r in new_routes)
            best_cost = sum(r.total_cost for r in vrp_routes)
            
            if new_cost < best_cost:
                vrp_routes = new_routes
                print(f"  ⭐ Nova melhor solução! Custo: R$ {new_cost:.2f}")
            
            cost_history.append(min(new_cost, best_cost))
            distance_history.append(new_distance if new_cost < best_cost else sum(r.total_distance for r in vrp_routes))
        
        screen.fill(WHITE)
        pygame.draw.rect(screen, GRAY, (0, 0, INFO_WIDTH, HEIGHT))
        pygame.draw.line(screen, BLACK, (INFO_WIDTH, 0), (INFO_WIDTH, HEIGHT), 2)
        
        if show_initial_search and attempts_history and render_vrp_initial_search:
            render_vrp_initial_search(screen, attempts_history, show_plot)
            list_y = LIST_Y + 150
        elif show_plot and len(cost_history) > 1:
            render_vrp_evolution_plots(screen, cost_history, distance_history, show_plot)
            list_y = LIST_Y
        elif show_plot and len(cost_history) == 1:
            plot_surface = screen.subsurface(
                pygame.Rect(20, PLOT_Y, INFO_WIDTH - 40, PLOT_H)
            )
            plot_surface.fill(GRAY)
            
            wait_font = pygame.font.SysFont("Arial", 14)
            msg = wait_font.render("Aguardando dados de evolução...", True, DARK_GRAY)
            plot_surface.blit(msg, (PLOT_H//2 - msg.get_width()//2, PLOT_H//2))
            list_y = LIST_Y
        else:
            list_y = PLOT_Y
        
        render_vrp_summary(screen, vrp_routes, depot_city)
        
        total_cost = sum(r.total_cost for r in vrp_routes)
        render_footer(screen, iteration, total_cost, len(vrp_routes), cost_history, len(coords), "VRP", show_initial_search)
        
        render_map_with_vrp_routes(
            screen,
            map_surface,
            vrp_routes,
            coords,
            cities,
            coord_to_city,
            city_latlng,
            deliveries_by_city,
            show_coordinates,
            depot_coord
        )
        
        if show_details:
            render_vrp_details_panel(
                screen,
                vrp_routes,
                coord_to_city,
                deliveries_by_city,
                depot_city,
                iteration
            )
        
        pygame.display.flip()
        clock.tick(30)
    
    # Exportar automaticamente ao finalizar
    if vrp_routes:
        filename = f"vrp_final_solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_solution_to_json(data, vrp_routes, "VRP", depot_city, export_path=filename)
    
    pygame.quit()


def main():
    data = load_all_data()
    
    pygame.init()
    
    mode = show_mode_selection()
    
    print(f"\n🎯 Modo selecionado: {mode.upper()}")
    print("📝 Dicas de controle:")
    print("   • Pressione E para exportar a solução atual")
    print("   • A solução será exportada automaticamente ao sair")
    
    ga_config = show_ga_menu()
    
    if mode == "vrp":
        depot_city = show_vrp_depot_selection(data['cities'])
        run_vrp_mode(data, ga_config, depot_city)
    else:
        run_tsp_mode(data, ga_config)
    
    print("✅ Programa finalizado")
    sys.exit()


if __name__ == "__main__":
    main()