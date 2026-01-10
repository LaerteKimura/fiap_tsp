import os
import math
import pygame
from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN,
    K_ESCAPE, K_BACKSPACE, K_RETURN, K_KP_ENTER, K_SPACE
)

from genetic_algorithm import MUTATION_TYPES, SELECTION_TYPES, CROSSOVER_TYPES


def show_ga_menu():
    pygame.init()

    WIDTH, HEIGHT = 900, 560
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sistema de Rotas - Configuração do GA")

    font_title = pygame.font.SysFont("Segoe UI", 36, bold=True)
    font_sub = pygame.font.SysFont("Segoe UI", 18)
    font_section = pygame.font.SysFont("Segoe UI", 16, bold=True)
    font_chip = pygame.font.SysFont("Segoe UI", 16, bold=True)
    font_hint = pygame.font.SysFont("Segoe UI", 14)

    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "..", "assets", "location_pin.png")

    logo = pygame.image.load(logo_path).convert_alpha()
    logo = pygame.transform.smoothscale(logo, (40, 40))

    clock = pygame.time.Clock()

    mutations = [("Swap", "swap"), ("Inversion", "inversion"), ("Scramble", "scramble")]
    selections = [("Tournament", "tournament"), ("Roulette", "roulette"), ("Rank", "rank")]
    crossovers = [("Order (OX)", "ox"), ("PMX", "pmx"), ("Cycle (CX)", "cx")]

    mutation_key = mutations[0][1]
    selection_key = selections[0][1]
    crossover_key = crossovers[0][1]

    def build_return():
        return {
            "mutation_fn": MUTATION_TYPES[mutation_key],
            "selection_fn": SELECTION_TYPES[selection_key],
            "crossover_fn": CROSSOVER_TYPES[crossover_key],
            "mutation_key": mutation_key,
            "selection_key": selection_key,
            "crossover_key": crossover_key,
        }

    def draw_chip(surface, rect, label, selected, hover):
        bg = (220, 235, 250) if selected else (245, 247, 250)
        if hover and not selected:
            bg = (235, 240, 246)

        border = (30, 90, 160) if selected else (200, 205, 210)
        text_color = (30, 90, 160) if selected else (70, 75, 85)

        pygame.draw.rect(surface, bg, rect, border_radius=12)
        pygame.draw.rect(surface, border, rect, width=1, border_radius=12)

        txt = font_chip.render(label, True, text_color)
        surface.blit(txt, txt.get_rect(center=rect.center))

    def chip_row(y, items, selected_value, card_x, card_w):
        mx, my = pygame.mouse.get_pos()

        left = card_x + 40
        total_w = card_w - 80
        gap = 14

        chip_w = (total_w - 2 * gap) // 3
        chip_h = 44

        rects = []
        for i, (label, key) in enumerate(items):
            x = left + i * (chip_w + gap)
            r = pygame.Rect(x, y, chip_w, chip_h)
            rects.append((r, key))
            draw_chip(screen, r, label, key == selected_value, r.collidepoint(mx, my))

        return rects

    mutation_rects = []
    selection_rects = []
    crossover_rects = []

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_BACKSPACE):
                    return "back"
                if event.key in (K_RETURN, K_KP_ENTER, K_SPACE):
                    return build_return()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                for r, key in mutation_rects:
                    if r.collidepoint(mx, my):
                        mutation_key = key

                for r, key in selection_rects:
                    if r.collidepoint(mx, my):
                        selection_key = key

                for r, key in crossover_rects:
                    if r.collidepoint(mx, my):
                        crossover_key = key

                if back_rect.collidepoint(mx, my):
                    return "back"

                if continue_rect.collidepoint(mx, my):
                    return build_return()

        # Fundo
        screen.fill((245, 247, 250))

        # Card
        card_w = int(WIDTH * 0.92)
        card_h = int(HEIGHT * 0.90)
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2

        pygame.draw.rect(screen, (210, 215, 220), (card_x + 5, card_y + 5, card_w, card_h), border_radius=18)
        pygame.draw.rect(screen, (255, 255, 255), (card_x, card_y, card_w, card_h), border_radius=18)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=18)

        # Topo
        logo_x = card_x + 40
        logo_y = card_y + 32
        screen.blit(logo, (logo_x, logo_y))

        title = font_title.render("Configuração do GA", True, (40, 45, 55))
        title_rect = title.get_rect(midleft=(logo_x + 60, logo_y + logo.get_height() // 2))
        screen.blit(title, title_rect)

        sub = font_sub.render("Escolha os operadores do Algoritmo Genético", True, (90, 95, 105))
        screen.blit(sub, (card_x + 40, card_y + 92))

        # Área de conteúdo (com folga real)
        content_top = card_y + 140

        y1 = content_top + 30
        y2 = y1 + 95
        y3 = y2 + 95

        section_x = card_x + 40

        screen.blit(font_section.render("Mutação", True, (60, 65, 75)), (section_x, y1 - 26))
        screen.blit(font_section.render("Seleção", True, (60, 65, 75)), (section_x, y2 - 26))
        screen.blit(font_section.render("Crossover", True, (60, 65, 75)), (section_x, y3 - 26))

        mutation_rects = chip_row(y1, mutations, mutation_key, card_x, card_w)
        selection_rects = chip_row(y2, selections, selection_key, card_x, card_w)
        crossover_rects = chip_row(y3, crossovers, crossover_key, card_x, card_w)

        # Rodapé: botões na mesma linha
        buttons_y = card_y + card_h - 78
        back_rect = pygame.Rect(card_x + 40, buttons_y, 170, 46)
        continue_rect = pygame.Rect(card_x + card_w - 230, buttons_y, 190, 46)

        mx, my = pygame.mouse.get_pos()

        # Voltar
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_chip.render("< Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        # Continuar
        cont_hover = continue_rect.collidepoint(mx, my)
        cont_bg = (220, 235, 250) if cont_hover else (245, 247, 250)
        pygame.draw.rect(screen, cont_bg, continue_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 90, 160), continue_rect, width=1, border_radius=12)

        pulse = 2 + int(2 * (1 + math.sin(pygame.time.get_ticks() / 320)))
        cont_txt = font_chip.render("Continuar >", True, (30, 90, 160))
        screen.blit(cont_txt, cont_txt.get_rect(center=(continue_rect.centerx + pulse, continue_rect.centery)))

        # Hint abaixo dos botões (com folga)
        hint = font_hint.render("Clique para selecionar • Enter continuar • Esc voltar", True, (120, 125, 135))
        screen.blit(hint, (card_x + 40, buttons_y + 54))

        pygame.display.flip()
        clock.tick(60)
