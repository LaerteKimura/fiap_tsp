import os
import math
import pygame
from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN,
    K_ESCAPE, K_UP, K_w, K_DOWN, K_s,
    K_RETURN, K_KP_ENTER, K_SPACE
)

def run_menu_screen(
    caption: str,
    title_text: str,
    subtitle_text: str,
    options: list[tuple[str, str]],
    default_selected: int = 0,
    logo_filename: str = "location_pin.png"
) -> str:
    pygame.init()

    WIDTH, HEIGHT = 720, 420
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(caption)

    font_title = pygame.font.SysFont("Segoe UI", 34, bold=True)
    font_sub = pygame.font.SysFont("Segoe UI", 16)
    font_item = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_hint = pygame.font.SysFont("Segoe UI", 14)

    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "..", "assets", logo_filename)

    logo = pygame.image.load(logo_path).convert_alpha()
    logo = pygame.transform.smoothscale(logo, (36, 36))

    clock = pygame.time.Clock()

    selected = max(0, min(default_selected, len(options) - 1))
    option_rects = [None] * len(options)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for idx, rect in enumerate(option_rects):
                    if rect and rect.collidepoint(mx, my):
                        return options[idx][1]

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "back"
                if event.key in (K_UP, K_w):
                    selected = (selected - 1) % len(options)
                if event.key in (K_DOWN, K_s):
                    selected = (selected + 1) % len(options)
                if event.key in (K_RETURN, K_KP_ENTER, K_SPACE):
                    return options[selected][1]

        # Fundo + card
        screen.fill((245, 247, 250))

        card_w = int(WIDTH * 0.95)
        card_h = int(HEIGHT * 0.9)
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2

        pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (255, 255, 255), (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)

        # Logo + título
        logo_x = card_x + 30
        logo_y = card_y + 30
        screen.blit(logo, (logo_x, logo_y))

        title = font_title.render(title_text, True, (40, 45, 55))
        title_rect = title.get_rect(midleft=(logo_x + 54, logo_y + logo.get_height() // 2))
        screen.blit(title, title_rect)

        sub = font_sub.render(subtitle_text, True, (90, 95, 105))
        screen.blit(sub, (card_x + 30, card_y + 82))

        # Menu: sempre centralizado no card para não "mexer"
        mx, my = pygame.mouse.get_pos()

        item_h = 46
        item_gap = 10
        menu_block_h = len(options) * item_h + (len(options) - 1) * item_gap

        menu_top = card_y + (card_h // 2) - (menu_block_h // 2) + 20

        for i, (label, _) in enumerate(options):
            y = menu_top + i * (item_h + item_gap)
            rect = pygame.Rect(card_x + 30, y, card_w - 60, item_h)
            option_rects[i] = rect

            if rect.collidepoint(mx, my):
                selected = i

            is_sel = (i == selected)
            pulse = 2 + int(2 * (1 + math.sin(pygame.time.get_ticks() / 300)))
            color = (30, 90, 160) if is_sel else (70, 75, 85)

            text = font_item.render(label, True, color)
            text_rect = text.get_rect(midleft=(card_x + 70 + (pulse if is_sel else 0), rect.centery))

            if is_sel:
                pygame.draw.rect(screen, (220, 235, 250), rect, border_radius=10)
                icon = font_item.render(">", True, (30, 90, 160))
                icon_rect = icon.get_rect(midleft=(card_x + 45, rect.centery))
                screen.blit(icon, icon_rect)

            screen.blit(text, text_rect)

        hint = font_hint.render("↑↓ ou mouse • Enter confirmar • Esc voltar", True, (120, 125, 135))
        screen.blit(hint, (card_x + 40, card_y + card_h - 45))

        pygame.display.flip()
        clock.tick(60)
