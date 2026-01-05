import pygame
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from typing import List, Tuple, Optional


def draw_plot(surface: pygame.Surface,
              x: List,
              y: List,
              y_label: str = "Fitness",
              position: Tuple[int, int] = (0, 0),
              size_px: Tuple[int, int] = (300, 200),
              title: Optional[str] = None):
    """
    Desenha um gráfico em uma superfície pygame.
    """
    if not x or not y:
        return
    
    dpi = 100
    fig, ax = plt.subplots(
        figsize=(size_px[0] / dpi, size_px[1] / dpi),
        dpi=dpi,
        facecolor='#f0f0f0'
    )
    
    ax.set_facecolor('#f8f8f8')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    ax.plot(x, y, linewidth=2, color='#2c3e50')
    
    ax.set_ylabel(y_label, fontsize=9)
    ax.set_xlabel("Generation", fontsize=9)
    
    if title:
        ax.set_title(title, fontsize=10)
    
    ax.tick_params(axis='both', labelsize=8)
    
    plt.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    
    raw = canvas.get_renderer().tostring_argb()
    surf = pygame.image.fromstring(raw, canvas.get_width_height(), "RGBA")
    
    surf = pygame.transform.smoothscale(surf, size_px)
    
    surface.blit(surf, position)
    plt.close(fig)


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