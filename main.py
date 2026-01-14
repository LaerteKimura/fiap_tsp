import sys
import pygame
from pygame.locals import *
import route_analyzer

from config import *
from loader_resources.data_loader import load_all_data

from infra.solution_exporter import export_solution_to_json

from views.menu_inicial import show_analyze_menu
from views.mode_selection import show_mode_selection
from views.ga_menu import show_ga_menu
from views.tsp_view import run_tsp_mode
from views.vrp_view import run_vrp_mode
from views.vrp_depot_selection import show_vrp_depot_selection

import os
os.environ["SDL_VIDEO_CENTERED"] = "1"

def run_analyze_flow():
    """Executa o modo análise com interface gráfica."""
    from views.analyze_view import run_analyze_mode
    try:
        run_analyze_mode()
    except Exception as e:
        print(f"Erro ao executar análise: {e}")
    # Retorna ao menu inicial após análise
    return

def run_open_report_flow():
    """Executa o modo de abrir relatório existente."""
    from views.open_report_view import show_open_report_menu
    pygame.init()
    
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Abrir Relatório PDF")
    clock = pygame.time.Clock()
    
    try:
        show_open_report_menu(screen, clock)
    except Exception as e:
        print(f"Erro ao abrir relatório: {e}")
    finally:
        pygame.quit()
    # Retorna ao menu inicial
    return

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
            continue

        if initial_choice == "open_report":
            run_open_report_flow()
            continue

        run_solver_flow(data)

def main():
    data = load_all_data()
    pygame.init()

    run_main_menu_flow(data)
    sys.exit()

if __name__ == "__main__":
    main()
