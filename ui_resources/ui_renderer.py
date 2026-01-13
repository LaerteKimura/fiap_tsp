import pygame
import math
from typing import List, Tuple, Dict, Optional
from config import *
from ui_resources.draw_functions import draw_plot, draw_paths
from route_helpers import get_city_priority_info, calculate_route_distance

def render_screen_header(
    screen: pygame.Surface,
    rect: pygame.Rect,
    title: str,
    icon_path: Optional[str] = None,
    *,
    bg_color: Tuple[int, int, int] = (245, 247, 250),
    border_color: Tuple[int, int, int] = (200, 205, 210),
    title_color: Tuple[int, int, int] = (20, 30, 30),
) -> int:
    """
    Renderiza um header (faixa) no topo da área informativa.
    Retorna a altura ocupada (em px) para você empurrar os painéis abaixo.    
    """
    pygame.draw.rect(screen, bg_color, rect)
    pygame.draw.line(screen, border_color, (rect.left, rect.bottom - 1), (rect.right, rect.bottom - 1), 1)

    padding_x = 16
    padding_y = 10
    icon_size = 28
    gap = 10

    icon_surf = None
    if icon_path:
        try:
            icon_surf = pygame.image.load(icon_path).convert_alpha()
            icon_surf = pygame.transform.smoothscale(icon_surf, (icon_size, icon_size))
        except Exception:
            icon_surf = None

    font_title = pygame.font.SysFont("Segoe UI", 18, bold=True)

    x = rect.left + padding_x

    if icon_surf:
        icon_y = rect.top + (rect.height - icon_size) // 2
        screen.blit(icon_surf, (x, icon_y))
        x += icon_size + gap

    title_surf = font_title.render(title, True, title_color)
    title_rect = title_surf.get_rect()
    title_rect.midleft = (x, rect.top + rect.height // 2)
    screen.blit(title_surf, title_rect)

    return rect.height

def render_vrp_evolution_plots(
    screen: pygame.Surface,
    cost_history: List[float],
    distance_history: List[float],
    show_plot: bool,
    *,
    y_offset: int = 0,
):
    """
    Renderiza os gráficos de evolução do VRP.
    """
    if not show_plot:
        return

    panel_y = PLOT_Y + y_offset

    plot_surface = screen.subsurface(
        pygame.Rect(20, panel_y, INFO_WIDTH - 40, PLOT_H)
    )
    plot_surface.fill(GRAY)

    font = pygame.font.SysFont("Segoe UI", 15, bold=True)
    title = font.render("Evolução da Solução VRP", True, (20, 30, 30))
    plot_surface.blit(title, (4, 0))

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
            size_px=(INFO_WIDTH - 40, PLOT_H//2 - 30),
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
            size_px=(INFO_WIDTH - 40, PLOT_H//2 - 30),
        )

def render_evolution_plots(
    screen: pygame.Surface,
    best_history,
    distance_history,
    show_plot: bool,
    *,
    y_offset: int = 0,
):
    if not show_plot:
        return

    panel_y = PLOT_Y + y_offset

    plot_surface = screen.subsurface(
        pygame.Rect(20, panel_y, INFO_WIDTH - 40, PLOT_H)
    )
    plot_surface.fill(GRAY)

    font_title = pygame.font.SysFont("Segoe UI", 15, bold=True)

    title_x = 4
    title_y = 0
    title = font_title.render("Evolução do Algoritmo Genético", True, (20, 30, 30))
    plot_surface.blit(title, (title_x, title_y))

    if len(best_history) > 1:
        fitness_plot = plot_surface.subsurface(
            pygame.Rect(0, 25, INFO_WIDTH - 40, PLOT_H // 2 - 30)
        )
        draw_plot(
            fitness_plot,
            list(range(len(best_history))),
            best_history,
            "Evolução do Fitness",
            (0, 0),
            size_px=(INFO_WIDTH - 40, PLOT_H // 2 - 30),
            line_color=(30, 90, 160),
        )

    if len(distance_history) > 1:
        distance_plot = plot_surface.subsurface(
            pygame.Rect(0, PLOT_H // 2 + 5, INFO_WIDTH - 40, PLOT_H // 2 - 30)
        )
        draw_plot(
            distance_plot,
            list(range(len(distance_history))),
            distance_history,
            "Distância Total da Rota (km)",
            (0, 0),
            size_px=(INFO_WIDTH - 40, PLOT_H // 2 - 30),
            line_color=(40, 140, 90),
        )

def render_route_list(screen: pygame.Surface,
                     best_route: List[Tuple[int, int]],
                     coord_to_city: Dict[Tuple[int, int], str],
                     deliveries_by_city: Dict,
                     distance_lookup: Dict[Tuple[str, str], float],
                     show_list: bool):
    if not show_list:
        return

    title_font = pygame.font.SysFont("Segoe UI", 15, bold=True)  # levemente menor
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)

    panel_x = 20
    panel_w = INFO_WIDTH - 40
    panel_y = LIST_Y
    panel_h = LIST_H

    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    pygame.draw.rect(screen, GRAY, panel_rect)

    TITLE_H = 25

    # área branca começa DEPOIS da faixa do título (não cobre o título)
    content_rect = pygame.Rect(
        panel_x,
        panel_y + TITLE_H,
        panel_w,
        panel_h - TITLE_H
    )
    pygame.draw.rect(screen, WHITE, content_rect)  # sem stroke

    title = title_font.render("Melhor Rota Atual", True, (20, 30, 30))
    screen.blit(title, (panel_x + 4, panel_y))

    clip = screen.subsurface(content_rect)

    y = 6
    max_cities = min(len(best_route), 15)

    for i in range(max_cities):
        coord = best_route[i]
        city = coord_to_city.get(coord, "?")

        priority_text, _, priority_color = get_city_priority_info(city, deliveries_by_city)

        city_display = city[:14] + "…" if len(city) > 14 else city
        line_text = f"{i+1:2d}. {city_display} [{priority_text.split()[0]}]"

        txt = font.render(line_text, True, BLACK)
        clip.blit(txt, (10, y))

        pygame.draw.circle(clip, priority_color, (190, y + 8), 4)

        if i > 0:
            sub_route = best_route[:i+1]
            dist = calculate_route_distance(sub_route, coord_to_city, distance_lookup)
            dist_txt = small_font.render(f"{dist:.0f} km", True, (90, 90, 90))
            dist_x = panel_w - dist_txt.get_width() - 12
            clip.blit(dist_txt, (dist_x, y))

        y += 18

    if len(best_route) > max_cities:
        remaining = len(best_route) - max_cities
        more = small_font.render(f"... +{remaining} cidades", True, (120, 120, 120))
        clip.blit(more, (10, content_rect.height - 18))

def render_vehicle_info(
    screen: pygame.Surface,
    total_weight: float,
    total_distance_km: float,
    vehicle: Optional,
    vehicles: List
):
    panel_x = 20
    panel_y = VEHICLE_Y
    panel_w = INFO_WIDTH - 40
    panel_h = VEHICLE_H

    TITLE_H = 20
    CONTENT_TOP_GAP = 6  # <<< espaço entre título e quadro branco

    pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_w, panel_h))

    content_rect = pygame.Rect(
        panel_x,
        panel_y + TITLE_H + CONTENT_TOP_GAP,
        panel_w,
        panel_h - TITLE_H - CONTENT_TOP_GAP
    )
    pygame.draw.rect(screen, WHITE, content_rect)

    title_font = pygame.font.SysFont("Segoe UI", 15, bold=True)
    strong_font = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)

    clip = screen.subsurface(content_rect)

    pad_x = 10
    y = 6

    if vehicle:
        verdict_text = "Viável"
        verdict_color = GREEN
        vehicle_line = f"Veículo: {vehicle.name}"
        details_line = f"Capacidade: {vehicle.max_weight} kg | Autonomia: {vehicle.max_distance} km"
    else:
        verdict_text = "Inviável"
        verdict_color = RED
        vehicle_line = "Nenhum veículo suporta essa demanda"
        if vehicles:
            min_w = min(v.max_weight for v in vehicles)
            min_d = min(v.max_distance for v in vehicles)
            details_line = f"Referência: ≤{min_w}kg | ≤{min_d}km"
        else:
            details_line = "Nenhum veículo cadastrado"

    clip.blit(strong_font.render(verdict_text, True, verdict_color), (pad_x, y))
    y += 20

    clip.blit(font.render(vehicle_line, True, (20, 30, 30)), (pad_x, y))
    y += 18

    clip.blit(small_font.render(details_line, True, (90, 90, 90)), (pad_x, y))
    y += 18

    demand_text = f"Peso: {total_weight:.1f} kg   |   Distância: {total_distance_km:.1f} km"
    clip.blit(font.render(demand_text, True, BLACK), (pad_x, y))

    title = title_font.render("Viabilidade Logística", True, (20, 30, 30))
    screen.blit(title, (panel_x + 4, panel_y + 2))

def _fmt_ptbr(value: float, decimals: int = 2) -> str:
    s = format(value, f",.{decimals}f")  # 1,234.56
    return s.replace(",", "X").replace(".", ",").replace("X", ".")  # 1.234,56


def render_vrp_summary(
    screen: pygame.Surface,
    vrp_routes: List,
    depot_city: Optional[str] = None,
    *,
    panel_y: int = None,
):
    """
    Card: Status da Solução VRP (novo padrão).
    Agora permite posicionamento dinâmico via panel_y.
    """
    panel_x = 20
    panel_w = INFO_WIDTH - 40
    panel_h = VEHICLE_H

    if panel_y is None:
        panel_y = VEHICLE_Y

    TITLE_H = 20
    CONTENT_TOP_GAP = 6

    pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_w, panel_h))

    content_rect = pygame.Rect(
        panel_x,
        panel_y + TITLE_H + CONTENT_TOP_GAP,
        panel_w,
        panel_h - TITLE_H - CONTENT_TOP_GAP
    )
    pygame.draw.rect(screen, WHITE, content_rect)

    title_font = pygame.font.SysFont("Segoe UI", 15, bold=True)
    strong_font = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font = pygame.font.SysFont("Arial", 14)
    small_font = pygame.font.SysFont("Arial", 12)

    clip = screen.subsurface(content_rect)

    total_distance = sum(r.total_distance for r in vrp_routes) if vrp_routes else 0.0
    total_weight = sum(r.total_weight for r in vrp_routes) if vrp_routes else 0.0
    total_cost = sum(r.total_cost for r in vrp_routes) if vrp_routes else 0.0
    vehicles_used = len(vrp_routes) if vrp_routes else 0

    violations = 0
    for route in vrp_routes or []:
        weight_limit = route.vehicle.max_weight
        distance_limit = route.vehicle.max_distance * 0.85
        if route.total_weight > weight_limit or route.total_distance > distance_limit:
            violations += 1

    if not vrp_routes:
        status_text = "Sem solução"
        status_color = RED
        status_detail = "Nenhuma rota gerada ainda"
    elif violations == 0:
        status_text = "Solução viável"
        status_color = GREEN
        status_detail = "Todas as rotas dentro dos limites"
    else:
        status_text = "Atenção"
        status_color = (200, 120, 0)
        status_detail = f"{violations} rota(s) fora do limite"

    pad_x = 10
    y = 6

    clip.blit(strong_font.render(status_text, True, status_color), (pad_x, y))
    y += 20

    clip.blit(small_font.render(status_detail, True, (90, 90, 90)), (pad_x, y))
    y += 18

    line3 = f"Veículos usados: {vehicles_used}   |   Rotas fora do limite: {violations}"
    clip.blit(font.render(line3, True, (20, 30, 30)), (pad_x, y))
    y += 20

    cost_line = f"Custo total: R$ {_fmt_ptbr(total_cost, 2)}"
    clip.blit(font.render(cost_line, True, (30, 90, 160)), (pad_x, y))
    y += 20

    metrics_line = f"Distância total: {_fmt_ptbr(total_distance, 1)} km   |   Peso total: {_fmt_ptbr(total_weight, 1)} kg"
    clip.blit(font.render(metrics_line, True, BLACK), (pad_x, y))
    y += 18

    if depot_city:
        depot_line = f"Depósito: {depot_city}"
        clip.blit(small_font.render(depot_line, True, (90, 90, 90)), (pad_x, y))

    title = title_font.render("Status da Solução VRP", True, (20, 30, 30))
    screen.blit(title, (panel_x + 4, panel_y))

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
    
    # map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT)
    map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT - ACTIONBAR_H)
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
    
    map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT - ACTIONBAR_H)
    screen.set_clip(map_rect)
    
    screen.blit(map_surface, (INFO_WIDTH, 0))
    
    render_map_legend(screen, "VRP", len(vrp_routes), vrp_routes)
    
    for i, route_obj in enumerate(vrp_routes):
        route_color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
        route = route_obj.route
        
        if depot_coord and route:
            depot_route = [depot_coord] + route + [depot_coord]
            draw_paths(screen, depot_route, route_color, 3)
        elif route and len(route) > 1:
            # [CORREÇÃO] Sem depósito: fechar a rota adicionando primeira cidade no final
            closed_route = route + [route[0]]
            draw_paths(screen, closed_route, route_color, 3)
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

