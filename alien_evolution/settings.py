"""
settings.py
===========
All game-wide constants live here.
Change values here to affect the whole game without touching other files.

Sections:
  - Screen
  - Colours
  - Evolution Stages
  - Fonts
  - Sound stubs  ← SOUND: all audio loaded here
  - Image stubs  ← IMAGE: all images loaded here
"""

import pygame

# ─────────────────────────────────────────────
# SCREEN
# ─────────────────────────────────────────────
SCREEN_W = 800
SCREEN_H = 600
FPS      = 60
TITLE    = "Alien Organism Evolution"

# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# EVOLUTION STAGES
# Columns: name, score_needed, radius, speed,
#          body_color, glow_color, pulse_color
# Edit these rows to change stage thresholds,
# sizes, speeds, and colours.
# ─────────────────────────────────────────────
STAGES = [
    ("Alien Larva",    0,  18, 4.0, (80,  200, 80),  (0,   255, 80),  (0,   180, 60)),
    ("Alien Creature", 10, 26, 4.5, (0,   200, 230), (0,   240, 255), (0,   160, 200)),
    ("Mutant Alien",   25, 34, 5.0, (200, 0,   255), (220, 80,  255), (160, 0,   200)),
    ("Ultimate Alien", 45, 44, 5.5, (255, 200, 0),   (255, 230, 80),  (220, 160, 0)),
]

# ─────────────────────────────────────────────
# DIFFICULTY MILESTONES
# (score_threshold, event_key)
# event_key is checked in game.py difficulty_scaling()
# ─────────────────────────────────────────────
DIFF_ADD_POISON   = 15   # score at which extra poison cloud spawns
DIFF_SPEED_DRONE  = 30   # score at which drones speed up
DIFF_ADD_DRONE    = 38   # score at which second drone spawns
DIFF_PORTAL_SCORE = 45   # score at which escape portal appears


# ─────────────────────────────────────────────
# FONTS
# To use a custom TTF font replace SysFont with:
#   pygame.font.Font("assets/fonts/myFont.ttf", size)
# ─────────────────────────────────────────────
def load_fonts():
    """Call once after pygame.init(). Returns a dict of font objects."""
    return {
        "title":  pygame.font.SysFont("Consolas", 52, bold=True),
        "large":  pygame.font.SysFont("Consolas", 36, bold=True),
        "medium": pygame.font.SysFont("Consolas", 24),
        "small":  pygame.font.SysFont("Consolas", 18),
        "tiny":   pygame.font.SysFont("Consolas", 14),
    }


# ─────────────────────────────────────────────
# SOUNDS
# Uncomment each line and set your file paths.
# ─────────────────────────────────────────────
def load_sounds():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/lab_ambient.wav")
    pygame.mixer.music.set_volume(0.5)

    """
    Load all sound effects and music.
    Returns a dict of Sound objects (or None if not loaded).

    SOUND: MUSIC — looping background music
        pygame.mixer.music.load("assets/music/lab_ambient.ogg")
        pygame.mixer.music.set_volume(0.5)
        (call pygame.mixer.music.play(-1) in game.py reset())

    SOUND: COLLECT — crystal pickup
        sounds["collect"] = pygame.mixer.Sound("assets/sfx/collect.wav")

    SOUND: HIT — player takes damage
        sounds["hit"] = pygame.mixer.Sound("assets/sfx/hit.wav")

    SOUND: EVOLVE — player evolves
        sounds["evolve"] = pygame.mixer.Sound("assets/sfx/evolve.wav")

    SOUND: PORTAL_OPEN — escape portal appears
        sounds["portal"] = pygame.mixer.Sound("assets/sfx/portal_open.wav")

    SOUND: WIN — victory
        sounds["win"] = pygame.mixer.Sound("assets/sfx/victory.wav")

    SOUND: GAMEOVER — death
        sounds["gameover"] = pygame.mixer.Sound("assets/sfx/gameover.wav")
    """
    sounds = {
        "collect":  None,
        "hit":      None,
        "evolve":   None,
        "portal":   None,
        "win":      None,
        "gameover": None,
    }
    # ── Uncomment below to enable sounds ──────────────────────────
    # pygame.mixer.music.load("assets/music/lab_ambient.ogg")
    # pygame.mixer.music.set_volume(0.5)
    # sounds["collect"]  = pygame.mixer.Sound("assets/sfx/collect.wav")
    # sounds["hit"]      = pygame.mixer.Sound("assets/sfx/hit.wav")
    # sounds["evolve"]   = pygame.mixer.Sound("assets/sfx/evolve.wav")
    # sounds["portal"]   = pygame.mixer.Sound("assets/sfx/portal_open.wav")
    # sounds["win"]      = pygame.mixer.Sound("assets/sfx/victory.wav")
    # sounds["gameover"] = pygame.mixer.Sound("assets/sfx/gameover.wav")
    return sounds


