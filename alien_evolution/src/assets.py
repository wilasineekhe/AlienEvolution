"""
assets.py
============================================================
Central loader for ALL images and sounds.
This is the only file you need to edit when adding
real sprites or audio.

HOW TO ADD AN IMAGE
-------------------
1. Put the .png file in  assets/images/
2. Find the matching IMAGE: comment below
3. Uncomment the pygame.image.load() line and set the path

HOW TO ADD SOUND / MUSIC
-------------------------
1. Put .ogg or .wav files in  assets/music/  or  assets/sfx/
2. Find the matching SOUND: comment below
3. Uncomment the load line

SOUND TAGS (search these in your IDE):
  SOUND: MUSIC        background music (loops)
  SOUND: COLLECT      crystal pickup
  SOUND: HIT          player takes damage
  SOUND: EVOLVE       evolution fanfare
  SOUND: PORTAL_OPEN  portal appears
  SOUND: WIN          victory
  SOUND: GAMEOVER     game over

IMAGE TAGS (search these in your IDE):
  IMAGE: BACKGROUND   lab floor texture
  IMAGE: MENU_BG      full-screen menu art
  IMAGE: LOGO         title logo
  IMAGE: PLAYER       alien sprite per stage (list of 4)
  IMAGE: CRYSTAL      energy crystal sprite
  IMAGE: POISON       toxic cloud PNG (with alpha)
  IMAGE: DRONE        security drone sprite
  IMAGE: PORTAL       escape portal sprite
============================================================
"""

import pygame
from src.constants import SCREEN_W, SCREEN_H


# ──────────────────────────────────────────────────────────
# SOUND HELPER
# ──────────────────────────────────────────────────────────

def play_sfx(sfx):
    """Safe wrapper — plays sound only if it was loaded."""
    if sfx:
        sfx.play()


# ──────────────────────────────────────────────────────────
# ASSET LOADER  (call once at startup)
# ──────────────────────────────────────────────────────────

def load_assets():
    """
    Load all images and sounds.
    Returns a dict:  assets["key"] = object

    If an image/sound is not loaded it is set to None,
    and the game will draw shapes/play silence instead.
    """
    assets = {}

    # ── IMAGES ────────────────────────────────────────────

    # IMAGE: BACKGROUND — lab floor / room texture (800×600)
    # assets["background"] = _load_image("assets/images/lab_floor.png", (SCREEN_W, SCREEN_H), alpha=False)
    assets["background"] = None

    # IMAGE: MENU_BG — full-screen art on menu / screens
    # assets["menu_bg"] = _load_image("assets/images/menu_bg.png", (SCREEN_W, SCREEN_H), alpha=False)
    assets["menu_bg"] = None

    # IMAGE: LOGO — title logo shown at top of menu
    # assets["logo"] = _load_image("assets/images/logo.png")
    assets["logo"] = None

    # IMAGE: PLAYER — one sprite per evolution stage (list of 4)
    # Sprites are square; the game scales them to radius*2 × radius*2.
    # assets["player"] = [
    #     _load_image("assets/images/stage1.png"),
    #     _load_image("assets/images/stage2.png"),
    #     _load_image("assets/images/stage3.png"),
    #     _load_image("assets/images/stage4.png"),
    # ]
    assets["player"] = None     # None = draw circle instead

    # IMAGE: CRYSTAL — energy crystal (recommended ~30×30 transparent PNG)
    # assets["crystal"] = _load_image("assets/images/crystal.png")
    assets["crystal"] = None

    # IMAGE: POISON — toxic cloud PNG with transparency (recommended ~100×100)
    # assets["poison"] = _load_image("assets/images/poison_cloud.png")
    assets["poison"] = None

    # IMAGE: DRONE — security drone sprite (recommended ~40×40)
    # assets["drone"] = _load_image("assets/images/drone.png")
    assets["drone"] = None

    # IMAGE: PORTAL — escape portal sprite (recommended ~80×80)
    # assets["portal"] = _load_image("assets/images/portal.png")
    assets["portal"] = None

    # ── SOUNDS ────────────────────────────────────────────

    # SOUND: MUSIC — background music (OGG recommended, loops forever)
    pygame.mixer.music.load("assets/music/lab_ambient.wav")
    pygame.mixer.music.set_volume(0.45)


    # SOUND: COLLECT — crystal pickup sound
    # assets["sfx_collect"] = _load_sfx("assets/sfx/collect.wav")
    assets["sfx_collect"] = _load_sfx("assets/sfx/winkcollect.wav")

    # SOUND: HIT — player takes damage
    # assets["sfx_hit"] = _load_sfx("assets/sfx/hit.wav")
    assets["sfx_hit"] = _load_sfx("assets/sfx/hit.wav")

    # SOUND: EVOLVE — evolution fanfare
    # assets["sfx_evolve"] = _load_sfx("assets/sfx/evolve.wav")
    assets["sfx_evolve"] = _load_sfx("assets/sfx/evolve.wav")

    # SOUND: PORTAL_OPEN — portal appears
    # assets["sfx_portal"] = _load_sfx("assets/sfx/portal_open.wav")
    assets["sfx_portal"] = _load_sfx("assets/sfx/portal_open.wav")

    # SOUND: WIN — victory jingle
    # assets["sfx_win"] = _load_sfx("assets/sfx/victory.wav")
    assets["sfx_win"] = _load_sfx("assets/sfx/victory.wav")

    # SOUND: GAMEOVER — death / game-over sting
    # assets["sfx_gameover"] = _load_sfx("assets/sfx/gameover.wav")
    assets["sfx_gameover"] = _load_sfx("assets/sfx/gameover.wav")

    return assets


# ──────────────────────────────────────────────────────────
# PRIVATE HELPERS
# ──────────────────────────────────────────────────────────

def _load_image(path, size=None, alpha=True):
    """Load an image; return None if file not found."""
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except (pygame.error, FileNotFoundError) as e:
        print(f"[assets] WARNING: could not load image '{path}': {e}")
        return None


def _load_sfx(path, volume=0.7):
    """Load a sound effect; return None if file not found."""
    try:
        sfx = pygame.mixer.Sound(path)
        sfx.set_volume(volume)
        return sfx
    except (pygame.error, FileNotFoundError) as e:
        print(f"[assets] WARNING: could not load sound '{path}': {e}")
        return None
