# config.py

# =========================
# SCREEN DIMENSIONS
# =========================

INFO_WIDTH = 400
MAP_WIDTH = 1080
DETAILS_WIDTH = 800
HEIGHT = 900
WIDTH = INFO_WIDTH + MAP_WIDTH
WIDTH_WITH_DETAILS = INFO_WIDTH + MAP_WIDTH + DETAILS_WIDTH

# =========================
# INFO PANEL LAYOUT
# =========================

PLOT_Y = 20
PLOT_H = 280

LIST_Y = PLOT_Y + PLOT_H + 10
LIST_H = 260

VEHICLE_Y = LIST_Y + LIST_H + 10
VEHICLE_H = 110

FOOTER_H = 120

# =========================
# COLORS
# =========================

WHITE = (255, 255, 255)
GRAY = (240, 240, 240)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 80, 220)
LIGHT_GRAY = (180, 180, 180)
GREEN = (50, 180, 50)
PURPLE = (180, 50, 180)
ORANGE = (255, 165, 0)
DARK_GRAY = (180, 180, 180)
LIGHT_BLUE = (100, 150, 255)

ROUTE_COLORS = [
    (50, 80, 220),    # Azul
    (220, 50, 50),    # Vermelho
    (50, 180, 50),    # Verde
    (255, 165, 0),    # Laranja
    (180, 50, 180),   # Roxo
    (0, 180, 180),    # Ciano
    (220, 180, 50),   # Amarelo escuro
    (150, 75, 0),     # Marrom
    (255, 105, 180),  # Rosa
    (128, 128, 128)   # Cinza
]

# =========================
# GENETIC ALGORITHM
# =========================

POPULATION_SIZE = 100
MUTATION_RATE = 0.4
PRIORITY_WEIGHT = 20

# =========================
# VRP SETTINGS
# =========================

VRP_GENERATIONS_PER_ROUTE = 100

# =========================
# UI TOGGLES (DEFAULT STATE)
# =========================

DEFAULT_SHOW_PLOT = True
DEFAULT_SHOW_LIST = True
DEFAULT_SHOW_ATTEMPTS = True
DEFAULT_SHOW_COORDINATES = False