# vrp_details_renderer.py

import pygame
from typing import List, Dict
from config import *
from route_helpers import get_city_priority_info


def render_vrp_details_panel(screen: pygame.Surface,
                             vrp_routes: List,
                             coord_to_city: Dict,
                             deliveries_by_city: Dict,
                             depot_city: str = None,
                             iteration: int = 0,
                             x_offset: int = 1480):
    """
    Renderiza o painel de detalhes VRP no lado direito da tela.
    """
    font_title = pygame.font.SysFont("Arial", 13, bold=True)
    font_normal = pygame.font.SysFont("Arial", 10)
    font_small = pygame.font.SysFont("Arial", 9)
    font_tiny = pygame.font.SysFont("Arial", 8)
    
    panel_rect = pygame.Rect(x_offset, 0, DETAILS_WIDTH, HEIGHT)
    pygame.draw.rect(screen, WHITE, panel_rect)
    pygame.draw.line(screen, BLACK, (x_offset, 0), (x_offset, HEIGHT), 3)
    
    y = 10
    
    title = font_title.render(f"Detalhes VRP (Iter. {iteration})", True, BLACK)
    screen.blit(title, (x_offset + 10, y))
    y += 25
    
    total_distance = sum(r.total_distance for r in vrp_routes)
    total_weight = sum(r.total_weight for r in vrp_routes)
    total_cost = sum(r.total_cost for r in vrp_routes)
    
    summary_text = [
        f"Rotas: {len(vrp_routes)}",
        f"Dist.: {total_distance:.1f} km",
        f"Peso: {total_weight:.1f} kg",
        f"Custo: R$ {total_cost:.2f}"
    ]
    
    if depot_city:
        summary_text.append(f"Depósito: {depot_city}")
    
    summary_rect = pygame.Rect(x_offset + 10, y, DETAILS_WIDTH - 20, 80)
    pygame.draw.rect(screen, GRAY, summary_rect)
    pygame.draw.rect(screen, BLACK, summary_rect, 2)
    
    y += 8
    for text in summary_text:
        txt = font_normal.render(text, True, BLACK)
        screen.blit(txt, (x_offset + 20, y))
        y += 15
    
    y += 12
    
    violations = 0
    for route in vrp_routes:
        weight_limit = route.vehicle.max_weight
        distance_limit = route.vehicle.max_distance * 0.85
        
        if route.total_weight > weight_limit or route.total_distance > distance_limit:
            violations += 1
    
    if violations > 0:
        warning = font_normal.render(
            f"⚠️ {violations} rota(s) excedem limites",
            True, RED
        )
        screen.blit(warning, (x_offset + 20, y))
    else:
        ok_text = font_normal.render(
            "✅ Todas rotas OK",
            True, GREEN
        )
        screen.blit(ok_text, (x_offset + 20, y))
    
    y += 25
    
    separator = font_title.render("Detalhes por Rota", True, BLACK)
    screen.blit(separator, (x_offset + 10, y))
    y += 20
    
    priority_colors = {0: RED, 1: ORANGE, 2: GREEN}
    priority_labels = {0: "P0", 1: "P1", 2: "P2"}
    
    vehicle_usage = {}
    for route in vrp_routes:
        vid = route.vehicle.vehicle_id
        vehicle_usage[vid] = vehicle_usage.get(vid, 0) + 1
    
    for i, route in enumerate(vrp_routes):
        if y > HEIGHT - 50:
            overflow = font_small.render(
                f"... +{len(vrp_routes) - i} rotas",
                True, DARK_GRAY
            )
            screen.blit(overflow, (x_offset + 20, y))
            break
        
        route_color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
        max_priority = getattr(route, 'max_priority', 2)
        avg_priority = getattr(route, 'avg_priority', 2.0)
        priority_color = priority_colors.get(max_priority, GRAY)
        
        box_height = 75 + len(route.route) * 10
        
        if y + box_height > HEIGHT - 20:
            overflow = font_small.render(
                f"... +{len(vrp_routes) - i} rotas (role)",
                True, DARK_GRAY
            )
            screen.blit(overflow, (x_offset + 20, y))
            break
        
        box_rect = pygame.Rect(x_offset + 10, y, DETAILS_WIDTH - 20, box_height)
        #pygame.draw.rect(screen, GRAY, box_rect)
       # pygame.draw.rect(screen, route_color, box_rect, 3)
        
        y += 6
        
        pygame.draw.rect(screen, route_color, (x_offset + 20, y, 15, 15))
        pygame.draw.rect(screen, BLACK, (x_offset + 20, y, 15, 15), 1)
        
        pygame.draw.circle(screen, priority_color, (x_offset + 43, y + 7), 6)
        pygame.draw.circle(screen, BLACK, (x_offset + 43, y + 7), 6, 1)
        
        priority_text = priority_labels.get(max_priority, "?")
        priority_txt = font_tiny.render(priority_text, True, WHITE)
        screen.blit(priority_txt, (x_offset + 39, y + 2))
        
        route_title = f"#{i+1}: {route.vehicle.name}"
        if vehicle_usage.get(route.vehicle.vehicle_id, 0) > 1:
            route_title += " ⚠️"
            title_color = RED
        else:
            title_color = BLACK
        
        txt = font_title.render(route_title, True, title_color)
        screen.blit(txt, (x_offset + 55, y))
        y += 15
        
        details = [
            f"ID:{route.vehicle.vehicle_id} | Cidades:{len(route.route)}",
            f"Dist:{route.total_distance:.0f}km (Max:{route.vehicle.max_distance})",
            f"Peso:{route.total_weight:.0f}kg (Max:{route.vehicle.max_weight})",
            f"Custo:R${route.total_cost:.2f} | Prior:{avg_priority:.1f}"
        ]
        
        weight_limit = route.vehicle.max_weight
        distance_limit = route.vehicle.max_distance * 0.85
        
        weight_ok = route.total_weight <= weight_limit
        distance_ok = route.total_distance <= distance_limit
        
        if not weight_ok or not distance_ok:
            warning_parts = []
            if not weight_ok:
                warning_parts.append(f"PESO!")
            if not distance_ok:
                warning_parts.append(f"DIST!")
            details.append("⚠️ " + " ".join(warning_parts))
        
        for detail in details:
            if "⚠️" in detail:
                txt = font_small.render(detail, True, RED)
            else:
                txt = font_small.render(detail, True, (60, 60, 60))
            screen.blit(txt, (x_offset + 25, y))
            y += 11
        
        y += 3
        cities_header = font_normal.render("Entrega:", True, BLACK)
        screen.blit(cities_header, (x_offset + 25, y))
        y += 14
        
        if depot_city:
            depot_txt = font_small.render(f"0.{depot_city[:12]} (DEP)", True, (0, 100, 200))
            screen.blit(depot_txt, (x_offset + 35, y))
            y += 10
        
        for idx, coord in enumerate(route.route):
            city_name = coord_to_city.get(coord, "?")
            if len(city_name) > 15:
                city_name = city_name[:15] + "."
            
            priority_text_city, priority_num, priority_color_city = get_city_priority_info(
                coord_to_city.get(coord, "?"), deliveries_by_city
            )
            
            pygame.draw.circle(screen, priority_color_city, (x_offset + 40, y + 5), 3)
            
            deliveries_info = ""
            full_city_name = coord_to_city.get(coord, "?")
            if full_city_name in deliveries_by_city:
                n_deliveries = len(deliveries_by_city[full_city_name])
                total_weight_city = sum(d.total_weight for d in deliveries_by_city[full_city_name])
                deliveries_info = f" {n_deliveries}x,{total_weight_city:.0f}kg"
            
            city_text = f"{idx+1}.{city_name} [{priority_text_city.split()[0]}]{deliveries_info}"
            city_txt = font_small.render(city_text, True, (40, 40, 40))
            screen.blit(city_txt, (x_offset + 48, y))
            y += 10
        
        if depot_city:
            depot_txt = font_small.render(f"{len(route.route)+1}.{depot_city[:12]} (RET)", True, (0, 100, 200))
            screen.blit(depot_txt, (x_offset + 35, y))
            y += 10
        
        y += 8
    
    hint = font_tiny.render("Pressione D para ocultar", True, DARK_GRAY)
    screen.blit(hint, (x_offset + 10, HEIGHT - 15))