# vrp_details_window.py

import pygame
import os
from typing import List, Dict
from config import *
from route_helpers import get_city_priority_info


class VRPDetailsWindow:
    def __init__(self, width=800, height=900):
        self.width = width
        self.height = height
        self.window = None
        self.active = False
        self.scroll_offset = 0
        
        self.font_title = pygame.font.SysFont("Arial", 13, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 10)
        self.font_small = pygame.font.SysFont("Arial", 9)
        self.font_tiny = pygame.font.SysFont("Arial", 8)
        
    def open(self):
        if not self.active:
            os.environ['SDL_VIDEO_WINDOW_POS'] = f"{1500},{100}"
            self.window = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
            pygame.display.set_caption("VRP - Detalhes das Rotas")
            self.active = True
            
    def close(self):
        if self.active:
            self.active = False
            
    def render(self, vrp_routes, coord_to_city, deliveries_by_city, depot_city=None, iteration=0):
        if not self.active or not self.window:
            return
            
        self.window.fill(WHITE)
        
        title = self.font_title.render(f"VRP - Detalhes Completos (Iteração {iteration})", True, BLACK)
        self.window.blit(title, (20, 5))
        
        y = 25
        
        total_distance = sum(r.total_distance for r in vrp_routes)
        total_weight = sum(r.total_weight for r in vrp_routes)
        total_cost = sum(r.total_cost for r in vrp_routes)
        
        summary_text = [
            f"Total de Rotas: {len(vrp_routes)}",
            f"Distância Total: {total_distance:.1f} km",
            f"Peso Total: {total_weight:.1f} kg",
            f"Custo Total: R$ {total_cost:.2f}"
        ]
        
        if depot_city:
            summary_text.append(f"Depósito: {depot_city}")
        
        pygame.draw.rect(self.window, GRAY, (10, y, self.width - 20, 80))
        pygame.draw.rect(self.window, BLACK, (10, y, self.width - 20, 80), 2)
        
        y += 8
        for text in summary_text:
            txt = self.font_normal.render(text, True, BLACK)
            self.window.blit(txt, (20, y))
            y += 15
        
        y += 12
        
        violations = 0
        for route in vrp_routes:
            weight_limit = route.vehicle.max_weight
            distance_limit = route.vehicle.max_distance * 0.85
            
            if route.total_weight > weight_limit or route.total_distance > distance_limit:
                violations += 1
        
        if violations > 0:
            warning = self.font_normal.render(
                f"⚠️ {violations} rota(s) excedem limites do veículo",
                True, RED
            )
            self.window.blit(warning, (20, y))
        else:
            ok_text = self.font_normal.render(
                "✅ Todas as rotas dentro dos limites",
                True, GREEN
            )
            self.window.blit(ok_text, (20, y))
        
        y += 25
        
        separator = self.font_title.render("Detalhes por Rota", True, BLACK)
        self.window.blit(separator, (20, y))
        y += 20
        
        priority_colors = {0: RED, 1: ORANGE, 2: GREEN}
        priority_labels = {0: "P0", 1: "P1", 2: "P2"}
        
        vehicle_usage = {}
        for route in vrp_routes:
            vid = route.vehicle.vehicle_id
            vehicle_usage[vid] = vehicle_usage.get(vid, 0) + 1
        
        for i, route in enumerate(vrp_routes):
            if y > self.height - 50:
                overflow = self.font_small.render(
                    f"... +{len(vrp_routes) - i} rotas (role para baixo)",
                    True, DARK_GRAY
                )
                self.window.blit(overflow, (20, y))
                break
            
            route_color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
            max_priority = getattr(route, 'max_priority', 2)
            avg_priority = getattr(route, 'avg_priority', 2.0)
            priority_color = priority_colors.get(max_priority, GRAY)
            
            box_height = 75 + len(route.route) * 10
            pygame.draw.rect(self.window, GRAY, (10, y, self.width - 20, box_height))
            pygame.draw.rect(self.window, route_color, (10, y, self.width - 20, box_height), 3)
            
            y += 6
            
            pygame.draw.rect(self.window, route_color, (20, y, 15, 15))
            pygame.draw.rect(self.window, BLACK, (20, y, 15, 15), 1)
            
            pygame.draw.circle(self.window, priority_color, (43, y + 7), 6)
            pygame.draw.circle(self.window, BLACK, (43, y + 7), 6, 1)
            
            priority_text = priority_labels.get(max_priority, "?")
            priority_txt = self.font_tiny.render(priority_text, True, WHITE)
            self.window.blit(priority_txt, (39, y + 2))
            
            route_title = f"Rota #{i+1}: {route.vehicle.name}"
            if vehicle_usage.get(route.vehicle.vehicle_id, 0) > 1:
                route_title += " ⚠️ (REUTILIZADO)"
                title_color = RED
            else:
                title_color = BLACK
            
            txt = self.font_title.render(route_title, True, title_color)
            self.window.blit(txt, (55, y))
            y += 15
            
            details = [
                f"Veículo ID: {route.vehicle.vehicle_id}",
                f"Cidades: {len(route.route)}",
                f"Distância: {route.total_distance:.1f} km (Limite: {route.vehicle.max_distance} km)",
                f"Peso: {route.total_weight:.1f} kg (Limite: {route.vehicle.max_weight} kg)",
                f"Custo: R$ {route.total_cost:.2f} (R$ {route.vehicle.cost_per_km:.2f}/km)",
                f"Prioridade Máxima: {priority_labels.get(max_priority, '?')} | Média: {avg_priority:.2f}"
            ]
            
            weight_limit = route.vehicle.max_weight
            distance_limit = route.vehicle.max_distance * 0.85
            
            weight_ok = route.total_weight <= weight_limit
            distance_ok = route.total_distance <= distance_limit
            
            if not weight_ok or not distance_ok:
                warning_parts = []
                if not weight_ok:
                    warning_parts.append(f"PESO EXCEDE: {route.total_weight:.0f} > {weight_limit:.0f} kg")
                if not distance_ok:
                    warning_parts.append(f"DISTÂNCIA EXCEDE: {route.total_distance:.0f} > {distance_limit:.0f} km")
                
                details.append("⚠️ " + " | ".join(warning_parts))
            
            for detail in details:
                if "⚠️" in detail or "EXCEDE" in detail:
                    txt = self.font_small.render(detail, True, RED)
                else:
                    txt = self.font_small.render(detail, True, (60, 60, 60))
                self.window.blit(txt, (25, y))
                y += 11
            
            y += 3
            cities_header = self.font_normal.render("Ordem de Entrega:", True, BLACK)
            self.window.blit(cities_header, (25, y))
            y += 14
            
            if depot_city:
                depot_txt = self.font_small.render(f"0. {depot_city} (DEPÓSITO)", True, (0, 100, 200))
                self.window.blit(depot_txt, (35, y))
                y += 10
            
            for idx, coord in enumerate(route.route):
                city_name = coord_to_city.get(coord, "?")
                
                priority_text_city, priority_num, priority_color_city = get_city_priority_info(
                    city_name, deliveries_by_city
                )
                
                pygame.draw.circle(self.window, priority_color_city, (40, y + 5), 3)
                
                deliveries_info = ""
                if city_name in deliveries_by_city:
                    n_deliveries = len(deliveries_by_city[city_name])
                    total_weight_city = sum(d.total_weight for d in deliveries_by_city[city_name])
                    deliveries_info = f" - {n_deliveries} entrega(s), {total_weight_city:.1f}kg"
                
                city_text = f"{idx+1}. {city_name} [{priority_text_city.split()[0]}]{deliveries_info}"
                city_txt = self.font_small.render(city_text, True, (40, 40, 40))
                self.window.blit(city_txt, (48, y))
                y += 10
            
            if depot_city:
                depot_txt = self.font_small.render(f"{len(route.route)+1}. {depot_city} (RETORNO)", True, (0, 100, 200))
                self.window.blit(depot_txt, (35, y))
                y += 10
            
            y += 8
        
        pygame.display.flip()
        
    def handle_events(self):
        if not self.active:
            return True
            
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_d:
                    self.close()
                    return False
        return True