# ─────────────────────────────────────────────
# IMAGES
# Uncomment each line and set your file paths.
# ─────────────────────────────────────────────
def load_images():
    """
    Load all sprite / background images.
    Returns a dict of Surface objects (or None if not loaded).

    IMAGE: BACKGROUND — lab floor texture (800x600)
        images["background"] = pygame.image.load("assets/images/lab_floor.png").convert()
        images["background"] = pygame.transform.scale(images["background"], (SCREEN_W, SCREEN_H))

    IMAGE: MENU_BG — full-screen menu art
        images["menu_bg"] = pygame.image.load("assets/images/menu_bg.png").convert()
        images["menu_bg"] = pygame.transform.scale(images["menu_bg"], (SCREEN_W, SCREEN_H))

    IMAGE: LOGO — title logo shown on menu
        images["logo"] = pygame.image.load("assets/images/logo.png").convert_alpha()

    IMAGE: PLAYER — one sprite per evolution stage
        images["player"] = [
            pygame.image.load("assets/images/stage1.png").convert_alpha(),
            pygame.image.load("assets/images/stage2.png").convert_alpha(),
            pygame.image.load("assets/images/stage3.png").convert_alpha(),
            pygame.image.load("assets/images/stage4.png").convert_alpha(),
        ]

    IMAGE: CRYSTAL — energy crystal sprite
        images["crystal"] = pygame.image.load("assets/images/crystal.png").convert_alpha()

    IMAGE: POISON — toxic cloud PNG with transparency
        images["poison"] = pygame.image.load("assets/images/poison_cloud.png").convert_alpha()

    IMAGE: DRONE — security drone sprite
        images["drone"] = pygame.image.load("assets/images/drone.png").convert_alpha()

    IMAGE: PORTAL — escape portal sprite
        images["portal"] = pygame.image.load("assets/images/portal.png").convert_alpha()
    """
    images = {
        "background": None,
        "menu_bg":    None,
        "logo":       None,
        "player":     None,   # list of 4 surfaces when enabled
        "crystal":    None,
        "poison":     None,
        "drone":      None,
        "portal":     None,
    }
    # ── Uncomment below to enable images ──────────────────────────
    # images["background"] = pygame.transform.scale(
    #     pygame.image.load("assets/images/lab_floor.png").convert(),
    #     (SCREEN_W, SCREEN_H))
    # images["menu_bg"] = pygame.transform.scale(
    #     pygame.image.load("assets/images/menu_bg.png").convert(),
    #     (SCREEN_W, SCREEN_H))
    # images["logo"]    = pygame.image.load("assets/images/logo.png").convert_alpha()
    # images["player"]  = [
    #     pygame.image.load(f"assets/images/stage{i+1}.png").convert_alpha()
    #     for i in range(4)
    # ]
    # images["crystal"] = pygame.image.load("assets/images/crystal.png").convert_alpha()
    # images["poison"]  = pygame.image.load("assets/images/poison_cloud.png").convert_alpha()
    # images["drone"]   = pygame.image.load("assets/images/drone.png").convert_alpha()
    # images["portal"]  = pygame.image.load("assets/images/portal.png").convert_alpha()
    return images
