import itertools
import pygame
from pygame.locals import *
from datetime import datetime

from config import (
    WIDTH, HEIGHT, INFO_WIDTH,
    POPULATION_SIZE, MUTATION_RATE,
    DEFAULT_SHOW_PLOT, DEFAULT_SHOW_LIST,
    DEFAULT_SHOW_ATTEMPTS, DEFAULT_SHOW_COORDINATES,
    PRIORITY_WEIGHT,
    WHITE, GRAY, BLACK, RED,
)

from genetic_algorithm import (
    generate_random_population,
    calculate_fitness,
    sort_population,
)

from route_helpers import (
    calculate_route_weight,
    calculate_route_distance,
    select_vehicle,
)

from ui_resources.ui_renderer import (
    render_action_bar,
    render_evolution_plots,
    render_route_list,
    render_screen_header,
    render_status,
    render_vehicle_info,
    render_map_with_routes,
)

def run_tsp_mode(data, ga_config, export_fn=None):
    deliveries_by_city = data["deliveries_by_city"]
    cities = data["cities"]
    distance_lookup = data["distance_lookup"]
    vehicles = data["vehicles"]
    city_latlng = data["city_latlng"]
    coords = data["coords"]
    coord_to_city = data["coord_to_city"]
    map_surface = data["map_surface"]

    population = generate_random_population(coords, POPULATION_SIZE)
    best_history = []
    distance_history = []
    best_solution = None
    best_solution_fitness = float("inf")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSP - São Paulo (E=exportar | Q=sair)")
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
                # clicar no X deve encerrar o app todo
                pygame.quit()
                raise SystemExit
                
            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos

                if 'back_btn_rect' in locals() and back_btn_rect.collidepoint(mx, my):
                    return "back"

                if 'coords_btn_rect' in locals() and coords_btn_rect.collidepoint(mx, my):
                    show_coordinates = not show_coordinates

                if 'export_btn_rect' in locals() and export_btn_rect.collidepoint(mx, my) and export_enabled:
                    filename = f"tsp_solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    export_fn(data, best_solution, "TSP", export_path=filename)
                    return "back"

        if paused:
            screen.fill(WHITE)
            font = pygame.font.SysFont("Arial", 14)
            pause_text = font.render("PAUSADO - Pressione P para continuar", True, RED)
            screen.blit(pause_text, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.flip()
            clock.tick(10)
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
                priority_weight=PRIORITY_WEIGHT,
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

        if best_fitness < best_solution_fitness:
            best_solution = best[:]
            best_solution_fitness = best_fitness

        render_screen_header(
            screen,
            pygame.Rect(0, 0, INFO_WIDTH, 64),
            "TSP - Otimização (Algoritmo Genético)",
            "./assets/location_pin.png",
        )

        render_evolution_plots(screen, best_history, distance_history, show_plot)
        
        render_route_list(screen, best, coord_to_city, deliveries_by_city, distance_lookup, show_list)

        render_vehicle_info(screen, total_weight, total_distance_km, vehicle, vehicles)

        render_status(screen, generation, best_fitness, len(best))

        # mouse_pos = pygame.mouse.get_pos()
        # mouse_down = pygame.mouse.get_pressed()[0]
        export_enabled = best_solution is not None and export_fn is not None
        back_btn_rect, coords_btn_rect, export_btn_rect = render_action_bar(
            screen,
            export_enabled=export_enabled,
            show_coordinates=show_coordinates,
        )

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
            show_coordinates,
        )

        new_pop = [population[0]]
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = ga_config["selection_fn"](population, fitness)
            child = ga_config["crossover_fn"](p1, p2)
            child = ga_config["mutation_fn"](child, MUTATION_RATE)
            new_pop.append(child)

        population = new_pop

        pygame.display.flip()       

        clock.tick(30)
