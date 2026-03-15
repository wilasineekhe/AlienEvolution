"""
constants.py
============================================================
All game-wide constants.
============================================================
"""

import pygame

SCREEN_W = 800
SCREEN_H = 600
FPS      = 60
TITLE    = "Alien Organism Evolution"

# ── Colours ───────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_BG    = (8,   10,  20)
GRID_COLOR = (20,  30,  50)
GREEN_NEON = (0,   255, 120)
CYAN       = (0,   220, 255)
PURPLE     = (180, 0,   255)
YELLOW     = (255, 230, 0)
ORANGE     = (255, 140, 0)
RED        = (255, 40,  40)
PINK       = (255, 80,  200)
GRAY       = (100, 100, 100)
DARK_GREEN = (0,   80,  40)
TEAL       = (0,   180, 160)

# ── Evolution Stages ──────────────────────────────────────
# (name, score_needed, radius, speed, body_color, glow_color, pulse_color)
STAGES = [
    ("Alien Larva",    0,  18, 4.0, (80,  200, 80),  (0,   255, 80),  (0,   180, 60)),
    ("Alien Creature", 10, 26, 4.5, (0,   200, 230), (0,   240, 255), (0,   160, 200)),
    ("Mutant Alien",   25, 34, 5.0, (200, 0,   255), (220, 80,  255), (160, 0,   200)),
    ("Ultimate Alien", 45, 44, 5.5, (255, 200, 0),   (255, 230, 80),  (220, 160, 0)),
]

# ── Portal condition (stage 4) ────────────────────────────────
# portal เปิดเมื่อเก็บ crystal ครบ PORTAL_CRYSTAL_GOAL ชิ้น ขณะอยู่ใน stage 4
# นับเฉพาะ crystal ที่เก็บตอนเป็น Ultimate Alien เท่านั้น
PORTAL_CRYSTAL_GOAL = 10   # เก็บ 10 ชิ้นใน stage 4 → portal เปิด
DIFF_PORTAL_SCORE   = 999  # ไม่ใช้แล้ว (คงไว้ไม่ให้ error)

# ── Fonts ─────────────────────────────────────────────────
def load_fonts():
    return {
        "title":  pygame.font.SysFont("Consolas", 52, bold=True),
        "large":  pygame.font.SysFont("Consolas", 36, bold=True),
        "medium": pygame.font.SysFont("Consolas", 24),
        "small":  pygame.font.SysFont("Consolas", 18),
        "tiny":   pygame.font.SysFont("Consolas", 14),
    }
