"""
hud.py
======
All in-game HUD drawing: score, HP bar, evolution bar,
stage name, timer, and objective text.

Call:
    draw_hud(surface, player, elapsed_seconds, fonts)
"""

import pygame
import math

from settings import (
    SCREEN_W, SCREEN_H, STAGES,
    WHITE, CYAN, GRAY, GREEN_NEON, ORANGE, RED, YELLOW
)
from utils import format_time


def draw_hud(surface, player, elapsed_seconds, fonts):
    """
    Render the full heads-up display.

    Parameters
    ----------
    surface         : pygame.Surface — the main screen
    player          : Player         — the current player object
    elapsed_seconds : float          — time since game started
    fonts           : dict           — loaded font dict from settings.load_fonts()
    """
    pad = 10

    # ── Top-left info panel ───────────────────────────────────────
    panel = pygame.Surface((260, 110), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 160))
    surface.blit(panel, (pad, pad))
    pygame.draw.rect(surface, player.glow_color,
                     (pad, pad, 260, 110), 1, border_radius=4)

    stage_name = STAGES[player.stage][0]
    surface.blit(
        fonts["small"].render(f"◈ {stage_name}", True, player.glow_color),
        (pad + 8, pad + 6)
    )
    surface.blit(
        fonts["medium"].render(f"Score : {player.score}", True, WHITE),
        (pad + 8, pad + 28)
    )
    surface.blit(
        fonts["small"].render(f"Time  : {format_time(elapsed_seconds)}", True, GRAY),
        (pad + 8, pad + 55)
    )

    # HP bar
    surface.blit(fonts["small"].render("HP:", True, WHITE), (pad + 8, pad + 78))
    bar_x, bar_y, bar_w, bar_h = pad + 40, pad + 80, 140, 14
    pygame.draw.rect(surface, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    filled = int(bar_w * player.hp / player.max_hp)
    hp_col = GREEN_NEON if player.hp > 2 else (ORANGE if player.hp == 2 else RED)
    if filled > 0:
        pygame.draw.rect(surface, hp_col, (bar_x, bar_y, filled, bar_h), border_radius=3)
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
    surface.blit(
        fonts["tiny"].render(f"{player.hp}/{player.max_hp}", True, WHITE),
        (bar_x + bar_w + 4, bar_y)
    )

    # ── Evolution progress bar ────────────────────────────────────
    if player.stage < len(STAGES) - 1:
        next_thresh = STAGES[player.stage + 1][1]
        prev_thresh = STAGES[player.stage][1]
        span        = next_thresh - prev_thresh
        prog        = player.score - prev_thresh
        ratio       = max(0.0, min(1.0, prog / span)) if span > 0 else 1.0

        evo_panel = pygame.Surface((260, 30), pygame.SRCALPHA)
        evo_panel.fill((0, 0, 0, 140))
        surface.blit(evo_panel, (pad, pad + 115))

        surface.blit(
            fonts["tiny"].render("EVOLUTION", True, GRAY),
            (pad + 8, pad + 119)
        )

        ev_x, ev_y, ev_w, ev_h = pad + 90, pad + 120, 160, 12
        pygame.draw.rect(surface, (30, 30, 60), (ev_x, ev_y, ev_w, ev_h), border_radius=3)
        if ratio > 0:
            pygame.draw.rect(surface, player.glow_color,
                             (ev_x, ev_y, int(ev_w * ratio), ev_h), border_radius=3)
        pygame.draw.rect(surface, player.glow_color,
                         (ev_x, ev_y, ev_w, ev_h), 1, border_radius=3)

        needed = next_thresh - player.score
        surface.blit(
            fonts["tiny"].render(f"{needed} pts to evolve", True, player.glow_color),
            (ev_x + ev_w + 4, ev_y)
        )
    else:
        # Final stage badge
        badge_panel = pygame.Surface((260, 26), pygame.SRCALPHA)
        badge_panel.fill((0, 0, 0, 140))
        surface.blit(badge_panel, (pad, pad + 115))
        surface.blit(
            fonts["small"].render("⭐ FINAL FORM", True, YELLOW),
            (pad + 8, pad + 118)
        )

    # ── Objective text (bottom centre) ───────────────────────────
    objectives = {
        0: "Collect crystals → Evolve",
        1: "Keep evolving → Reach Mutant form",
        2: "Reach Ultimate Alien form",
        3: "Reach the ESCAPE PORTAL  ►",
    }
    obj_text = objectives.get(player.stage, "")
    obj_surf = fonts["small"].render(f"Objective: {obj_text}", True, CYAN)
    ox = SCREEN_W // 2 - obj_surf.get_width() // 2
    oy = SCREEN_H - 28
    bg = pygame.Surface((obj_surf.get_width() + 16, obj_surf.get_height() + 6), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 130))
    surface.blit(bg, (ox - 8, oy - 3))
    surface.blit(obj_surf, (ox, oy))
