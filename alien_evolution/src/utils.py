"""
utils.py
============================================================
Shared utility / drawing helper functions.
These are imported by multiple modules so they live here
to avoid circular imports.
============================================================
"""

import pygame
import math
from src.constants import SCREEN_W, SCREEN_H, DARK_BG, GRID_COLOR


# ──────────────────────────────────────────────────────────
# MATH HELPERS
# ──────────────────────────────────────────────────────────

def dist(ax, ay, bx, by):
    """Euclidean distance between two points."""
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def format_time(seconds):
    """Convert raw seconds → 'MM:SS' string."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


# ──────────────────────────────────────────────────────────
# DRAWING HELPERS
# ──────────────────────────────────────────────────────────

def draw_glow_circle(surface, color, pos, radius, layers=4):
    """
    Draw a soft glowing halo around a circle using alpha layers.
    color  — (R, G, B) base colour of the glow
    pos    — (x, y) centre
    radius — inner radius
    layers — how many alpha rings to draw (more = softer glow)
    """
    size = radius * 2 + layers * 8
    glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for i in range(layers, 0, -1):
        alpha = int(40 * (i / layers))
        r = min(255, color[0])
        g = min(255, color[1])
        b = min(255, color[2])
        pygame.draw.circle(glow_surf, (r, g, b, alpha), (cx, cy), radius + i * 4)
    surface.blit(glow_surf, (int(pos[0]) - cx, int(pos[1]) - cy))


def draw_text_centered(surface, text, font, color, y, shadow=True):
    """
    Render text horizontally centred on the screen.
    shadow — draw a black drop-shadow 2 px offset
    """
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surface.blit(s, (SCREEN_W // 2 - s.get_width() // 2 + 2, y + 2))
    rendered = font.render(text, True, color)
    surface.blit(rendered, (SCREEN_W // 2 - rendered.get_width() // 2, y))


def draw_grid(surface):
    """
    Draw the sci-fi laboratory background grid.

    IMAGE: BACKGROUND
    To use a real image instead of a drawn grid, replace
    this entire function body with:

        surface.blit(bg_image, (0, 0))

    where bg_image is loaded in assets.py and passed in,
    or stored as a module-level variable.
    """
    surface.fill(DARK_BG)
    for x in range(0, SCREEN_W, 40):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_H), 1)
    for y in range(0, SCREEN_H, 40):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_W, y), 1)
    # Corner lab-frame markers
    marker_size = 20
    for cx, cy in [(0, 0), (SCREEN_W, 0), (0, SCREEN_H), (SCREEN_W, SCREEN_H)]:
        pygame.draw.rect(surface, (30, 80, 60),
                         (cx - marker_size // 2, cy - marker_size // 2,
                          marker_size, marker_size), 2)
