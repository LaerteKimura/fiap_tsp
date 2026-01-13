from views.base_menu import run_menu_screen

def show_analyze_menu():
    return run_menu_screen(
        caption="Sistema de Rotas - Menu Inicial",
        title_text="Sistema de Rotas",
        subtitle_text="Otimização TSP/VRP com Algoritmos Genéticos e Relatórios via LLM",
        options=[
            ("Analisar solução existente", "analyze"),
            ("Abrir relatório existente", "open_report"),
            ("Criar nova solução", "new"),
            ("Sair", "skip"),
        ],
        default_selected=0
    )