def render_vrp_initial_search(
    screen: pygame.Surface,
    attempts_history: List[Dict],
    *,
    y_offset: int = 0,
):
    """
    Renderiza os gráficos da busca inicial do VRP.
    Mostra TODAS as tentativas com diferentes números de veículos.
    """
    panel_y = PLOT_Y + y_offset

    plot_surface = screen.subsurface(
        pygame.Rect(20, panel_y, INFO_WIDTH - 40, PLOT_H + 50)
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

def render_status(
    screen: pygame.Surface,
    generation: int,
    best_fitness: float,
    num_cities: int
):
    """
    Bloco: Status da Execução
    Mostra apenas informações essenciais do estado atual do algoritmo.
    """

    panel_x = 20
    panel_y = STATUS_Y
    panel_w = INFO_WIDTH - 40
    panel_h = STATUS_H

    TITLE_H = 20
    CONTENT_TOP_GAP = 6

    # Fundo do card
    pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_w, panel_h))

    # Área branca
    content_rect = pygame.Rect(
        panel_x,
        panel_y + TITLE_H + CONTENT_TOP_GAP,
        panel_w,
        panel_h - TITLE_H - CONTENT_TOP_GAP
    )
    pygame.draw.rect(screen, WHITE, content_rect)

    # Fontes
    title_font = pygame.font.SysFont("Segoe UI", 15, bold=True)
    label_font = pygame.font.SysFont("Arial", 14)
    value_font = pygame.font.SysFont("Arial", 14, bold=True)

    clip = screen.subsurface(content_rect)

    y = 8
    pad_x = 10

    # Geração
    clip.blit(label_font.render("Geração:", True, (60, 60, 60)), (pad_x, y))
    clip.blit(value_font.render(str(generation), True, BLACK), (140, y))
    y += 20

    # Melhor fitness
    clip.blit(label_font.render("Melhor fitness:", True, (60, 60, 60)), (pad_x, y))
    clip.blit(value_font.render(f"{best_fitness:.2f}", True, BLACK), (140, y))
    y += 20

    # Cidades na rota
    clip.blit(label_font.render("Cidades na rota:", True, (60, 60, 60)), (pad_x, y))
    clip.blit(value_font.render(str(num_cities), True, BLACK), (140, y))

    # Título
    title = title_font.render("Status da Execução", True, (20, 30, 30))
    screen.blit(title, (panel_x + 4, panel_y + 2))

