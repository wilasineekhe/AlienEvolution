"""
screens.py
============================================================
Full-screen drawing functions for non-gameplay states:
  draw_menu()       — title / start screen
  draw_game_over()  — death screen
  draw_victory()    — escape success screen

IMAGE: MENU_BG — see draw_menu() and draw_game_over() below
IMAGE: LOGO    — see draw_menu() below
============================================================
"""

import pygame
import math
from src.constants import (
    SCREEN_W, SCREEN_H, STAGES,
    WHITE, GRAY, CYAN, GREEN_NEON, YELLOW, RED, ORANGE
)
from src.utils import draw_text_centered, draw_grid, format_time


# ──────────────────────────────────────────────────────────
# MENU SCREEN
# ──────────────────────────────────────────────────────────

def draw_menu(surface, fonts: dict, assets: dict, tick: int):
    """
    Render the animated main menu.

    IMAGE: MENU_BG
    -------------------------------------------------------
    Replace draw_grid(surface) with:
        img = assets.get("menu_bg")
        if img:
            surface.blit(img, (0, 0))
        else:
            draw_grid(surface)
    -------------------------------------------------------

    IMAGE: LOGO
    -------------------------------------------------------
    Replace the two draw_text_centered title lines with:
        logo = assets.get("logo")
        if logo:
            surface.blit(logo,
                         (SCREEN_W // 2 - logo.get_width() // 2, 60))
        else:
            draw_text_centered(...)   # keep existing fallback
    -------------------------------------------------------
    """
    draw_grid(surface)

    # Animated scanline overlay
    scan = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    for y in range(0, SCREEN_H, 4):
        a = 20 + int(10 * math.sin(y * 0.1 + tick * 0.02))
        pygame.draw.line(scan, (0, 255, 120, a), (0, y), (SCREEN_W, y))
    surface.blit(scan, (0, 0))

    # Title
    pulse = math.sin(tick * 0.05)
    title_col = (255, int(200 + pulse * 55), int(max(0, pulse * 100)))
    draw_text_centered(surface, "ALIEN ORGANISM", fonts["title"], title_col,    80)
    draw_text_centered(surface, "EVOLUTION",      fonts["title"], GREEN_NEON,  130)
    draw_text_centered(surface, "Laboratory Escape Experiment",
                       fonts["small"], GRAY, 185)

    # Separator
    pygame.draw.line(surface, GREEN_NEON, (160, 210), (SCREEN_W - 160, 210), 1)

    # Controls table
    controls = [
        ("MOVE",    "WASD  /  Arrow Keys"),
        ("COLLECT", "Walk over crystals"),
        ("SURVIVE", "Avoid green gas & red drones"),
        ("EVOLVE",  "Collect enough crystals"),
        ("ESCAPE",  "Touch portal in Final Form"),
    ]
    for i, (key, val) in enumerate(controls):
        ky = 225 + i * 34
        surface.blit(fonts["small"].render(key, True, CYAN),  (200, ky))
        surface.blit(fonts["small"].render(val, True, WHITE), (350, ky))

    # Blinking prompt
    if (tick // 35) % 2 == 0:
        draw_text_centered(surface, "► Press  ENTER  to Begin ◄",
                           fonts["medium"], YELLOW, 410)

    # Version watermark
    surface.blit(
        fonts["tiny"].render("v1.0  |  Python + Pygame", True, (50, 60, 70)),
        (10, SCREEN_H - 20)
    )


# ──────────────────────────────────────────────────────────
# GAME OVER SCREEN
# ──────────────────────────────────────────────────────────

def draw_game_over(surface, fonts: dict, assets: dict, player, elapsed: float):
    """
    Render the defeat / game-over screen.

    IMAGE: MENU_BG  (reuse menu art or a dedicated defeat image)
    -------------------------------------------------------
    Same swap as draw_menu — replace draw_grid() with an
    assets.get("menu_bg") blit.
    -------------------------------------------------------
    """
    draw_grid(surface)

    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((80, 0, 0, 100))
    surface.blit(overlay, (0, 0))

    draw_text_centered(surface, "ORGANISM TERMINATED", fonts["large"], RED, 90)
    draw_text_centered(surface, "─" * 34, fonts["small"], GRAY, 135)

    stage_name = STAGES[player.stage][0]
    rows = [
        ("Final Form",    stage_name,            player.glow_color),
        ("Score",         str(player.score),      WHITE),
        ("Time Survived", format_time(elapsed),   CYAN),
    ]
    for i, (lbl, val, col) in enumerate(rows):
        y = 160 + i * 50
        surface.blit(fonts["medium"].render(f"{lbl}:", True, GRAY),
                     (SCREEN_W // 2 - 160, y))
        surface.blit(fonts["medium"].render(val, True, col),
                     (SCREEN_W // 2 + 20, y))

    draw_text_centered(surface, "► Press  R  to Restart ◄",
                       fonts["medium"], YELLOW, 340)
    draw_text_centered(surface, "► Press  M  for Menu ◄",
                       fonts["small"],  GRAY,   380)


# ──────────────────────────────────────────────────────────
# VICTORY SCREEN
# ──────────────────────────────────────────────────────────

def draw_victory(surface, fonts: dict, assets: dict,
                 player, elapsed: float, tick: int):
    """
    Render the escape-success / victory screen.

    IMAGE: MENU_BG  (reuse or supply a dedicated victory image)
    """
    draw_grid(surface)

    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 60, 80, 100))
    surface.blit(overlay, (0, 0))

    pulse   = abs(math.sin(tick * 0.04))
    vc      = (int(200 * pulse), 255, int(200 * pulse))
    draw_text_centered(surface, "ESCAPE SUCCESSFUL!", fonts["large"],  vc,   80)
    draw_text_centered(surface, "Evolution Complete", fonts["medium"], CYAN, 130)
    draw_text_centered(surface, "─" * 34, fonts["small"], GRAY, 158)

    rows = [
        ("Final Form",   STAGES[player.stage][0],         YELLOW),
        ("Final Score",  str(player.score),                WHITE),
        ("Time",         format_time(elapsed),             CYAN),
        ("HP Remaining", f"{player.hp} / {player.max_hp}", GREEN_NEON),
    ]
    for i, (lbl, val, col) in enumerate(rows):
        y = 175 + i * 50
        surface.blit(fonts["medium"].render(f"{lbl}:", True, GRAY),
                     (SCREEN_W // 2 - 160, y))
        surface.blit(fonts["medium"].render(val, True, col),
                     (SCREEN_W // 2 + 20, y))

    if (tick // 35) % 2 == 0:
        draw_text_centered(surface, "► Press  R  to Play Again ◄",
                           fonts["medium"], YELLOW, 390)
    draw_text_centered(surface, "► Press  M  for Menu ◄",
                       fonts["small"], GRAY, 430)
