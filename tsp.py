# -*- coding: utf-8 -*-

import sys
import random
import itertools
import pygame
from pygame.locals import *
from collections import defaultdict
from sp_map import * 

from ga_menu import choose_ga_config
from delivery_loader import load_deliveries
from vehicle_loader import load_vehicles

from genetic_algorithm import (
    generate_random_population,
    calculate_fitness,
    sort_population
)

from draw_functions import (
    draw_paths,
    draw_plot,
    draw_cities
)

from city_loader import (
    load_distances_from_tsv,
    load_city_coordinates_from_csv,
    latlng_to_screen_coordinates
)


# =========================
# SCREEN
# =========================

INFO_WIDTH = 400
MAP_WIDTH = 850
HEIGHT = 720
WIDTH = INFO_WIDTH + MAP_WIDTH

# =========================
# INFO PANEL LAYOUT
# =========================

PLOT_Y = 20
PLOT_H = 300

LIST_Y = PLOT_Y + PLOT_H + 20
LIST_H = 200

VEHICLE_Y = LIST_Y + LIST_H + 15

# =========================
# COLORS
# =========================

WHITE = (255, 255, 255)
GRAY = (240, 240, 240)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 80, 220)
LIGHT_GRAY = (180, 180, 180)

# =========================
# LOAD DATA
# =========================

_, distance_lookup = load_distances_from_tsv("cidades_sp.tsv")

deliveries = load_deliveries("deliveries.csv")
deliveries_by_city = defaultdict(list)
for d in deliveries:
    deliveries_by_city[d.city].append(d)

vehicles = load_vehicles("veiculos.csv")
cities = sorted(deliveries_by_city.keys())

from city_loader import (
    load_distances_from_tsv,
    load_city_coordinates_from_csv,
    latlng_to_screen_coordinates
)

city_latlng = load_city_coordinates_from_csv("worldcities.csv", cities)

missing = set(cities) - set(city_latlng.keys())
if missing:
    print("⚠️ CIDADES SEM COORDENADAS:", missing)


city_to_coord = latlng_to_screen_coordinates(
    city_latlng,
    MAP_WIDTH - 40,
    HEIGHT - 40,
    INFO_WIDTH + 20,
    20
)


coords = [city_to_coord[c] for c in cities]
coord_to_city = {v: k for k, v in city_to_coord.items()}



city_to_coord = dict(zip(cities, coords))
coord_to_city = {v: k for k, v in city_to_coord.items()}

# =========================
# HELPERS
# =========================

def city_priority(city):
    return min(d.priority for d in deliveries_by_city[city])


def route_total_weight(route):
    total = 0.0
    for coord in route:
        city = coord_to_city[coord]
        for d in deliveries_by_city[city]:
            total += d.total_weight
    return total


def route_total_distance(route):
    dist = 0.0
    for i in range(len(route)):
        x1, y1 = route[i]
        x2, y2 = route[(i + 1) % len(route)]
        dist += ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    return dist


def choose_vehicle(total_weight, total_distance):
    viable = [
        v for v in vehicles
        if total_weight <= v.max_weight
        and total_distance <= v.max_distance
    ]
    if not viable:
        return None
    return min(viable, key=lambda v: v.cost_per_km)

# =========================
# PYGAME INIT
# =========================

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSP – Genetic Algorithm")
font = pygame.font.SysFont("Arial", 14)
clock = pygame.time.Clock()

# =========================
# TOGGLES
# =========================

show_plot = True
show_list = True
show_attempts = True

# =========================
# GA INIT
# =========================

POP = 100
population = generate_random_population(coords, POP)

best_history = []

ga = choose_ga_config()


# rendering map
map_surface = build_sp_map_surface(
    size=(MAP_WIDTH, HEIGHT),
    geojson_path="geojs-35-mun.json"
)


# =========================
# LOOP
# =========================

