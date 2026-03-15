"""
screens.py
==========
All full-screen state drawings:
  - draw_menu()       — main menu / title screen
  - draw_game_over()  — death screen
  - draw_victory()    — win screen
"""

import pygame
import math

from settings import (
    SCREEN_W, SCREEN_H, STAGES,
    WHITE, CYAN, GRAY, GREEN_NEON, YELLOW, RED, ORANGE
)
from utils import draw_text_centered, draw_grid, format_time


def draw_menu(surface, tick, fonts, images=None):
    """
    Draw the main menu / title screen.

    IMAGE: MENU_BG
    If images["menu_bg"] is loaded it will replace the drawn grid.
    draw_grid() checks for this automatically when you pass images.

    IMAGE: LOGO
    If images["logo"] is loaded it replaces the text title block:
        if images and images.get("logo"):
            logo = images["logo"]
            surface.blit(logo, (SCREEN_W//2 - logo.get_width()//2, 60))
        else:
            # draw text title ...
    """
    draw_grid(surface, images)

    # Scanline overlay (animated)
    scanline = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    for y in range(0, SCREEN_H, 4):
        alpha = 20 + int(10 * math.sin(y * 0.1 + tick * 0.02))
        pygame.draw.line(scanline, (0, 255, 120, alpha), (0, y), (SCREEN_W, y))
    surface.blit(scanline, (0, 0))

    # ── Title ─────────────────────────────────────────────────────
    # IMAGE: LOGO — replace the two draw_text_centered calls below
    pulse = math.sin(tick * 0.05)
    title_col = (255, int(200 + pulse * 55), int(pulse * 100))
    draw_text_centered(surface, "ALIEN ORGANISM", fonts["title"], title_col,     80)
    draw_text_centered(surface, "EVOLUTION",       fonts["title"], GREEN_NEON,  130)
    draw_text_centered(surface, "Laboratory Escape Experiment",
                       fonts["small"], GRAY, 185)

    # Separator line
    pygame.draw.line(surface, GREEN_NEON, (160, 210), (SCREEN_W - 160, 210), 1)

    # ── Controls table ────────────────────────────────────────────
    controls = [
        ("MOVE",    "WASD  /  Arrow Keys"),
        ("COLLECT", "Walk over crystals"),
        ("SURVIVE", "Avoid green gas & red drones"),
        ("EVOLVE",  "Collect enough crystals"),
        ("ESCAPE",  "Touch portal in Final Form"),
    ]
    for i, (key, val) in enumerate(controls):
        y = 225 + i * 34
        surface.blit(fonts["small"].render(key, True, CYAN),  (200, y))
        surface.blit(fonts["small"].render(val, True, WHITE), (350, y))

    # Blinking start prompt
    if (tick // 35) % 2 == 0:
        draw_text_centered(surface, "► Press  ENTER  to Begin ◄",
                           fonts["medium"], YELLOW, 410)

    # Version tag
    surface.blit(
        fonts["tiny"].render("v1.0  |  Python + Pygame", True, (50, 60, 70)),
        (10, SCREEN_H - 20)
    )


def draw_game_over(surface, player, elapsed, fonts, images=None):
    """
    Draw the game-over / death screen.

    IMAGE: MENU_BG — reuse the same background or a separate death image.
    """
    draw_grid(surface, images)

    # Red overlay tint
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((80, 0, 0, 100))
    surface.blit(overlay, (0, 0))

    draw_text_centered(surface, "ORGANISM TERMINATED", fonts["large"], RED, 90)
    draw_text_centered(surface, "─" * 34, fonts["small"], GRAY, 135)

    stage_name = STAGES[player.stage][0]
    rows = [
        ("Final Form",    stage_name,              player.glow_color),
        ("Score",         str(player.score),        WHITE),
        ("Time Survived", format_time(elapsed),     CYAN),
    ]
    for i, (label, value, col) in enumerate(rows):
        y = 160 + i * 50
        surface.blit(fonts["medium"].render(f"{label}:", True, GRAY),
                     (SCREEN_W // 2 - 160, y))
        surface.blit(fonts["medium"].render(value, True, col),
                     (SCREEN_W // 2 + 20, y))

    draw_text_centered(surface, "► Press  R  to Restart ◄",
                       fonts["medium"], YELLOW, 340)
    draw_text_centered(surface, "► Press  M  for Menu ◄",
                       fonts["small"], GRAY, 380)


def draw_victory(surface, player, elapsed, tick, fonts, images=None):
    """
    Draw the victory / escape screen.

    IMAGE: MENU_BG — reuse or use a separate victory art image.
    """
    draw_grid(surface, images)

    # Cyan tint
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 60, 80, 100))
    surface.blit(overlay, (0, 0))

    pulse   = abs(math.sin(tick * 0.04))
    win_col = (int(200 * pulse), 255, int(200 * pulse))
    draw_text_centered(surface, "ESCAPE SUCCESSFUL!", fonts["large"], win_col, 80)
    draw_text_centered(surface, "Evolution Complete",  fonts["medium"], CYAN,  130)
    draw_text_centered(surface, "─" * 34, fonts["small"], GRAY, 158)

    rows = [
        ("Final Form",   STAGES[player.stage][0],         YELLOW),
        ("Final Score",  str(player.score),                WHITE),
        ("Time",         format_time(elapsed),             CYAN),
        ("HP Remaining", f"{player.hp} / {player.max_hp}", GREEN_NEON),
    ]
    for i, (label, value, col) in enumerate(rows):
        y = 175 + i * 50
        surface.blit(fonts["medium"].render(f"{label}:", True, GRAY),
                     (SCREEN_W // 2 - 160, y))
        surface.blit(fonts["medium"].render(value, True, col),
                     (SCREEN_W // 2 + 20, y))

    if (tick // 35) % 2 == 0:
        draw_text_centered(surface, "► Press  R  to Play Again ◄",
                           fonts["medium"], YELLOW, 390)
    draw_text_centered(surface, "► Press  M  for Menu ◄",
                       fonts["small"], GRAY, 430)
