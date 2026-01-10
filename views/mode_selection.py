from views.base_menu import run_menu_screen

def show_mode_selection():
    return run_menu_screen(
        caption="Sistema de Rotas - Seleção de Modo",
        title_text="Seleção de Modo",
        subtitle_text="Escolha o tipo de otimização a ser executada",
        options=[
            ("TSP - 1 Veículo (rota única)", "tsp"),
            ("VRP - Múltiplos Veículos", "vrp"),
            ("Voltar", "back"),
        ],
        default_selected=0
    )
