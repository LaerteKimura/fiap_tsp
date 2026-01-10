# views/vrp_view.py
import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN, K_c, K_g, K_p, K_i, K_r, K_e
from datetime import datetime

from config import (
    WIDTH, HEIGHT, INFO_WIDTH,
    PLOT_Y, PLOT_H, VEHICLE_H,
    ACTIONBAR_H, DEFAULT_SHOW_COORDINATES, DEFAULT_SHOW_PLOT,
    WHITE, GRAY, BLACK, RED, DARK_GRAY,
    VRP_GENERATIONS_PER_ROUTE,
)

from vrp_solver import solve_vrp
from ui_resources.vrp_details_renderer import render_vrp_details_panel

from ui_resources.ui_renderer import (
    render_screen_header,
    render_vrp_evolution_plots,
    render_vrp_summary,
    render_map_with_vrp_routes,
    render_action_bar,
)

try:
    from ui_resources.ui_renderer import render_vrp_initial_search
except ImportError:
    render_vrp_initial_search = None


def _draw_loading(screen: pygame.Surface):
    font = pygame.font.SysFont("Arial", 16, bold=True)
    small_font = pygame.font.SysFont("Arial", 14)

    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, (0, 0, INFO_WIDTH, HEIGHT))

    title = font.render("🚚 Calculando Solução VRP...", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 50))

    msg1 = small_font.render("Analisando cidades e veículos", True, DARK_GRAY)
    screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2))

    msg2 = small_font.render("Isso pode levar alguns segundos...", True, DARK_GRAY)
    screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 25))

    pygame.display.flip()


