# =========================
# GENETIC ALGORITHM
# =========================

POPULATION_SIZE = 100
MUTATION_RATE = 0.4
PRIORITY_WEIGHT = 20

# Elitismo: porcentagem da população mantida como elite (aplicado em TSP e VRP)
ELITE_PERCENTAGE = 0.1  # 10% da população mantida como elite

# =========================
# VRP SETTINGS
# =========================

VRP_GENERATIONS_PER_ROUTE = 200

# Custo fixo por rota (independente do veículo) - usado no cálculo de custo total
VRP_FIXED_COST_PER_ROUTE = 1500  # Custo fixo em R$ adicionado ao custo de cada rota

# Critérios de parada VRP - limites configuráveis para controle da evolução
VRP_MAX_GENERATIONS = 2000  # Máximo de gerações para VRP (evita execução infinita)
VRP_CONVERGENCE_GENERATIONS = 100  # Gerações sem melhoria para considerar convergência no VRP
VRP_CONVERGENCE_THRESHOLD = 0.002  # Melhoria mínima para resetar contador de convergência no VRP

# =========================
# UI TOGGLES (DEFAULT STATE)
# =========================

DEFAULT_SHOW_PLOT = True
DEFAULT_SHOW_LIST = True
DEFAULT_SHOW_ATTEMPTS = True
DEFAULT_SHOW_COORDINATES = False
