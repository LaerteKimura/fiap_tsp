import os
import math
import pygame
from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN,
    K_ESCAPE, K_RETURN, K_KP_ENTER, K_SPACE,
    K_UP, K_DOWN, K_PAGEUP, K_PAGEDOWN
)

def show_vrp_depot_selection(cities):
    pygame.init()

    WIDTH, HEIGHT = 980, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sistema de Rotas - Depósito (VRP)")

    font_title = pygame.font.SysFont("Segoe UI", 34, bold=True)
    font_sub = pygame.font.SysFont("Segoe UI", 16)
    font_chip = pygame.font.SysFont("Segoe UI", 16, bold=True)    

    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "..", "assets", "location_pin.png")
    logo = None
    try:
        logo = pygame.image.load(logo_path).convert_alpha()
        logo = pygame.transform.smoothscale(logo, (36, 36))
    except Exception:
        logo = None

    clock = pygame.time.Clock()

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def ellipsize(text: str, max_px: int, font: pygame.font.Font) -> str:
        if font.size(text)[0] <= max_px:
            return text
        if max_px <= font.size("…")[0]:
            return "…"
        s = text
        while s and font.size(s + "…")[0] > max_px:
            s = s[:-1]
        return s + "…"

    def draw_chip(rect, label, selected, hover):
        bg = (220, 235, 250) if selected else (245, 247, 250)
        if hover and not selected:
            bg = (235, 240, 246)

        border = (30, 90, 160) if selected else (200, 205, 210)
        text_color = (30, 90, 160) if selected else (70, 75, 85)

        pygame.draw.rect(screen, bg, rect, border_radius=12)
        pygame.draw.rect(screen, border, rect, width=1, border_radius=12)

        txt = font_chip.render(label, True, text_color)
        screen.blit(txt, txt.get_rect(center=rect.center))

    def draw_btn(rect, label, primary=False):
        mx, my = pygame.mouse.get_pos()
        hover = rect.collidepoint(mx, my)

        if primary:
            bg = (220, 235, 250) if hover else (245, 247, 250)
            border = (30, 90, 160)
            text_c = (30, 90, 160)
            pulse = 2 + int(2 * (1 + math.sin(pygame.time.get_ticks() / 320))) if hover else 0
        else:
            bg = (235, 240, 246) if hover else (245, 247, 250)
            border = (200, 205, 210)
            text_c = (70, 75, 85)
            pulse = 0

        pygame.draw.rect(screen, bg, rect, border_radius=12)
        pygame.draw.rect(screen, border, rect, width=1, border_radius=12)

        txt = font_chip.render(label, True, text_c)
        screen.blit(txt, txt.get_rect(center=(rect.centerx + pulse, rect.centery)))

    # ---------- dados ----------
    cities_sorted = sorted(list(cities))
    items = [("Sem Depósito Central", None)] + [(c, c) for c in cities_sorted]

    selected = 0
    scroll = 0

    # ---------- layout (card) ----------
    card_w = int(WIDTH * 0.94)
    card_h = int(HEIGHT * 0.92)
    card_x = (WIDTH - card_w) // 2
    card_y = (HEIGHT - card_h) // 2

    logo_x = card_x + 30
    logo_y = card_y + 28

    content_top = card_y + 120

    # grid
    grid_x = card_x + 30
    grid_y = content_top
    grid_w = card_w - 60

    # rodapé: botões + hint (área fixa)
    buttons_y = card_y + card_h - 72
    hint_y = buttons_y + 50  # começa abaixo dos botões
    footer_top = buttons_y - 12
    footer_h = (card_y + card_h) - footer_top

    grid_h = (footer_top - 16) - grid_y  # deixa uma margem antes do footer

    cols = 2
    gap_x = 14
    gap_y = 12
    chip_h = 44
    col_w = (grid_w - gap_x) // cols

    rows_visible = max(1, (grid_h + gap_y) // (chip_h + gap_y))
    per_page = rows_visible * cols

    back_rect = pygame.Rect(card_x + 30, buttons_y, 170, 46)
    continue_rect = pygame.Rect(card_x + card_w - 30 - 190, buttons_y, 190, 46)

    def max_scroll():
        return max(0, len(items) - per_page)

    def ensure_selected_visible():
        nonlocal scroll
        if selected < scroll:
            scroll = selected
        elif selected >= scroll + per_page:
            scroll = selected - per_page + 1
        scroll = clamp(scroll, 0, max_scroll())

    ensure_selected_visible()

    # ---------- loop ----------
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "back"

                if event.key in (K_RETURN, K_KP_ENTER, K_SPACE):
                    if 0 <= selected < len(items):
                        return items[selected][1]

                if event.key == K_UP:
                    selected = clamp(selected - cols, 0, len(items) - 1)
                    ensure_selected_visible()

                if event.key == K_DOWN:
                    selected = clamp(selected + cols, 0, len(items) - 1)
                    ensure_selected_visible()

                if event.key == K_PAGEUP:
                    selected = clamp(selected - per_page, 0, len(items) - 1)
                    ensure_selected_visible()

                if event.key == K_PAGEDOWN:
                    selected = clamp(selected + per_page, 0, len(items) - 1)
                    ensure_selected_visible()

            if event.type == MOUSEBUTTONDOWN:
                mx, my = event.pos

                if event.button == 1:
                    if back_rect.collidepoint(mx, my):
                        return "back"
                    if continue_rect.collidepoint(mx, my):
                        if 0 <= selected < len(items):
                            return items[selected][1]

                    # clique nos chips visíveis
                    start = scroll
                    end = min(len(items), scroll + per_page)

                    local = 0
                    for idx in range(start, end):
                        r = local // cols
                        c = local % cols
                        x = grid_x + c * (col_w + gap_x)
                        y = grid_y + r * (chip_h + gap_y)
                        rect = pygame.Rect(x, y, col_w, chip_h)

                        if rect.collidepoint(mx, my):
                            selected = idx
                            ensure_selected_visible()
                            return items[selected][1]
                        local += 1

                # scroll wheel
                if event.button == 4:
                    scroll = clamp(scroll - cols, 0, max_scroll())
                elif event.button == 5:
                    scroll = clamp(scroll + cols, 0, max_scroll())

        # ---------- draw ----------
        screen.fill((245, 247, 250))

        pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (255, 255, 255), (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)

        # header
        if logo:
            screen.blit(logo, (logo_x, logo_y))
            title = font_title.render("Depósito Central (VRP)", True, (40, 45, 55))
            title_rect = title.get_rect(midleft=(logo_x + 54, logo_y + logo.get_height() // 2))
            screen.blit(title, title_rect)
        else:
            title = font_title.render("Depósito Central (VRP)", True, (40, 45, 55))
            screen.blit(title, (card_x + 30, logo_y))

        sub = font_sub.render("Selecione uma cidade como depósito, ou opere sem depósito.", True, (90, 95, 105))
        screen.blit(sub, (card_x + 30, card_y + 74))

        # itens
        mx, my = pygame.mouse.get_pos()
        start = scroll
        end = min(len(items), scroll + per_page)

        local = 0
        for idx in range(start, end):
            r = local // cols
            c = local % cols

            x = grid_x + c * (col_w + gap_x)
            y = grid_y + r * (chip_h + gap_y)
            rect = pygame.Rect(x, y, col_w, chip_h)

            label = ellipsize(str(items[idx][0]), col_w - 24, font_chip)
            draw_chip(rect, label, idx == selected, rect.collidepoint(mx, my))

            local += 1

        # scrollbar
        if len(items) > per_page:
            track_h = rows_visible * (chip_h + gap_y) - gap_y
            track_rect = pygame.Rect(card_x + card_w - 22, grid_y, 6, track_h)
            pygame.draw.rect(screen, (230, 232, 236), track_rect, border_radius=4)

            ratio = per_page / len(items)
            thumb_h = max(24, int(track_h * ratio))
            max_s = max_scroll() or 1
            thumb_y = grid_y + int((track_h - thumb_h) * (scroll / max_s))
            thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.w, thumb_h)
            pygame.draw.rect(screen, (180, 185, 195), thumb_rect, border_radius=4)

        # botões
        draw_btn(back_rect, "< Voltar", primary=False)
        draw_btn(continue_rect, "Continuar >", primary=True)
       
        pygame.display.flip()
        clock.tick(60)
