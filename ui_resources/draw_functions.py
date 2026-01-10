import locale
import pygame
import pygame.freetype
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from typing import List, Tuple, Optional

try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except:
    pass

def format_ptbr(value: float) -> str:
    """
    Formata número no padrão pt-BR com decimais.
    """
    if abs(value) >= 1000:
        txt = f"{value:,.1f}"   # 1 casa decimal
    else:
        txt = f"{value:,.2f}"   # 2 casas decimaisi

    return txt.replace(",", "X").replace(".", ",").replace("X", ".")

def _compute_scale(y_values):
    min_y = min(y_values)
    max_y = max(y_values)
    if min_y == max_y:
        max_y += 1
    return min_y, max_y


def _draw_grid_and_y_axis(surface, axis_font, min_y, max_y, plot_h, left_pad, top_pad, plot_w):
    for i in range(5):
        y = top_pad + int(i * plot_h / 4)

        pygame.draw.line(
            surface,
            (220, 220, 220),
            (left_pad, y),
            (left_pad + plot_w, y),
            1
        )

        value = max_y - (i * (max_y - min_y) / 4)
        axis_font.render_to(
            surface,
            (10, y - 8),
            format_ptbr(value),
            (90, 90, 90)
        )


def _compute_points(y_values, min_y, max_y, plot_w, plot_h, left_pad, top_pad):
    points = []
    total = len(y_values) - 1

    for i, val in enumerate(y_values):
        x = left_pad + int(i * plot_w / total)
        y = top_pad + int((max_y - val) / (max_y - min_y) * plot_h)
        points.append((x, y))

    return points

def _draw_title(surface, font, text, width):
    title = font.render(text, True, (20, 30, 30))
    title_rect = title.get_rect(midtop=(width // 2, 6))
    surface.blit(title, title_rect)

def draw_plot(surface,x_values,y_values,label,pos,size_px,line_color=(30, 90, 160)):
    width, height = size_px
    surface.fill((255, 255, 255))

    font_title = pygame.font.SysFont("Segoe UI", 13, bold=True)
    axis_font = pygame.freetype.SysFont("Segoe UI", 11)
    axis_font.antialiased = True

    left_pad, right_pad = 65, 15
    top_pad, bottom_pad = 30, 25

    plot_w = width - left_pad - right_pad
    plot_h = height - top_pad - bottom_pad

    if len(y_values) < 2:
        return

    min_y, max_y = _compute_scale(y_values)

    _draw_grid_and_y_axis(surface,axis_font,min_y,max_y,plot_h,left_pad,top_pad,plot_w)
    points = _compute_points(y_values,min_y,max_y,plot_w,plot_h,left_pad,top_pad)

    pygame.draw.lines(surface, line_color, False, points, 2)
    _draw_title(surface, font_title, label, width)

def draw_paths(screen: pygame.Surface,
               path: List[Tuple[int, int]],
               color: Tuple[int, int, int],
               width: int = 2,
               show_direction: bool = False,
               show_distance: bool = False,
               font: Optional[pygame.font.Font] = None):
    """
    Desenha caminhos conectando cidades.
    """
    if len(path) < 2:
        return
    
    for i in range(len(path)):
        start = path[i]
        end = path[(i + 1) % len(path)]
        
        pygame.draw.line(screen, color, start, end, width)
        
        if show_direction and width > 1:
            draw_arrow(screen, start, end, color, width * 2)
        
        if show_distance and font and i == 0:
            mid_x = (start[0] + end[0]) // 2
            mid_y = (start[1] + end[1]) // 2
            
            distance = ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5
            text = font.render(f"{distance:.0f}px", True, (0, 0, 0))
            text_rect = text.get_rect(center=(mid_x, mid_y - 15))
            
            bg_rect = text_rect.inflate(6, 4)
            s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            s.fill((255, 255, 255, 180))
            screen.blit(s, bg_rect)
            
            screen.blit(text, text_rect)


def draw_arrow(screen: pygame.Surface,
               start: Tuple[int, int],
               end: Tuple[int, int],
               color: Tuple[int, int, int],
               size: int = 10):
    """
    Desenha uma seta entre dois pontos.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    
    length = max(0.1, (dx ** 2 + dy ** 2) ** 0.5)
    dx, dy = dx / length, dy / length
    
    adjusted_end = (
        int(end[0] - dx * size / 2),
        int(end[1] - dy * size / 2)
    )
    
    perp_x = -dy
    perp_y = dx
    
    wing1 = (
        int(adjusted_end[0] - dx * size + perp_x * size * 0.4),
        int(adjusted_end[1] - dy * size + perp_y * size * 0.4)
    )
    
    wing2 = (
        int(adjusted_end[0] - dx * size - perp_x * size * 0.4),
        int(adjusted_end[1] - dy * size - perp_y * size * 0.4)
    )
    
    pygame.draw.polygon(screen, color, [adjusted_end, wing1, wing2])