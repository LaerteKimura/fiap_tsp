import pygame
from pygame.locals import *
from genetic_algorithm import (
    MUTATION_TYPES,
    SELECTION_TYPES,
    CROSSOVER_TYPES
)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (240, 240, 240)
DARK_GRAY = (180, 180, 180)
BLUE = (50, 120, 220)
LIGHT_BLUE = (100, 150, 255)
GREEN = (50, 180, 50)

class Button:
    def __init__(self, x, y, width, height, text, value):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.selected = False
        
    def draw(self, surface, font):
        if self.selected:
            color = BLUE
            text_color = WHITE
        else:
            color = GRAY
            text_color = BLACK
            
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2)
        
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def show_ga_menu():
    """
    Mostra menu gráfico para escolher configurações do GA.
    Retorna dicionário com as escolhas.
    """
    pygame.init()
    
    WIDTH = 600
    HEIGHT = 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Configuração do Algoritmo Genético")
    
    font_title = pygame.font.SysFont("Arial", 24, bold=True)
    font_normal = pygame.font.SysFont("Arial", 16)
    font_small = pygame.font.SysFont("Arial", 14)
    
    mutation_buttons = [
        Button(50, 100, 150, 50, "Swap", "swap"),
        Button(225, 100, 150, 50, "Inversion", "inversion"),
        Button(400, 100, 150, 50, "Scramble", "scramble")
    ]
    mutation_buttons[0].selected = True
    
    selection_buttons = [
        Button(50, 220, 150, 50, "Tournament", "tournament"),
        Button(225, 220, 150, 50, "Roulette", "roulette"),
        Button(400, 220, 150, 50, "Rank", "rank")
    ]
    selection_buttons[0].selected = True
    
    crossover_buttons = [
        Button(50, 340, 150, 50, "Order (OX)", "ox"),
        Button(225, 340, 150, 50, "PMX", "pmx"),
        Button(400, 340, 150, 50, "Cycle (CX)", "cx")
    ]
    crossover_buttons[0].selected = True
    
    start_button = Button(200, 430, 200, 50, "INICIAR", "start")
    
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
                
                for btn in mutation_buttons:
                    if btn.is_clicked(pos):
                        for b in mutation_buttons:
                            b.selected = False
                        btn.selected = True
                
                for btn in selection_buttons:
                    if btn.is_clicked(pos):
                        for b in selection_buttons:
                            b.selected = False
                        btn.selected = True
                
                for btn in crossover_buttons:
                    if btn.is_clicked(pos):
                        for b in crossover_buttons:
                            b.selected = False
                        btn.selected = True
                
                if start_button.is_clicked(pos):
                    running = False
            
            elif event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    running = False
        
        screen.fill(WHITE)
        
        title = font_title.render("Configuração do Algoritmo Genético", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        mutation_label = font_normal.render("Tipo de Mutação:", True, BLACK)
        screen.blit(mutation_label, (50, 70))
        
        selection_label = font_normal.render("Método de Seleção:", True, BLACK)
        screen.blit(selection_label, (50, 190))
        
        crossover_label = font_normal.render("Tipo de Crossover:", True, BLACK)
        screen.blit(crossover_label, (50, 310))
        
        for btn in mutation_buttons:
            btn.draw(screen, font_small)
        
        for btn in selection_buttons:
            btn.draw(screen, font_small)
        
        for btn in crossover_buttons:
            btn.draw(screen, font_small)
        
        pygame.draw.rect(screen, GREEN, start_button.rect)
        pygame.draw.rect(screen, BLACK, start_button.rect, 2)
        start_text = font_normal.render(start_button.text, True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button.rect.center)
        screen.blit(start_text, start_text_rect)
        
        hint = font_small.render("Clique nas opções ou pressione ENTER para iniciar", True, DARK_GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 405))
        
        pygame.display.flip()
        clock.tick(30)
    
    mutation_key = next(btn.value for btn in mutation_buttons if btn.selected)
    selection_key = next(btn.value for btn in selection_buttons if btn.selected)
    crossover_key = next(btn.value for btn in crossover_buttons if btn.selected)
    
    pygame.display.quit()
    pygame.display.init()
    
    print(f"\n✓ Configurações escolhidas:")
    print(f"  Mutação: {mutation_key}")
    print(f"  Seleção: {selection_key}")
    print(f"  Crossover: {crossover_key}\n")
    
    return {
        "mutation_fn": MUTATION_TYPES[mutation_key],
        "selection_fn": SELECTION_TYPES[selection_key],
        "crossover_fn": CROSSOVER_TYPES[crossover_key],
        "mutation_key": mutation_key,
        "selection_key": selection_key,
        "crossover_key": crossover_key,
    }