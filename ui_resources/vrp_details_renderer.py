# vrp_details_renderer.py
import pygame
from typing import List, Dict, Optional
from config import *
from route_helpers import get_city_priority_info

def _make_font(size: int, bold: bool = False) -> pygame.font.Font:
    # tenta achar fontes com emoji/símbolos no Windows
    for name in ["Segoe UI Emoji", "Segoe UI Symbol", "Segoe UI", "Arial Unicode MS", "Arial"]:
        path = pygame.font.match_font(name)
        if path:
            f = pygame.font.Font(path, size)
            f.set_bold(bold)
            return f

    f = pygame.font.SysFont("Arial", size)
    f.set_bold(bold)
    return f

def _fmt_ptbr(value: float, decimals: int = 2) -> str:
    s = format(value, f",.{decimals}f")  # 1,234.56
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def render_vrp_details_panel(
    screen: pygame.Surface,
    vrp_routes: List,
    coord_to_city: Dict,
    deliveries_by_city: Dict,
    depot_city: Optional[str] = None,
    iteration: int = 0,
    *,
    panel_rect: pygame.Rect,
    scroll_y: int = 0,
) -> int:
    """
    Renderiza o painel de detalhes VRP no estilo novo (título flutuante + card),
    dentro de panel_rect, com rolagem vertical.

    - O título fica "voando" fora do card (igual Status / Gráficos).
    - O conteúdo interno rola (scroll_y).
    - Retorna max_scroll para clamp no caller.
    """

    # Fonts (padrão novo)
    font_title = _make_font(15, bold=True)
    font_sub = _make_font(12)
    font_label = _make_font(12)
    font_value = _make_font(12, bold=True)
    font_route_title = _make_font(13, bold=True)
    font_small = _make_font(11)
    font_tiny = _make_font(10)

    # -----------------------------
    # Título flutuante (fora do card)
    # -----------------------------
    title_surf = font_title.render("Detalhes da Solução VRP", True, (20, 30, 30))
    screen.blit(title_surf, (panel_rect.x + 4, panel_rect.y + 2))

    TITLE_H = 24
    TOP_GAP = 6

    # -----------------------------
    # Card começa abaixo do título
    # -----------------------------
    card_rect = pygame.Rect(
        panel_rect.x,
        panel_rect.y + TITLE_H + TOP_GAP,
        panel_rect.width,
        panel_rect.height - (TITLE_H + TOP_GAP),
    )

    # Fundo do card (cinza)
    pygame.draw.rect(screen, GRAY, card_rect)
    pygame.draw.rect(screen, (200, 205, 210), card_rect, width=1)

    # Área branca interna
    INNER_PAD = 8
    content_rect = pygame.Rect(
        card_rect.x + INNER_PAD,
        card_rect.y + INNER_PAD,
        card_rect.width - 2 * INNER_PAD,
        card_rect.height - 2 * INNER_PAD,
    )
    pygame.draw.rect(screen, WHITE, content_rect)

    viewport = screen.subsurface(content_rect)
    vw, vh = viewport.get_width(), viewport.get_height()

    # -----------------------------
    # Agregados e validações
    # -----------------------------
    total_distance = sum(r.total_distance for r in vrp_routes) if vrp_routes else 0.0
    total_weight = sum(r.total_weight for r in vrp_routes) if vrp_routes else 0.0
    total_cost = sum(r.total_cost for r in vrp_routes) if vrp_routes else 0.0

    violations = 0
    for r in vrp_routes:
        w_lim = r.vehicle.max_weight
        d_lim = r.vehicle.max_distance * 0.85
        if r.total_weight > w_lim or r.total_distance > d_lim:
            violations += 1

    all_ok = (len(vrp_routes) > 0 and violations == 0)

    # -----------------------------
    # Calcular altura de conteúdo (para scroll)
    # -----------------------------
    y = 10
    top_block_h = 86 + (18 if depot_city else 0)
    y += top_block_h + 12

    # altura por rota (card)
    route_total_h = 0
    for r in vrp_routes:
        dep_extra = 2 if depot_city else 0
        cities_lines = len(r.route) + dep_extra
        cities_h = cities_lines * 16

        card_h = 92 + 22 + cities_h + 18
        route_total_h += card_h + 12

    content_h = max(vh, y + route_total_h + 20)

    content = pygame.Surface((vw, content_h), pygame.SRCALPHA)
    content.fill((0, 0, 0, 0))

    # -----------------------------
    # Desenhar conteúdo (em surface grande)
    # -----------------------------
    y = 10
    pad_x = 10

    # Iteração (acima das métricas)
    content.blit(font_sub.render(f"Iteração atual: {iteration}", True, (90, 95, 105)), (pad_x, y))
    y += 22

    # Linha 1: Rotas / Distância
    content.blit(font_label.render("Rotas:", True, (60, 65, 75)), (pad_x, y))
    content.blit(font_value.render(str(len(vrp_routes)), True, (20, 30, 30)), (pad_x + 55, y))

    content.blit(font_label.render("Distância:", True, (60, 65, 75)), (pad_x + 140, y))
    content.blit(
        font_value.render(f"{_fmt_ptbr(total_distance, 1)} km", True, (20, 30, 30)),
        (pad_x + 220, y),
    )
    y += 18

    # Linha 2: Peso / Custo
    content.blit(font_label.render("Peso:", True, (60, 65, 75)), (pad_x, y))
    content.blit(
        font_value.render(f"{_fmt_ptbr(total_weight, 1)} kg", True, (20, 30, 30)),
        (pad_x + 55, y),
    )

    content.blit(font_label.render("Custo:", True, (60, 65, 75)), (pad_x + 140, y))
    cost_color = GREEN if all_ok else (20, 30, 30)
    content.blit(
        font_value.render(f"R$ {_fmt_ptbr(total_cost, 2)}", True, cost_color),
        (pad_x + 220, y),
    )
    y += 18

    # Linha 3: badge geral
    if len(vrp_routes) == 0:
        badge_txt = "⚠ Nenhuma rota gerada"
        badge_col = (180, 0, 0)
    elif all_ok:
        badge_txt = "✔ Todas as rotas dentro dos limites"
        badge_col = (0, 120, 0)
    else:
        badge_txt = f"⚠ {violations} rota(s) excedem limites"
        badge_col = (180, 0, 0)

    content.blit(font_sub.render(badge_txt, True, badge_col), (pad_x, y))
    y += 22

    # Depósito
    if depot_city:
        content.blit(font_sub.render(f"Depósito: {depot_city}", True, (90, 95, 105)), (pad_x, y))
        y += 18

    # Separador leve
    pygame.draw.line(content, (220, 225, 230), (pad_x, y + 6), (vw - pad_x, y + 6), 1)
    y += 18

    # -----------------------------
    # Cards de rotas
    # -----------------------------
    priority_colors = {0: RED, 1: ORANGE, 2: GREEN}
    priority_labels = {0: "P0", 1: "P1", 2: "P2"}

    for idx_route, route in enumerate(vrp_routes):
        route_color = ROUTE_COLORS[idx_route % len(ROUTE_COLORS)]
        max_priority = getattr(route, "max_priority", 2)
        avg_priority = getattr(route, "avg_priority", 2.0)

        w_lim = route.vehicle.max_weight
        d_lim = route.vehicle.max_distance * 0.85
        w_ok = route.total_weight <= w_lim
        d_ok = route.total_distance <= d_lim
        route_ok = w_ok and d_ok

        # Dimensões do card
        dep_extra = 2 if depot_city else 0
        cities_lines = len(route.route) + dep_extra
        cities_h = cities_lines * 16
        card_h = 92 + 22 + cities_h + 18

        card_x = pad_x
        card_w = vw - 2 * pad_x
        card_rect = pygame.Rect(card_x, y, card_w, card_h)

        # Corpo do card
        pygame.draw.rect(content, WHITE, card_rect, border_radius=12)
        pygame.draw.rect(content, (200, 205, 210), card_rect, width=1, border_radius=12)

        # Marca da rota
        mark_rect = pygame.Rect(card_rect.x + 10, card_rect.y + 10, 14, 14)
        pygame.draw.rect(content, route_color, mark_rect, border_radius=3)
        pygame.draw.rect(content, BLACK, mark_rect, width=1, border_radius=3)

        # Bola prioridade
        pr_label = priority_labels.get(max_priority, "P?")
        pr_color = priority_colors.get(max_priority, (150, 150, 150))
        pygame.draw.circle(content, pr_color, (card_rect.x + card_w - 22, card_rect.y + 18), 7)
        pygame.draw.circle(content, (40, 45, 55), (card_rect.x + card_w - 22, card_rect.y + 18), 7, 1)

        # Título
        title_x = card_rect.x + 32
        t1 = f"Rota #{idx_route + 1} — {route.vehicle.name} (ID: {route.vehicle.vehicle_id})"
        content.blit(font_route_title.render(t1, True, (20, 30, 30)), (title_x, card_rect.y + 8))

        # Sub-linha: prioridade + status
        status_txt = "✔ Dentro dos limites" if route_ok else "⚠ Viola limites"
        status_col = (0, 120, 0) if route_ok else (180, 0, 0)

        content.blit(font_small.render(f"Prioridade: {pr_label}", True, (60, 65, 75)), (title_x, card_rect.y + 30))
        content.blit(font_small.render(status_txt, True, status_col), (title_x + 160, card_rect.y + 30))

        # Métricas
        my = card_rect.y + 50
        content.blit(
            font_small.render(
                f"Distância: {_fmt_ptbr(route.total_distance, 0)} km / {_fmt_ptbr(route.vehicle.max_distance, 0)} km",
                True,
                (60, 65, 75),
            ),
            (title_x, my),
        )
        my += 16

        content.blit(
            font_small.render(
                f"Peso: {_fmt_ptbr(route.total_weight, 0)} kg / {_fmt_ptbr(route.vehicle.max_weight, 0)} kg",
                True,
                (60, 65, 75),
            ),
            (title_x, my),
        )
        my += 16

        cost_line = f"Custo: R$ {_fmt_ptbr(route.total_cost, 2)}   |   Prior média: {_fmt_ptbr(avg_priority, 1)}"
        content.blit(font_small.render(cost_line, True, (60, 65, 75)), (title_x, my))
        my += 18

        # Avisos específicos
        warn_parts = []
        if not w_ok:
            warn_parts.append("PESO")
        if not d_ok:
            warn_parts.append("DISTÂNCIA")
        if warn_parts:
            content.blit(font_small.render("⚠ " + " + ".join(warn_parts), True, (180, 0, 0)), (title_x, my))
            my += 18
        else:
            my += 6

        # Entregas
        content.blit(font_label.render("Entregas (ordem do trajeto)", True, (20, 30, 30)), (title_x, my))
        my += 18

        def draw_city_line(seq: str, city_name: str, col: tuple, suffix: str = ""):
            nonlocal my
            pygame.draw.circle(content, col, (title_x + 6, my + 7), 4)
            pygame.draw.circle(content, (40, 45, 55), (title_x + 6, my + 7), 4, 1)
            content.blit(font_tiny.render(f"{seq}. {city_name}{suffix}", True, (40, 45, 55)), (title_x + 18, my))
            my += 16

        # DEP
        if depot_city:
            draw_city_line("0", f"{depot_city} (DEP)", (0, 100, 200))

        # Cidades
        for idx_city, coord in enumerate(route.route):
            full_city = coord_to_city.get(coord, "?")

            pr_text, _, pr_col = get_city_priority_info(full_city, deliveries_by_city)

            deliveries_info = ""
            if full_city in deliveries_by_city:
                n_del = len(deliveries_by_city[full_city])
                w_city = sum(d.total_weight for d in deliveries_by_city[full_city])
                deliveries_info = f"  {n_del}x · {_fmt_ptbr(w_city, 0)} kg"

            suffix = f" [{pr_text.split()[0]}]{deliveries_info}"
            draw_city_line(str(idx_city + 1), full_city, pr_col, suffix=suffix)

        # RET
        if depot_city:
            draw_city_line(str(len(route.route) + 1), f"{depot_city} (RET)", (0, 100, 200))

        y += card_h + 12

    # -----------------------------
    # Aplicar scroll no viewport
    # -----------------------------
    max_scroll = max(0, content_h - vh)
    scroll_y = max(0, min(scroll_y, max_scroll))

    # limpa viewport e desenha conteúdo deslocado
    viewport.fill(WHITE)
    viewport.blit(content, (0, -scroll_y))

    # -----------------------------------------
    # Scrollbar (discreta) para indicar rolagem
    # -----------------------------------------
    if max_scroll > 0:
        track_w = 6
        track_margin = 4
        track_rect = pygame.Rect(
            vw - track_w - track_margin,
            track_margin,
            track_w,
            vh - 2 * track_margin
        )

        # trilho bem suave
        pygame.draw.rect(viewport, (235, 240, 246), track_rect, border_radius=6)

        # thumb proporcional ao conteúdo visível
        visible_ratio = vh / float(content_h)
        thumb_h = max(26, int(track_rect.height * visible_ratio))

        # posição do thumb baseada no scroll
        scroll_ratio = scroll_y / float(max_scroll)
        thumb_y = track_rect.y + int((track_rect.height - thumb_h) * scroll_ratio)

        thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_h)

        # thumb um pouco mais “presente” mas ainda clean
        pygame.draw.rect(viewport, (200, 205, 210), thumb_rect, border_radius=6)

        # se quiser, um destaque quando estiver “no meio do scroll”
        # (fica bonito e sutil)
        pygame.draw.rect(viewport, (180, 185, 195), thumb_rect, width=1, border_radius=6)

    # -----------------------------------------
    # Fades topo/rodapé (indicam conteúdo fora)
    # -----------------------------------------
    if max_scroll > 0:
        fade_h = 18

        # fade topo (só aparece se não estiver no topo)
        if scroll_y > 0:
            fade = pygame.Surface((vw, fade_h), pygame.SRCALPHA)
            for i in range(fade_h):
                a = int(110 * (1 - i / fade_h))
                pygame.draw.line(fade, (255, 255, 255, a), (0, i), (vw, i))
            viewport.blit(fade, (0, 0))

        # fade rodapé (só aparece se não estiver no fim)
        if scroll_y < max_scroll:
            fade = pygame.Surface((vw, fade_h), pygame.SRCALPHA)
            for i in range(fade_h):
                a = int(110 * (i / fade_h))
                pygame.draw.line(fade, (255, 255, 255, a), (0, i), (vw, i))
            viewport.blit(fade, (0, vh - fade_h))



    return max_scroll
