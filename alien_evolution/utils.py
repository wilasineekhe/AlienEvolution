"""
utils.py
========
Shared utility functions used by multiple modules.

Contains:
  - dist()              — Euclidean distance
  - draw_glow_circle()  — soft glowing circle
  - draw_text_centered()— centred text with shadow
  - format_time()       — seconds → MM:SS
  - draw_grid()         — background grid / lab floor
  - spawn_particles()   — burst of particles at a point
"""

import pygame
import math
import random

from settings import DARK_BG, GRID_COLOR, WHITE, SCREEN_W, SCREEN_H


# ─────────────────────────────────────────────
# MATH
# ─────────────────────────────────────────────

def dist(ax, ay, bx, by):
    """Return Euclidean distance between two points."""
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def format_time(seconds):
    """Convert a float seconds value into a MM:SS string."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


# ─────────────────────────────────────────────
# DRAWING HELPERS
# ─────────────────────────────────────────────

def draw_glow_circle(surface, color, pos, radius, layers=4):
    """
    Draw a multi-layer soft glow around a circle.
    color  — (R, G, B) tuple
    pos    — (x, y) centre
    radius — inner radius
    layers — how many glow rings (more = softer/wider glow)
    """
    glow_surf = pygame.Surface(
        (radius * 2 + layers * 8, radius * 2 + layers * 8),
        pygame.SRCALPHA
    )
    for i in range(layers, 0, -1):
        alpha = int(40 * (i / layers))
        r = min(255, color[0])
        g = min(255, color[1])
        b = min(255, color[2])
        pygame.draw.circle(
            glow_surf, (r, g, b, alpha),
            (radius + layers * 4, radius + layers * 4),
            radius + i * 4
        )
    cx = int(pos[0]) - radius - layers * 4
    cy = int(pos[1]) - radius - layers * 4
    surface.blit(glow_surf, (cx, cy))


def draw_text_centered(surface, text, font, color, y, shadow=True):
    """
    Render text horizontally centred on the screen.
    shadow=True draws a dark drop shadow 2px offset.
    """
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        surface.blit(shadow_surf,
                     (SCREEN_W // 2 - shadow_surf.get_width() // 2 + 2, y + 2))
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, (SCREEN_W // 2 - text_surf.get_width() // 2, y))


def draw_grid(surface, images=None):
    """
    Draw the laboratory background grid.

    IMAGE: BACKGROUND
    If images["background"] is loaded, it replaces the drawn grid entirely.
    Just pass the images dict from settings.load_images().

    Example:
        draw_grid(surface, images)
    """
    if images and images.get("background"):
        surface.blit(images["background"], (0, 0))
        return

    # Fallback: drawn grid
    surface.fill(DARK_BG)
    for x in range(0, SCREEN_W, 40):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_H), 1)
    for y in range(0, SCREEN_H, 40):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_W, y), 1)
    # Corner lab markers
    size = 20
    for cx, cy in [(0, 0), (SCREEN_W, 0), (0, SCREEN_H), (SCREEN_W, SCREEN_H)]:
        pygame.draw.rect(surface, (30, 80, 60),
                         (cx - size // 2, cy - size // 2, size, size), 2)


# ─────────────────────────────────────────────
# PARTICLE HELPERS
# ─────────────────────────────────────────────

def spawn_particles(particle_list, x, y, color, count=12):
    """Add `count` new Particle objects to particle_list at (x, y)."""
    from entities import Particle          # local import avoids circular dependency
    for _ in range(count):
        particle_list.append(Particle(x, y, color))


def play_sfx(sounds, key):
    """
    Safely play a sound from the sounds dict.
    Does nothing if the sound was not loaded (None).
    """
    sfx = sounds.get(key)
    if sfx:
        sfx.play()
