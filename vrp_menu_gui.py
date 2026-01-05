# vrp_menu_gui.py

import pygame
from pygame.locals import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (240, 240, 240)
DARK_GRAY = (180, 180, 180)
BLUE = (50, 120, 220)
GREEN = (50, 180, 50)
ORANGE = (255, 165, 0)


class Button:
    def __init__(self, x, y, width, height, text, value):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.selected = False
        
    def draw(self, surface, font):
        color = BLUE if self.selected else GRAY
        text_color = WHITE if self.selected else BLACK
            
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2)
        
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def show_mode_selection():
    """
    Menu para escolher entre TSP ou VRP.
    """
    pygame.init()
    
    WIDTH = 600
    HEIGHT = 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Seleção de Modo")
    
    font_title = pygame.font.SysFont("Arial", 28, bold=True)
    font_normal = pygame.font.SysFont("Arial", 16)
    font_small = pygame.font.SysFont("Arial", 14)
    
    mode_buttons = [
        Button(100, 150, 180, 80, "TSP\n(1 Veículo)", "tsp"),
        Button(320, 150, 180, 80, "VRP\n(Múltiplos)", "vrp")
    ]
    mode_buttons[0].selected = True
    
    start_button = Button(200, 300, 200, 50, "CONTINUAR", "start")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                import sys
                sys.exit()
                
            elif event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                
                for btn in mode_buttons:
                    if btn.is_clicked(pos):
                        for b in mode_buttons:
                            b.selected = False
                        btn.selected = True
                
                if start_button.is_clicked(pos):
                    running = False
            
            elif event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    running = False
        
        screen.fill(WHITE)
        
        title = font_title.render("Selecione o Modo de Operação", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        desc = font_small.render("TSP: Uma única rota otimizada | VRP: Múltiplas rotas com vários veículos", True, DARK_GRAY)
        screen.blit(desc, (WIDTH//2 - desc.get_width()//2, 100))
        
        for btn in mode_buttons:
            btn.draw(screen, font_small)
        
        pygame.draw.rect(screen, GREEN, start_button.rect)
        pygame.draw.rect(screen, BLACK, start_button.rect, 2)
        start_text = font_normal.render(start_button.text, True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button.rect.center)
        screen.blit(start_text, start_text_rect)
        
        pygame.display.flip()
        clock.tick(30)
    
    mode = next(btn.value for btn in mode_buttons if btn.selected)
    
    pygame.display.quit()
    pygame.display.init()
    
    return mode


def show_vrp_depot_selection(cities):
    """
    Menu para selecionar depósito central (opcional).
    """
    pygame.init()
    
    WIDTH = 700
    HEIGHT = 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Seleção de Depósito Central")
    
    font_title = pygame.font.SysFont("Arial", 24, bold=True)
    font_normal = pygame.font.SysFont("Arial", 14)
    font_small = pygame.font.SysFont("Arial", 12)
    
    no_depot_button = Button(50, 100, 280, 60, "Sem Depósito Central", None)
    no_depot_button.selected = True
    
    city_buttons = []
    y_pos = 180
    x_pos = 50
    btn_width = 200
    btn_height = 35
    
    for i, city in enumerate(sorted(cities)):
        if i > 0 and i % 10 == 0:
            x_pos += btn_width + 20
            y_pos = 180
        
        btn = Button(x_pos, y_pos, btn_width, btn_height, city[:18], city)
        city_buttons.append(btn)
        y_pos += btn_height + 5
    
    start_button = Button(250, 520, 200, 50, "INICIAR VRP", "start")
    
    clock = pygame.time.Clock()
    running = True
    scroll_offset = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                import sys
                sys.exit()
                
            elif event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                
                if no_depot_button.is_clicked(pos):
                    no_depot_button.selected = True
                    for btn in city_buttons:
                        btn.selected = False
                
                for btn in city_buttons:
                    if btn.is_clicked(pos):
                        no_depot_button.selected = False
                        for b in city_buttons:
                            b.selected = False
                        btn.selected = True
                
                if start_button.is_clicked(pos):
                    running = False
            
            elif event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    running = False
        
        screen.fill(WHITE)
        
        title = font_title.render("Configuração VRP - Depósito Central", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        desc1 = font_small.render("Escolha um depósito central ou opere sem depósito", True, DARK_GRAY)
        screen.blit(desc1, (WIDTH//2 - desc1.get_width()//2, 55))
        desc2 = font_small.render("Com depósito: todos os veículos partem/retornam ao mesmo local", True, DARK_GRAY)
        screen.blit(desc2, (WIDTH//2 - desc2.get_width()//2, 70))
        
        no_depot_button.draw(screen, font_normal)
        
        cities_label = font_normal.render("Ou selecione uma cidade como depósito:", True, BLACK)
        screen.blit(cities_label, (50, 150))
        
        for btn in city_buttons:
            btn.draw(screen, font_small)
        
        pygame.draw.rect(screen, ORANGE, start_button.rect)
        pygame.draw.rect(screen, BLACK, start_button.rect, 2)
        start_text = font_normal.render(start_button.text, True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button.rect.center)
        screen.blit(start_text, start_text_rect)
        
        hint = font_small.render("Pressione ENTER para iniciar", True, DARK_GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 495))
        
        pygame.display.flip()
        clock.tick(30)
    
    if no_depot_button.selected:
        depot = None
    else:
        depot = next((btn.value for btn in city_buttons if btn.selected), None)
    
    pygame.display.quit()
    pygame.display.init()
    
    print(f"\n📍 Depósito selecionado: {depot if depot else 'Nenhum (sem depósito central)'}")
    
    return depot