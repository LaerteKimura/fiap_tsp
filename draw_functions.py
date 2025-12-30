import pygame
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from typing import List, Tuple
import pygame
from typing import List, Tuple


def draw_plot(
    surface,
    x,
    y,
    y_label="Fitness",
    position=(0, 0),
    size_px=(300, 200)
):
    dpi = 100
    fig, ax = plt.subplots(
        figsize=(size_px[0] / dpi, size_px[1] / dpi),
        dpi=dpi
    )

    ax.plot(x, y)
    ax.set_ylabel(y_label)
    ax.set_xlabel("Generation")
    plt.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()

    raw = canvas.get_renderer().tostring_argb()
    surf = pygame.image.fromstring(raw, size_px, "RGBA")

    surface.blit(surf, position)
    plt.close(fig)



def draw_cities(
    screen: pygame.Surface,
    cities_locations: List[Tuple[int, int]],
    city_names: List[str],
    color: Tuple[int, int, int],
    radius: int,
    font: pygame.font.Font,
    label_offset=(10, -10)
):
    """
    Draw cities as circles with their names.
    """

    for (x, y), name in zip(cities_locations, city_names):
        # city point
        pygame.draw.circle(screen, color, (x, y), radius)

        # city label
        label = font.render(name, True, (0, 0, 0))
        screen.blit(
            label,
            (x + label_offset[0], y + label_offset[1])
        )



def draw_paths(
    screen: pygame.Surface,
    path: List[Tuple[int, int]],
    color: Tuple[int, int, int],
    width: int = 2
):
    if len(path) > 1:
        pygame.draw.lines(screen, color, True, path, width)