def run_vrp_mode(data, ga_config, depot_city, export_fn=None):
    deliveries_by_city = data["deliveries_by_city"]
    cities = data["cities"]
    distance_lookup = data["distance_lookup"]
    vehicles = data["vehicles"]
    city_latlng = data["city_latlng"]
    city_to_coord = data["city_to_coord"]
    coords = data["coords"]
    coord_to_city = data["coord_to_city"]
    map_surface = data["map_surface"]

    depot_coord = city_to_coord.get(depot_city) if depot_city else None

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("VRP - Calculando solução inicial...")

    _draw_loading(screen)

    vrp_routes, initial_history = solve_vrp(
        coords,
        coord_to_city,
        deliveries_by_city,
        distance_lookup,
        vehicles,
        ga_config,
        depot_city,
        VRP_GENERATIONS_PER_ROUTE,
    )

    pygame.display.set_caption("VRP - São Paulo (C=coords | G=gráfico | I=busca | R=recalcular | E=exportar)")
    clock = pygame.time.Clock()

    show_coordinates = DEFAULT_SHOW_COORDINATES
    show_plot = DEFAULT_SHOW_PLOT
    show_initial_search = False
    paused = False

    cost_history = initial_history.get("cost_history", [])[:]
    distance_history = initial_history.get("distance_history", [])[:]
    attempts_history = initial_history.get("attempts", [])[:]

    iteration = 0

    details_scroll = 0
    details_rect = None
    max_details_scroll = 0

    while True:
        # -------------------------
        # Eventos
        # -------------------------
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                raise SystemExit

            if e.type == KEYDOWN:
                if e.key == K_c:
                    show_coordinates = not show_coordinates

                elif e.key == K_g:
                    show_plot = not show_plot

                elif e.key == K_p:
                    paused = not paused

                elif e.key == K_i:
                    show_initial_search = not show_initial_search

                elif e.key == K_r:
                    _draw_loading(screen)
                    vrp_routes, initial_history = solve_vrp(
                        coords,
                        coord_to_city,
                        deliveries_by_city,
                        distance_lookup,
                        vehicles,
                        ga_config,
                        depot_city,
                        VRP_GENERATIONS_PER_ROUTE,
                    )
                    cost_history = initial_history.get("cost_history", [])[:]
                    distance_history = initial_history.get("distance_history", [])[:]
                    attempts_history = initial_history.get("attempts", [])[:]
                    iteration = 0
                    details_scroll = 0

                elif e.key == K_e:
                    if export_fn and vrp_routes:
                        filename = f"vrp_solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        export_fn(data, vrp_routes, "VRP", depot_city, export_path=filename)

            elif e.type == pygame.MOUSEWHEEL:
                if details_rect is not None:
                    mx, my = pygame.mouse.get_pos()
                    if details_rect.collidepoint(mx, my):
                        details_scroll -= e.y * 30
                        details_scroll = max(0, min(details_scroll, max_details_scroll))

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos

                if "back_btn_rect" in locals() and back_btn_rect.collidepoint(mx, my):
                    return "back"

                if "coords_btn_rect" in locals() and coords_btn_rect.collidepoint(mx, my):
                    show_coordinates = not show_coordinates

                if "export_btn_rect" in locals() and export_btn_rect.collidepoint(mx, my):
                    export_enabled = (export_fn is not None) and bool(vrp_routes)
                    if export_enabled:
                        filename = f"vrp_solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        export_fn(data, vrp_routes, "VRP", depot_city, export_path=filename)
                        return "back"

        # -------------------------
        # Pausado
        # -------------------------
        if paused:
            screen.fill(WHITE)
            pause_font = pygame.font.SysFont("Arial", 14)
            pause_text = pause_font.render("PAUSADO - Pressione P para continuar", True, RED)
            screen.blit(pause_text, (screen.get_width() // 2 - 160, HEIGHT // 2))
            pygame.display.flip()
            clock.tick(10)
            continue

        # -------------------------
        # Re-otimização periódica
        # -------------------------
        iteration += 1

        if iteration % 30 == 0:
            new_routes, _new_history = solve_vrp(
                coords,
                coord_to_city,
                deliveries_by_city,
                distance_lookup,
                vehicles,
                ga_config,
                depot_city,
                VRP_GENERATIONS_PER_ROUTE // 3,
            )

            new_cost = sum(r.total_cost for r in new_routes)
            best_cost = sum(r.total_cost for r in vrp_routes)

            if new_cost < best_cost:
                vrp_routes = new_routes

            cost_history.append(min(new_cost, best_cost))
            distance_history.append(sum(r.total_distance for r in vrp_routes))

        # -------------------------
        # Layout base
        # -------------------------
        screen.fill(WHITE)
        pygame.draw.rect(screen, GRAY, (0, 0, INFO_WIDTH, HEIGHT))
        pygame.draw.line(screen, BLACK, (INFO_WIDTH, 0), (INFO_WIDTH, HEIGHT), 2)

        header_h = render_screen_header(
            screen,
            pygame.Rect(0, 0, INFO_WIDTH, 64),
            "VRP - Otimização (Algoritmo Genético)",
            "./assets/location_pin.png",
        )

        # empurra os plots para começar logo abaixo do header
        y_off = max(0, (header_h + 8) - PLOT_Y)

        # -------------------------
        # Painel de gráficos / busca inicial
        # -------------------------
        panel_h = 0

        if show_initial_search and attempts_history and render_vrp_initial_search:
            render_vrp_initial_search(screen, attempts_history, y_offset=y_off)
            panel_h = PLOT_H + 50

        elif show_plot and len(cost_history) > 1:
            render_vrp_evolution_plots(screen, cost_history, distance_history, True, y_offset=y_off)
            panel_h = PLOT_H

        else:
            # mesmo quando não renderiza, considere que a área do plot existe
            # pra não "despencar" o status e ficar inconsistente.
            panel_h = PLOT_H

        # ✅ aqui é o ajuste que resolve seu problema:
        # o summary SEMPRE começa logo após a área do plot (independente do conteúdo)
        summary_y = PLOT_Y + y_off + panel_h + 12

        render_vrp_summary(
            screen,
            vrp_routes,
            depot_city,
            panel_y=summary_y,
        )

        # -------------------------
        # Detalhes (abaixo do status)
        # -------------------------
        details_y = summary_y + VEHICLE_H + 12
        details_h = (HEIGHT - ACTIONBAR_H) - details_y - 12
        details_h = max(140, details_h)

        details_rect = pygame.Rect(20, details_y, INFO_WIDTH - 40, details_h)

        max_details_scroll = render_vrp_details_panel(
            screen,
            vrp_routes,
            coord_to_city,
            deliveries_by_city,
            depot_city,
            iteration,
            panel_rect=details_rect,
            scroll_y=details_scroll,
        )

        details_scroll = max(0, min(details_scroll, max_details_scroll))

        # -------------------------
        # Mapa
        # -------------------------
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
            depot_coord,
        )

        # -------------------------
        # Action bar
        # -------------------------
        export_enabled = (export_fn is not None) and bool(vrp_routes)
        back_btn_rect, coords_btn_rect, export_btn_rect = render_action_bar(
            screen,
            export_enabled=export_enabled,
            show_coordinates=show_coordinates,
        )

        pygame.display.flip()
        clock.tick(30)