def render_action_bar(
    screen: pygame.Surface,
    *,
    export_enabled: bool,
    show_coordinates: bool,
):  
    # bar_rect = pygame.Rect(0, ACTIONBAR_Y, WIDTH, ACTIONBAR_H)
    screen_w = screen.get_width()
    bar_rect = pygame.Rect(0, ACTIONBAR_Y, screen_w, ACTIONBAR_H)
    pygame.draw.rect(screen, (245, 247, 250), bar_rect)
    pygame.draw.line(screen, (200, 205, 210), (0, ACTIONBAR_Y), (WIDTH, ACTIONBAR_Y), 1)

    font_btn = pygame.font.SysFont("Segoe UI", 16, bold=True)

    btn_h = 46
    back_w = 170
    export_w = 300  # um pouco maior pra não apertar o texto
    coords_w = 220
    gap = 14
    y = ACTIONBAR_Y + (ACTIONBAR_H - btn_h) // 2

    # Voltar à esquerda / Export à direita (padrão bom)
    back_rect = pygame.Rect(20, y, back_w, btn_h)
    export_rect = pygame.Rect(WIDTH - 20 - export_w, y, export_w, btn_h)

    coords_x = back_rect.right + gap
    coords_rect = pygame.Rect(coords_x, y, coords_w, btn_h)

    mx, my = pygame.mouse.get_pos()

    # ─────────────────────────────
    # Voltar
    # ─────────────────────────────
    back_hover = back_rect.collidepoint(mx, my)
    back_bg = (235, 240, 246) if back_hover else (245, 247, 250)

    pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
    pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)

    back_txt = font_btn.render("< Voltar", True, (70, 75, 85))
    screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

    # ─────────────────────────────
    # Export
    # ─────────────────────────────
    export_hover = export_rect.collidepoint(mx, my)

    if not export_enabled:
        exp_bg = (245, 247, 250)
        exp_border = (200, 205, 210)
        exp_text = (150, 150, 150)
        pulse = 0
    else:
        exp_bg = (220, 235, 250) if export_hover else (245, 247, 250)
        exp_border = (30, 90, 160)
        exp_text = (30, 90, 160)
        pulse = 2 + int(2 * (1 + math.sin(pygame.time.get_ticks() / 320))) if export_hover else 0

    pygame.draw.rect(screen, exp_bg, export_rect, border_radius=12)
    pygame.draw.rect(screen, exp_border, export_rect, width=1, border_radius=12)

    exp_txt = font_btn.render("Gerar Arquivo da Solução >", True, exp_text)
    screen.blit(exp_txt, exp_txt.get_rect(center=(export_rect.centerx + pulse, export_rect.centery)))

    # ─────────────────────────────
    # Coords
    # ─────────────────────────────
    coords_hover = coords_rect.collidepoint(mx, my)

    if show_coordinates:
        coords_bg = (220, 235, 250)
        coords_border = (30, 90, 160)
        coords_text = (30, 90, 160)
        label = "Coordenadas: ON"
    else:
        coords_bg = (235, 240, 246) if coords_hover else (245, 247, 250)
        coords_border = (200, 205, 210)
        coords_text = (70, 75, 85)
        label = "Exibir coordenadas"

    pygame.draw.rect(screen, coords_bg, coords_rect, border_radius=12)
    pygame.draw.rect(screen, coords_border, coords_rect, width=1, border_radius=12)

    txt = font_btn.render(label, True, coords_text)
    screen.blit(txt, txt.get_rect(center=coords_rect.center))

    return back_rect, coords_rect, export_rect

def draw_button(
    screen: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    *,
    hovered: bool = False,
    pressed: bool = False,
    disabled: bool = False,
    font: pygame.font.Font = None,
    text_color: Tuple[int, int, int] = (20, 30, 30),
):
    if font is None:
        font = pygame.font.SysFont("Segoe UI", 14, bold=True)

    # Paleta "tela nova"
    bg = (245, 247, 250)
    border = (200, 205, 210)
    shadow = (0, 0, 0, 25)

    if hovered and not disabled:
        bg = (250, 252, 255)

    if pressed and not disabled:
        bg = (238, 242, 246)

    if disabled:
        bg = (240, 240, 240)
        border = (215, 215, 215)
        text_color = (150, 150, 150)

    # Sombra leve (alpha)
    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shadow_surf.fill(shadow)
    screen.blit(shadow_surf, (rect.x, rect.y + 2))

    # Corpo do botão
    pygame.draw.rect(screen, bg, rect, border_radius=10)
    pygame.draw.rect(screen, border, rect, width=1, border_radius=10)

    # Texto centralizado
    txt = font.render(text, True, text_color)
    screen.blit(txt, txt.get_rect(center=rect.center))
