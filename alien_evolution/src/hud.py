"""
hud.py — แสดง Score, HP, Armor, Evolution, Crystal Counter (stage 4), orb indicators
"""

import pygame
import math
from src.constants import (
    SCREEN_W, SCREEN_H, STAGES, PORTAL_CRYSTAL_GOAL,
    WHITE, GRAY, CYAN, GREEN_NEON, ORANGE, RED, YELLOW
)
from src.utils import format_time

HP_ORB_COLOR    = (80,  255, 160)
ARMOR_ORB_COLOR = (100, 200, 255)
ARMOR_BAR_COLOR = (80,  180, 255)
CRYSTAL_GOLD    = (255, 220, 60)


def draw_hud(surface, player, fonts: dict, elapsed_seconds: float,
             hp_orbs_on_map: int = 0, armor_orbs_on_map: int = 0):

    pad = 10

    # ── Top-left stats panel ──────────────────────────────
    panel_h = 134
    panel = pygame.Surface((260, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 160))
    surface.blit(panel, (pad, pad))
    pygame.draw.rect(surface, player.glow_color,
                     (pad, pad, 260, panel_h), 1, border_radius=4)

    surface.blit(
        fonts["small"].render(f"◈ {STAGES[player.stage][0]}", True, player.glow_color),
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
    bar_x, bar_y, bar_w, bar_h = pad + 40, pad + 80, 140, 13
    pygame.draw.rect(surface, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    filled = int(bar_w * max(0, player.hp) / player.max_hp)
    hp_col = GREEN_NEON if player.hp > 3 else (ORANGE if player.hp >= 2 else RED)
    if filled > 0:
        pygame.draw.rect(surface, hp_col, (bar_x, bar_y, filled, bar_h), border_radius=3)
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
    surface.blit(fonts["tiny"].render(f"{player.hp}/{player.max_hp}", True, WHITE),
                 (bar_x + bar_w + 4, bar_y))

    # Armor bar
    surface.blit(fonts["small"].render("ARM:", True, ARMOR_BAR_COLOR), (pad + 8, pad + 98))
    arm_x, arm_y, arm_w, arm_h = pad + 50, pad + 100, 130, 13
    pygame.draw.rect(surface, (10, 20, 50), (arm_x, arm_y, arm_w, arm_h), border_radius=3)
    if player.armor > 0:
        seg_w = (arm_w - 4) // player.max_armor
        gap   = 3
        for i in range(player.armor):
            sx = arm_x + 2 + i * (seg_w + gap)
            pygame.draw.rect(surface, ARMOR_BAR_COLOR,
                             (sx, arm_y + 1, seg_w - gap, arm_h - 2), border_radius=2)
    else:
        no_arm = fonts["tiny"].render("no armor", True, (50, 70, 100))
        surface.blit(no_arm, (arm_x + arm_w // 2 - no_arm.get_width() // 2, arm_y + 1))
    pygame.draw.rect(surface, ARMOR_BAR_COLOR, (arm_x, arm_y, arm_w, arm_h), 1, border_radius=3)
    surface.blit(fonts["tiny"].render(f"{player.armor}/{player.max_armor}", True, ARMOR_BAR_COLOR),
                 (arm_x + arm_w + 4, arm_y))

    # ── Evolution bar  OR  Crystal counter (stage 4) ─────
    if player.stage < len(STAGES) - 1:
        # Evolution progress
        next_thresh = STAGES[player.stage + 1][1]
        prev_thresh = STAGES[player.stage][1]
        span  = max(1, next_thresh - prev_thresh)
        ratio = max(0.0, min(1.0, (player.score - prev_thresh) / span))

        evo_panel = pygame.Surface((260, 30), pygame.SRCALPHA)
        evo_panel.fill((0, 0, 0, 140))
        surface.blit(evo_panel, (pad, pad + panel_h + 4))
        surface.blit(fonts["tiny"].render("EVOLUTION", True, GRAY),
                     (pad + 8, pad + panel_h + 8))
        ev_x, ev_y, ev_w, ev_h = pad + 90, pad + panel_h + 9, 160, 12
        pygame.draw.rect(surface, (30, 30, 60), (ev_x, ev_y, ev_w, ev_h), border_radius=3)
        if ratio > 0:
            pygame.draw.rect(surface, player.glow_color,
                             (ev_x, ev_y, int(ev_w * ratio), ev_h), border_radius=3)
        pygame.draw.rect(surface, player.glow_color, (ev_x, ev_y, ev_w, ev_h), 1, border_radius=3)
        surface.blit(fonts["tiny"].render(f"{next_thresh - player.score} pts", True, player.glow_color),
                     (ev_x + ev_w + 4, ev_y))
    else:
        # ── Stage 4: Crystal collection counter ──────────
        _draw_crystal_counter(surface, fonts, player, pad, panel_h)

    # ── Item indicators (top-right) ───────────────────────
    _draw_item_indicators(surface, fonts, player, hp_orbs_on_map, armor_orbs_on_map)

    # ── Objective strip (bottom) ──────────────────────────
    if player.stage == 3:
        collected = player.crystals_stage4
        needed    = max(0, PORTAL_CRYSTAL_GOAL - collected)
        if needed > 0:
            obj_text = f"Collect {needed} more crystals to open the PORTAL!"
            obj_col  = CRYSTAL_GOLD
        else:
            obj_text = "PORTAL IS OPEN — reach it to ESCAPE!"
            obj_col  = CYAN
    else:
        obj_map = {
            0: "Collect crystals to evolve",
            1: "Watch for Hunter & Laser — grab armor!",
            2: "Reach Ultimate form — dodge Bombs & gas!",
        }
        obj_text = obj_map.get(player.stage, "")
        obj_col  = CYAN

    obj_surf = fonts["small"].render(f"► {obj_text}", True, obj_col)
    ox = SCREEN_W // 2 - obj_surf.get_width() // 2
    oy = SCREEN_H - 28
    bg = pygame.Surface((obj_surf.get_width() + 16, obj_surf.get_height() + 6), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 130))
    surface.blit(bg,       (ox - 8, oy - 3))
    surface.blit(obj_surf, (ox, oy))


def _draw_crystal_counter(surface, fonts, player, pad, panel_h):
    """
    แสดงตัวนับ crystal ใน stage 4 — ใต้ panel หลัก
    แสดงเป็นวงกลมเล็กๆ 10 ดวง ที่ติดสีเหลืองเมื่อเก็บแล้ว
    """
    collected = player.crystals_stage4
    goal      = PORTAL_CRYSTAL_GOAL
    done      = collected >= goal

    tick      = pygame.time.get_ticks()
    cy_       = pad + panel_h + 4
    panel_w   = 260

    # background panel
    cp = pygame.Surface((panel_w, 46), pygame.SRCALPHA)
    border_col = (0, 220, 255) if done else CRYSTAL_GOLD
    cp.fill((0, 0, 0, 160))
    surface.blit(cp, (pad, cy_))
    pygame.draw.rect(surface, border_col, (pad, cy_, panel_w, 46), 1, border_radius=4)

    if done:
        # PORTAL OPEN — กะพริบ
        if (tick // 300) % 2 == 0:
            txt = fonts["small"].render("PORTAL IS OPEN!", True, (0, 220, 255))
            surface.blit(txt, (pad + panel_w // 2 - txt.get_width() // 2, cy_ + 14))
    else:
        # label
        label = fonts["tiny"].render(
            f"Crystals needed: {collected}/{goal}", True, CRYSTAL_GOLD)
        surface.blit(label, (pad + 8, cy_ + 4))

        # วาดดวงกลมตัวนับ
        dot_r   = 7
        spacing = (panel_w - 20) // goal
        start_x = pad + 10 + dot_r
        dot_y   = cy_ + 32

        for i in range(goal):
            cx_ = start_x + i * spacing
            if i < collected:
                # เก็บแล้ว — เหลืองสว่าง
                pygame.draw.circle(surface, CRYSTAL_GOLD, (cx_, dot_y), dot_r)
                # เพชรเล็กๆ ข้างใน
                pts = [(cx_, dot_y - dot_r + 2), (cx_ + dot_r - 2, dot_y),
                       (cx_, dot_y + dot_r - 2), (cx_ - dot_r + 2, dot_y)]
                pygame.draw.polygon(surface, (255, 255, 180), pts)
            else:
                # ยังไม่ได้เก็บ — วงจาง
                pygame.draw.circle(surface, (60, 50, 20), (cx_, dot_y), dot_r)
                pygame.draw.circle(surface, (120, 100, 30), (cx_, dot_y), dot_r, 1)

        # บอกเหลืออีกกี่ชิ้น
        left = goal - collected
        txt2 = fonts["tiny"].render(f"{left} more", True, (180, 150, 50))
        surface.blit(txt2, (pad + panel_w - txt2.get_width() - 8, cy_ + 4))


def _draw_item_indicators(surface, fonts, player, hp_orbs, armor_orbs):
    tick = pygame.time.get_ticks()
    pad  = 10
    pw   = 190
    ph   = 36
    px_  = SCREEN_W - pw - pad

    _draw_orb_row(surface, fonts, px_, pad,          pw, ph, tick,
                  hp_orbs,    player.hp    >= player.max_hp,
                  HP_ORB_COLOR,    "HP",  "+HP on map!")
    _draw_orb_row(surface, fonts, px_, pad + ph + 4, pw, ph, tick,
                  armor_orbs, player.armor >= player.max_armor,
                  ARMOR_ORB_COLOR, "ARM", "+Armor on map!")


def _draw_orb_row(surface, fonts, px, py, pw, ph, tick,
                  orbs_on_map, is_full, color, label_full, label_avail):
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 150))
    surface.blit(panel, (px, py))

    if is_full:
        pygame.draw.rect(surface, color, (px, py, pw, ph), 1, border_radius=4)
        txt = fonts["tiny"].render(f"{label_full} FULL", True, color)
        surface.blit(txt, (px + pw // 2 - txt.get_width() // 2,
                           py + ph // 2 - txt.get_height() // 2))
    elif orbs_on_map > 0:
        blink      = (tick // 380) % 2 == 0
        border_col = color if blink else tuple(c // 3 for c in color)
        pygame.draw.rect(surface, border_col, (px, py, pw, ph), 1, border_radius=4)
        ix, iy, ir = px + 16, py + ph // 2, 7
        pygame.draw.circle(surface, tuple(c // 4 for c in color), (ix, iy), ir)
        pygame.draw.circle(surface, color, (ix, iy), ir, 2)
        pygame.draw.line(surface, color, (ix, iy - ir + 2), (ix, iy + ir - 2), 2)
        pygame.draw.line(surface, color, (ix - ir + 2, iy), (ix + ir - 2, iy), 2)
        txt_col = color if blink else tuple(c // 2 for c in color)
        txt = fonts["tiny"].render(f"{label_avail} ({orbs_on_map})", True, txt_col)
        surface.blit(txt, (ix + ir + 5, py + ph // 2 - txt.get_height() // 2))
    else:
        pygame.draw.rect(surface, tuple(c // 4 for c in color),
                         (px, py, pw, ph), 1, border_radius=4)
        dots = "." * ((tick // 500) % 4)
        txt  = fonts["tiny"].render(f"{label_full} orb coming{dots}",
                                    True, tuple(c // 2 for c in color))
        surface.blit(txt, (px + pw // 2 - txt.get_width() // 2,
                           py + ph // 2 - txt.get_height() // 2))