gen = itertools.count(1)
running = True

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

    generation = next(gen)

    # =========================
    # BACKGROUND
    # =========================

    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, (0, 0, INFO_WIDTH, HEIGHT))
    pygame.draw.line(screen, BLACK, (INFO_WIDTH, 0), (INFO_WIDTH, HEIGHT), 2)

    # =========================
    # FITNESS
    # =========================

    fitness = [
        calculate_fitness(
            ind,
            coord_to_city,
            deliveries_by_city,
            vehicles,
            distance_lookup,
            priority_weight=20
        )
        for ind in population
    ]

    population, fitness = sort_population(population, fitness)
    best = population[0]
    best_history.append(fitness[0])

    # =========================
    # PLOT
    # =========================

    if show_plot:
        plot_surface = screen.subsurface(
            pygame.Rect(20, PLOT_Y, INFO_WIDTH - 40, PLOT_H)
        )
        plot_surface.fill(GRAY)

        draw_plot(
            plot_surface,
            list(range(len(best_history))),
            best_history,
            "Fitness",
            (0, 0),
            size_px=(INFO_WIDTH - 40, PLOT_H)
        )

    # =========================
    # ROUTE LIST
    # =========================

    if show_list:
        list_rect = pygame.Rect(20, LIST_Y, INFO_WIDTH - 40, LIST_H)
        pygame.draw.rect(screen, GRAY, list_rect)

        clip = screen.subsurface(list_rect)
        y = 5

        for i, coord in enumerate(best):
            city = coord_to_city[coord]
            p = city_priority(city)
            txt = font.render(f"{i+1}. {city} | P{p}", True, BLACK)
            clip.blit(txt, (5, y))
            y += 18
            if y > LIST_H - 10:
                break

    # =========================
    # VEHICLE INFO (COM DISTÂNCIA)
    # =========================

    total_weight = route_total_weight(best)
    total_distance = route_total_distance(best)
    vehicle = choose_vehicle(total_weight, total_distance)

    info_rect = pygame.Rect(20, VEHICLE_Y, INFO_WIDTH - 40, 90)
    pygame.draw.rect(screen, GRAY, info_rect)

    y = VEHICLE_Y + 8
    screen.blit(font.render(
        f"Total load weight: {total_weight:.1f} kg", True, BLACK), (30, y)
    )
    y += 18

    screen.blit(font.render(
        f"Route distance: {total_distance:.1f} km", True, BLACK), (30, y)
    )
    y += 18

    if vehicle:
        screen.blit(font.render(
            f"Vehicle: {vehicle.name} | max {vehicle.max_distance} km",
            True, BLACK), (30, y)
        )
    else:
        screen.blit(font.render(
            "No vehicle meets distance/weight constraints!",
            True, (180, 0, 0)), (30, y)
        )

    # =========================
    # FOOTER
    # =========================

    footer = [
        f"Generation: {generation}",
        f"Best fitness: {fitness[0]:.2f}",
        "G = plot | L = list | T = attempts | Q = quit"
    ]

    y = HEIGHT - 60
    for line in footer:
        screen.blit(font.render(line, True, BLACK), (20, y))
        y += 18

    # test map rendering
    map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT)
    best_history = []

    screen.set_clip(map_rect)

    screen.blit(map_surface, map_rect.topleft)

    if show_attempts:
        attempt = random.choice(population[1:10])
        draw_paths(screen, attempt, LIGHT_GRAY, 1)

    draw_paths(screen, best, BLUE, 3)
    draw_cities(screen, coords, cities, RED, 8, font)

    screen.set_clip(None)
    

    # =========================
    # MAP
    # =========================

    map_rect = pygame.Rect(INFO_WIDTH, 0, MAP_WIDTH, HEIGHT)
    screen.set_clip(map_rect)

    if show_attempts:
        attempt = random.choice(population[1:10])
        draw_paths(screen, attempt, LIGHT_GRAY, 1)

    draw_paths(screen, best, BLUE, 3)
    draw_cities(screen, coords, cities, RED, 8, font)

    screen.set_clip(None)

    # =========================
    # REPRODUCTION
    # =========================

    new_pop = [population[0]]
    while len(new_pop) < POP:
        p1, p2 = ga["selection_fn"](population, fitness)
        child = ga["crossover_fn"](p1, p2)
        child = ga["mutation_fn"](child, 0.4)
        new_pop.append(child)

    population = new_pop

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
