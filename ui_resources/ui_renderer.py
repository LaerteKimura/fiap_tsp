# ui_renderer.py

import pygame
from typing import List, Tuple, Dict, Optional
from config import *
from draw_functions import draw_plot, draw_paths
from route_helpers import get_city_priority_info, calculate_route_distance


def render_vrp_evolution_plots(screen: pygame.Surface, 
                              cost_history: List[float],
                              distance_history: List[float],
                              show_plot: bool):
    """
    Renderiza os gráficos de evolução do VRP.
    """
    if not show_plot:
        return
    
    plot_surface = screen.subsurface(
        pygame.Rect(20, PLOT_Y, INFO_WIDTH - 40, PLOT_H)
    )
    plot_surface.fill(GRAY)
    
    font = pygame.font.SysFont("Arial", 14)
    title = font.render("Evolução da Solução VRP", True, BLACK)
    plot_surface.blit(title, (10, 5))

    if len(cost_history) > 1:
        cost_plot = plot_surface.subsurface(
            pygame.Rect(0, 25, INFO_WIDTH - 40, PLOT_H//2 - 30)
        )
        draw_plot(
            cost_plot,
            list(range(len(cost_history))),
            cost_history,
            "Custo Total (R$)",
            (0, 0),
            size_px=(INFO_WIDTH - 40, PLOT_H//2 - 30)
        )
    
    if len(distance_history) > 1:
        distance_plot = plot_surface.subsurface(
            pygame.Rect(0, PLOT_H//2 + 5, INFO_WIDTH - 40, PLOT_H//2 - 30)
        )
        draw_plot(
            distance_plot,
            list(range(len(distance_history))),
            distance_history,
            "Distância Total (km)",
            (0, 0),
            size_px=(INFO_WIDTH - 40, PLOT_H//2 - 30)
        )


def render_evolution_plots(screen: pygame.Surface, 
                           best_history: List[float],
                           distance_history: List[float],
                           show_plot: bool):
    """
    Renderiza os gráficos de evolução do GA.
    """
    if not show_plot:
        return
    
    plot_surface = screen.subsurface(
        pygame.Rect(20, PLOT_Y, INFO_WIDTH - 40, PLOT_H)
    )
    plot_surface.fill(GRAY)
    
    font = pygame.font.SysFont("Arial", 14)
    title = font.render("Evolução do Algoritmo Genético", True, BLACK)
    plot_surface.blit(title, (10, 5))

    if len(best_history) > 1:
        fitness_plot = plot_surface.subsurface(
            pygame.Rect(0, 25, INFO_WIDTH - 40, PLOT_H//2 - 30)
        )
        draw_plot(
            fitness_plot,
            list(range(len(best_history))),
            best_history,
            "Fitness (menor é melhor)",
            (0, 0),
            size_px=(INFO_WIDTH - 40, PLOT_H//2 - 30)
        )
    
    if len(distance_history) > 1:
        distance_plot = plot_surface.subsurface(
            pygame.Rect(0, PLOT_H//2 + 5, INFO_WIDTH - 40, PLOT_H//2 - 30)
        )
        draw_plot(
            distance_plot,
            list(range(len(distance_history))),
            distance_history,
            "Distância (km)",
            (0, 0),
            size_px=(INFO_WIDTH - 40, PLOT_H//2 - 30)
        )


def render_route_list(screen: pygame.Surface,
                     best_route: List[Tuple[int, int]],
                     coord_to_city: Dict[Tuple[int, int], str],
                     deliveries_by_city: Dict,
                     distance_lookup: Dict[Tuple[str, str], float],
                     show_list: bool):
    """
    Renderiza a lista de cidades da melhor rota.
    """
    if not show_list:
        return
    
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)
    
    list_rect = pygame.Rect(20, LIST_Y, INFO_WIDTH - 40, LIST_H)
    pygame.draw.rect(screen, GRAY, list_rect)
    pygame.draw.rect(screen, BLACK, list_rect, 1)

    title = font.render("Melhor Rota Atual:", True, BLACK)
    screen.blit(title, (25, LIST_Y + 5))

    clip = screen.subsurface(list_rect)
    clip.fill(GRAY)
    y = 25

    max_cities = min(len(best_route), 15)
    
    for i in range(max_cities):
        coord = best_route[i]
        city = coord_to_city[coord]
        
        priority_text, priority_num, priority_color = get_city_priority_info(
            city, deliveries_by_city
        )
        
        if len(city) > 12:
            city_display = city[:12] + "..."
        else:
            city_display = city
            
        line_text = f"{i+1:2d}. {city_display} [{priority_text.split()[0]}]"
        
        txt = font.render(line_text, True, BLACK)
        clip.blit(txt, (5, y))
        
        pygame.draw.circle(clip, priority_color, (150, y + 7), 4)
        
        if i > 0:
            sub_route = best_route[:i+1]
            dist = calculate_route_distance(sub_route, coord_to_city, distance_lookup)
            dist_text = f"{dist:.0f}km"
            dist_txt = small_font.render(dist_text, True, (100, 100, 100))
            clip.blit(dist_txt, (INFO_WIDTH - 70, y))
        
        y += 18
    
    if len(best_route) > max_cities:
        remaining = len(best_route) - max_cities
        indicator = small_font.render(f"... +{remaining} cidades", True, (100, 100, 100))
        clip.blit(indicator, (5, LIST_H - 20))


def render_vrp_routes_list(screen: pygame.Surface,
                           vrp_routes: List,
                           coord_to_city: Dict,
                           deliveries_by_city: Dict,
                           show_list: bool,
                           y_offset: int = LIST_Y,
                           show_cities: bool = False):
    """
    Renderiza resumo das rotas VRP.
    """
    if not show_list:
        return
    
    font = pygame.font.SysFont("Arial", 13)
    small_font = pygame.font.SysFont("Arial", 11)
    tiny_font = pygame.font.SysFont("Arial", 10)
    city_font = pygame.font.SysFont("Arial", 9)
    
    list_height = min(LIST_H + 100, HEIGHT - y_offset - VEHICLE_H - FOOTER_H - 10)
    list_rect = pygame.Rect(20, y_offset, INFO_WIDTH - 40, list_height)
    pygame.draw.rect(screen, GRAY, list_rect)
    pygame.draw.rect(screen, BLACK, list_rect, 1)

    title_text = f"VRP - {len(vrp_routes)} Rotas (Ordem de Execução)"
    if show_cities:
        title_text += " - Detalhado"
    title = font.render(title_text, True, BLACK)
    screen.blit(title, (25, y_offset + 5))

    clip = screen.subsurface(list_rect)
    clip.fill(GRAY)
    y = 25
    
    vehicle_usage = {}
    for route in vrp_routes:
        vid = route.vehicle.vehicle_id
        vehicle_usage[vid] = vehicle_usage.get(vid, 0) + 1
    
    priority_colors = {0: RED, 1: ORANGE, 2: GREEN}
    priority_labels = {0: "P0", 1: "P1", 2: "P2"}
    
    max_routes_to_show = 6 if not show_cities else 3
    
    for i, route in enumerate(vrp_routes):
        if y > list_height - 60:
            break
            
        route_color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
        
        max_priority = getattr(route, 'max_priority', 2)
        avg_priority = getattr(route, 'avg_priority', 2.0)
        
        priority_color = priority_colors.get(max_priority, GRAY)
        
        pygame.draw.rect(clip, route_color, (5, y, 15, 15))
        pygame.draw.rect(clip, BLACK, (5, y, 15, 15), 1)
        
        pygame.draw.circle(clip, priority_color, (28, y + 7), 6)
        pygame.draw.circle(clip, BLACK, (28, y + 7), 6, 1)
        
        priority_text = priority_labels.get(max_priority, "?")
        priority_txt = tiny_font.render(priority_text, True, WHITE)
        clip.blit(priority_txt, (24, y + 2))
        
        vehicle_name = route.vehicle.name
        vehicle_id = route.vehicle.vehicle_id
        
        if vehicle_usage.get(vehicle_id, 0) > 1:
            route_text = f"#{i+1}: {vehicle_name} ⚠️"
            txt = font.render(route_text, True, RED)
        else:
            route_text = f"#{i+1}: {vehicle_name}"
            txt = font.render(route_text, True, BLACK)
        
        clip.blit(txt, (40, y))
        y += 17
        
        if vehicle_usage.get(vehicle_id, 0) > 1:
            warning = tiny_font.render(f"(Veículo reutilizado - ID:{vehicle_id})", True, (150, 0, 0))
            clip.blit(warning, (5, y))
            y += 12
        
        details = [
            f"  {len(route.route)} cidades | {route.total_distance:.0f}km | {route.total_weight:.0f}kg",
            f"  Custo: R$ {route.total_cost:.2f} | Prioridade: {avg_priority:.1f}"
        ]
        
        weight_limit = route.vehicle.max_weight
        distance_limit = route.vehicle.max_distance * 0.85
        
        weight_ok = route.total_weight <= weight_limit
        distance_ok = route.total_distance <= distance_limit
        
        if not weight_ok or not distance_ok:
            warning_parts = []
            if not weight_ok:
                warning_parts.append(f"PESO:{route.total_weight:.0f}>{weight_limit:.0f}kg")
            if not distance_ok:
                warning_parts.append(f"DIST:{route.total_distance:.0f}>{distance_limit:.0f}km")
            
            warning_text = "  ⚠️ EXCEDE LIMITES: " + " | ".join(warning_parts)
            details.append(warning_text)
        
        for idx, detail in enumerate(details):
            if "⚠️ EXCEDE" in detail:
                detail_txt = small_font.render(detail, True, (180, 0, 0))
            else:
                detail_txt = small_font.render(detail, True, (80, 80, 80))
            clip.blit(detail_txt, (5, y))
            y += 14
        
        if show_cities and route.route:
            y += 3
            cities_header = tiny_font.render("  Cidades:", True, (60, 60, 60))
            clip.blit(cities_header, (5, y))
            y += 12
            
            for idx, coord in enumerate(route.route[:8]):
                city_name = coord_to_city.get(coord, "?")
                
                if len(city_name) > 16:
                    city_name = city_name[:16] + "..."
                
                priority_text_city, priority_num, priority_color_city = get_city_priority_info(
                    coord_to_city.get(coord, "?"), deliveries_by_city
                )
                
                pygame.draw.circle(clip, priority_color_city, (10, y + 4), 2)
                
                city_text = f"  {idx+1}. {city_name}"
                city_txt = city_font.render(city_text, True, (50, 50, 50))
                clip.blit(city_txt, (15, y))
                y += 10
                
                if y > list_height - 20:
                    break
            
            if len(route.route) > 8:
                more = city_font.render(f"  ... +{len(route.route)-8} cidades", True, (100, 100, 100))
                clip.blit(more, (15, y))
                y += 10
        
        y += 8
        
        if i >= max_routes_to_show - 1:
            break
    
    if len(vrp_routes) > max_routes_to_show:
        remaining = len(vrp_routes) - max_routes_to_show
        indicator = small_font.render(f"... +{remaining} rotas (pressione V para detalhes)", True, (100, 100, 100))
        clip.blit(indicator, (5, list_height - 20))


def render_vehicle_info(screen: pygame.Surface,
                       total_weight: float,
                       total_distance_km: float,
                       vehicle: Optional,
                       vehicles: List):
    """
    Renderiza informações do veículo selecionado.
    """
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)
    
    info_rect = pygame.Rect(20, VEHICLE_Y, INFO_WIDTH - 40, VEHICLE_H)
    pygame.draw.rect(screen, GRAY, info_rect)
    pygame.draw.rect(screen, BLACK, info_rect, 1)

    y = VEHICLE_Y + 10
    
    weight_text = font.render(f"Peso total: {total_weight:.1f} kg", True, BLACK)
    screen.blit(weight_text, (30, y))
    y += 20
    
    dist_text = font.render(f"Distância total: {total_distance_km:.1f} km", True, BLACK)
    screen.blit(dist_text, (30, y))
    y += 20
    
    if vehicle:
        vehicle_text = font.render(f"Veículo: {vehicle.name}", True, GREEN)
        screen.blit(vehicle_text, (30, y))
        y += 20
        details = small_font.render(
            f"Capacidade: {vehicle.max_weight} kg | Autonomia: {vehicle.max_distance} km",
            True, (80, 80, 80)
        )
        screen.blit(details, (30, y))
    else:
        vehicle_text = font.render("Nenhum veículo adequado!", True, RED)
        screen.blit(vehicle_text, (30, y))
        y += 20
        details = small_font.render(
            f"Necessário: ≤{min(v.max_weight for v in vehicles)}kg e ≤{min(v.max_distance for v in vehicles)}km",
            True, (150, 0, 0)
        )
        screen.blit(details, (30, y))


def render_vrp_summary(screen: pygame.Surface,
                      vrp_routes: List,
                      depot_city: Optional[str] = None):
    """
    Renderiza resumo geral da solução VRP.
    """
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)
    tiny_font = pygame.font.SysFont("Arial", 10)
    
    info_rect = pygame.Rect(20, VEHICLE_Y, INFO_WIDTH - 40, VEHICLE_H)
    pygame.draw.rect(screen, GRAY, info_rect)
    pygame.draw.rect(screen, BLACK, info_rect, 1)

    y = VEHICLE_Y + 10
    
    total_distance = sum(r.total_distance for r in vrp_routes)
    total_weight = sum(r.total_weight for r in vrp_routes)
    total_cost = sum(r.total_cost for r in vrp_routes)
    
    dist_text = font.render(f"Distância total: {total_distance:.1f} km", True, BLACK)
    screen.blit(dist_text, (30, y))
    y += 20
    
    weight_text = font.render(f"Peso total: {total_weight:.1f} kg", True, BLACK)
    screen.blit(weight_text, (30, y))
    y += 20
    
    cost_text = font.render(f"Custo total: R$ {total_cost:.2f}", True, GREEN)
    screen.blit(cost_text, (30, y))
    y += 20
    
    violations = 0
    for route in vrp_routes:
        weight_limit = route.vehicle.max_weight
        distance_limit = route.vehicle.max_distance * 0.85
        
        if route.total_weight > weight_limit or route.total_distance > distance_limit:
            violations += 1
    
    if violations > 0:
        warning = small_font.render(
            f"⚠️ {violations} rota(s) excedem limites do veículo",
            True, (180, 0, 0)
        )
        screen.blit(warning, (30, y))
    else:
        vehicles_text = small_font.render(
            f"✅ Todas as rotas dentro dos limites",
            True, (0, 120, 0)
        )
        screen.blit(vehicles_text, (30, y))
    
    y += 15
    
    vehicles_count = small_font.render(
        f"Veículos utilizados: {len(vrp_routes)}",
        True, (80, 80, 80)
    )
    screen.blit(vehicles_count, (30, y))
    
    if depot_city:
        y += 15
        depot_text = small_font.render(
            f"Depósito: {depot_city}",
            True, (80, 80, 80)
        )
        screen.blit(depot_text, (30, y))





def render_map_legend(screen: pygame.Surface, mode: str = "TSP", num_routes: int = 0, vrp_routes: List = None):
    """
    Renderiza a legenda do mapa.
    """
    small_font = pygame.font.SysFont("Arial", 12)
    tiny_font = pygame.font.SysFont("Arial", 10)
    
    legend_y = 10
    
    if mode == "TSP":
        legend_items = [
            ("Mapa de São Paulo", BLACK),
            ("Cidades P0 (Alta)", RED),
            ("Cidades P1 (Média)", ORANGE),
            ("Cidades P2 (Baixa)", GREEN),
            ("Melhor rota", BLUE),
            ("Tentativas", LIGHT_GRAY)
        ]
    else:
        legend_items = [
            ("Mapa de São Paulo", BLACK),
            ("Cidades P0 (Alta)", RED),
            ("Cidades P1 (Média)", ORANGE),
            ("Cidades P2 (Baixa)", GREEN)
        ]
        
        priority_labels = {0: "🔴", 1: "🟠", 2: "🟢"}
        
        if vrp_routes:
            for i in range(min(num_routes, len(ROUTE_COLORS))):
                if i < len(vrp_routes):
                    route = vrp_routes[i]
                    max_priority = getattr(route, 'max_priority', 2)
                    priority_icon = priority_labels.get(max_priority, "⚪")
                    legend_items.append((f"Rota {i+1} {priority_icon}", ROUTE_COLORS[i]))
                else:
                    legend_items.append((f"Rota {i+1}", ROUTE_COLORS[i]))
        else:
            for i in range(min(num_routes, len(ROUTE_COLORS))):
                legend_items.append((f"Rota {i+1}", ROUTE_COLORS[i]))
    
    for text, color in legend_items:
        if "Cidades" in text:
            pygame.draw.circle(screen, color, (INFO_WIDTH + 10, legend_y + 6), 4)
        else:
            pygame.draw.rect(screen, color, (INFO_WIDTH + 10, legend_y, 8, 8))
        
        pygame.draw.rect(screen, BLACK, (INFO_WIDTH + 10, legend_y, 8, 8), 1)
        leg_text = small_font.render(text, True, BLACK)
        screen.blit(leg_text, (INFO_WIDTH + 27, legend_y - 2))
        legend_y += 18


def render_map_with_routes(screen: pygame.Surface,
                          map_surface: pygame.Surface,
                          best_route: List[Tuple[int, int]],
                          population: List[List[Tuple[int, int]]],
                          coords: List[Tuple[int, int]],
                          cities: List[str],
                          coord_to_city: Dict[Tuple[int, int], str],
                          city_latlng: Dict[str, Tuple[float, float]],
                          deliveries_by_city: Dict,
                          show_attempts: bool,
                          show_coordinates: bool):
    """
    Renderiza o mapa com rotas, cidades e informações (TSP).
    """
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)
    
    map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT)
    screen.set_clip(map_rect)
    
    screen.blit(map_surface, (INFO_WIDTH, 0))
    
    render_map_legend(screen, "TSP")
    
    if show_attempts and len(population) > 3:
        for attempt in population[1:4]:
            draw_paths(screen, attempt, LIGHT_GRAY, 1)
    
    draw_paths(screen, best_route, BLUE, 3)
    
    for i, (coord, city) in enumerate(zip(coords, cities)):
        _, _, priority_color = get_city_priority_info(city, deliveries_by_city)
        
        pygame.draw.circle(screen, priority_color, coord, 8)
        pygame.draw.circle(screen, WHITE, coord, 6)
        
        if show_coordinates:
            lat, lng = city_latlng[city]
            coord_text = small_font.render(f"{city}: ({lat:.2f}, {lng:.2f})", True, PURPLE)
            screen.blit(coord_text, (coord[0] + 10, coord[1] - 20))
        else:
            name_text = small_font.render(city, True, BLACK)
            text_rect = name_text.get_rect()
            text_rect.center = (coord[0], coord[1] - 15)
            
            bg_rect = text_rect.inflate(6, 4)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 200))
            screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(screen, BLACK, bg_rect, 1)
            
            screen.blit(name_text, text_rect)
        
        if coord in best_route:
            idx = best_route.index(coord)
            num_text = font.render(str(idx + 1), True, BLUE)
            num_rect = num_text.get_rect(center=coord)
            screen.blit(num_text, num_rect)

    screen.set_clip(None)


def render_map_with_vrp_routes(screen: pygame.Surface,
                               map_surface: pygame.Surface,
                               vrp_routes: List,
                               coords: List[Tuple[int, int]],
                               cities: List[str],
                               coord_to_city: Dict[Tuple[int, int], str],
                               city_latlng: Dict[str, Tuple[float, float]],
                               deliveries_by_city: Dict,
                               show_coordinates: bool,
                               depot_coord: Optional[Tuple[int, int]] = None):
    """
    Renderiza o mapa com múltiplas rotas VRP.
    """
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)
    
    map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT)
    screen.set_clip(map_rect)
    
    screen.blit(map_surface, (INFO_WIDTH, 0))
    
    render_map_legend(screen, "VRP", len(vrp_routes), vrp_routes)
    
    for i, route_obj in enumerate(vrp_routes):
        route_color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
        route = route_obj.route
        
        if depot_coord and route:
            depot_route = [depot_coord] + route + [depot_coord]
            draw_paths(screen, depot_route, route_color, 3)
        else:
            draw_paths(screen, route, route_color, 3)
    
    if depot_coord:
        pygame.draw.circle(screen, BLACK, depot_coord, 12)
        pygame.draw.circle(screen, (255, 215, 0), depot_coord, 10)
        
        depot_text = font.render("D", True, BLACK)
        depot_rect = depot_text.get_rect(center=depot_coord)
        screen.blit(depot_text, depot_rect)
        
        depot_city = coord_to_city.get(depot_coord, "Depósito")
        label = small_font.render(depot_city, True, BLACK)
        label_rect = label.get_rect()
        label_rect.center = (depot_coord[0], depot_coord[1] - 20)
        
        bg_rect = label_rect.inflate(6, 4)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 220))
        screen.blit(bg_surface, bg_rect)
        pygame.draw.rect(screen, BLACK, bg_rect, 1)
        screen.blit(label, label_rect)
    
    for i, (coord, city) in enumerate(zip(coords, cities)):
        _, _, priority_color = get_city_priority_info(city, deliveries_by_city)
        
        pygame.draw.circle(screen, priority_color, coord, 8)
        pygame.draw.circle(screen, WHITE, coord, 6)
        
        if show_coordinates:
            lat, lng = city_latlng[city]
            coord_text = small_font.render(f"{city}: ({lat:.2f}, {lng:.2f})", True, PURPLE)
            screen.blit(coord_text, (coord[0] + 10, coord[1] - 20))
        else:
            name_text = small_font.render(city, True, BLACK)
            text_rect = name_text.get_rect()
            text_rect.center = (coord[0], coord[1] - 15)
            
            bg_rect = text_rect.inflate(6, 4)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 200))
            screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(screen, BLACK, bg_rect, 1)
            
            screen.blit(name_text, text_rect)
        
        for route_idx, route_obj in enumerate(vrp_routes):
            if coord in route_obj.route:
                route_pos = route_obj.route.index(coord) + 1
                route_color = ROUTE_COLORS[route_idx % len(ROUTE_COLORS)]
                
                num_text = font.render(str(route_pos), True, route_color)
                num_rect = num_text.get_rect(center=coord)
                screen.blit(num_text, num_rect)
                break

    screen.set_clip(None)




def render_vrp_initial_search(screen: pygame.Surface,
                              attempts_history: List[Dict]):
    """
    Renderiza os gráficos da busca inicial do VRP.
    Mostra TODAS as tentativas com diferentes números de veículos.
    """
    plot_surface = screen.subsurface(
        pygame.Rect(20, PLOT_Y, INFO_WIDTH - 40, PLOT_H + 50)
    )
    plot_surface.fill(GRAY)
    
    font = pygame.font.SysFont("Arial", 14, bold=True)
    small_font = pygame.font.SysFont("Arial", 11)
    tiny_font = pygame.font.SysFont("Arial", 10)
    
    title = font.render("📊 BUSCA INICIAL - Tentativas", True, BLACK)
    plot_surface.blit(title, (10, 5))
    
    subtitle = tiny_font.render(f"Testadas {len(attempts_history)} configurações de veículos", True, DARK_GRAY)
    plot_surface.blit(subtitle, (10, 22))
    
    n_vehicles = [a['n_vehicles'] for a in attempts_history]
    costs = [a['cost'] for a in attempts_history]
    distances = [a['distance'] for a in attempts_history]
    feasible = [a['feasible'] for a in attempts_history]
    
    cost_plot = plot_surface.subsurface(
        pygame.Rect(0, 40, INFO_WIDTH - 40, PLOT_H//2 - 15)
    )
    draw_plot(
        cost_plot,
        n_vehicles,
        costs,
        "Custo Total (R$)",
        (0, 0),
        size_px=(INFO_WIDTH - 40, PLOT_H//2 - 15)
    )
    
    distance_plot = plot_surface.subsurface(
        pygame.Rect(0, PLOT_H//2 + 30, INFO_WIDTH - 40, PLOT_H//2 - 15)
    )
    draw_plot(
        distance_plot,
        n_vehicles,
        distances,
        "Distância (km)",
        (0, 0),
        size_px=(INFO_WIDTH - 40, PLOT_H//2 - 15)
    )
    
    legend_y = PLOT_H + 15
    
    feasible_count = sum(1 for f in feasible if f)
    infeasible_count = len(feasible) - feasible_count
    
    pygame.draw.circle(plot_surface, GREEN, (15, legend_y + 5), 4)
    pygame.draw.circle(plot_surface, RED, (100, legend_y + 5), 4)
    
    viable_text = small_font.render(f"Viáveis: {feasible_count}", True, BLACK)
    plot_surface.blit(viable_text, (25, legend_y))
    
    inviable_text = small_font.render(f"Inviáveis: {infeasible_count}", True, BLACK)
    plot_surface.blit(inviable_text, (110, legend_y))
    
    if feasible:
        best_feasible_idx = None
        best_cost = float('inf')
        for i, (f, c) in enumerate(zip(feasible, costs)):
            if f and c < best_cost:
                best_cost = c
                best_feasible_idx = i
        
        if best_feasible_idx is not None:
            best_vehicles = n_vehicles[best_feasible_idx]
            best_dist = distances[best_feasible_idx]
            
            pygame.draw.circle(plot_surface, ORANGE, (15, legend_y + 22), 4)
            
            best_text = f"⭐ Melhor: {best_vehicles} veículos - R$ {best_cost:.2f} - {best_dist:.0f}km"
            best_label = small_font.render(best_text, True, (0, 120, 0))
            plot_surface.blit(best_label, (25, legend_y + 17))
    
    hint = tiny_font.render("Pressione G para alternar entre gráficos", True, (120, 120, 120))
    plot_surface.blit(hint, (10, PLOT_H + 37))


def render_footer(
    screen: pygame.Surface,
    generation: int,
    best_fitness: float,
    population_size: int,
    fitness_list: list,
    num_cities: int,
    mode: str = "TSP",
    show_initial_search: bool = False
):
    small_font = pygame.font.SysFont("Arial", 12)

    footer_bg = pygame.Rect(0, HEIGHT - FOOTER_H, INFO_WIDTH, FOOTER_H)
    pygame.draw.rect(screen, (220, 220, 220), footer_bg)
    pygame.draw.rect(screen, BLACK, footer_bg, 1)

    if mode == "TSP":
        footer_lines = [
            f"Geração: {generation}",
            f"Melhor fitness: {best_fitness:.2f}",
            f"Rotas viáveis: {sum(1 for f in fitness_list if f < 10000)}/{population_size}",
            f"Cidades na rota: {num_cities}",
            "Controles:",
            "E=Gerar arquivo com solução",
            "G=gráficos  L=lista  T=tentativas",
            "C=coords  P=pausa  R=reset  Q=sair"
        ]
    else:
        improvement = ""
        if len(fitness_list) > 1 and fitness_list[0] > 0:
            pct = ((fitness_list[0] - fitness_list[-1]) / fitness_list[0]) * 100
            improvement = f" (↓ {pct:.1f}%)"

        graph_mode = "BUSCA INICIAL" if show_initial_search else "RE-OTIMIZAÇÕES"

        footer_lines = [
            f"Modo: VRP | Iteração: {generation}",
            f"Custo atual: R$ {best_fitness:.2f}{improvement}",
            f"Gráfico: {graph_mode} | Cidades: {num_cities}",
            "Controles:",
            "E=Gerar arquivo com solução",
            "G=gráficos  L=lista  V=cidades  D=detalhes",
            "C=coords  P=pausa  R=recalcular  Q=sair"
        ]

    y = HEIGHT - FOOTER_H + 8
    for line in footer_lines:
        text = small_font.render(line, True, BLACK)
        screen.blit(text, (10, y))
        y += 14
