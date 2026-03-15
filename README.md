# Alien Organism Evolution 🧬

A 2D Arcade Survival / Growth / Evolution game built with **Python + Pygame**.

---

## Project Structure

```
alien_evolution/
│
├── main.py               ← Entry point — run this file
├── requirements.txt      ← Dependencies (pygame only)
│
├── src/                  ← All game source modules
│   ├── __init__.py
│   ├── constants.py      ← Colours, screen size, stage data, fonts
│   ├── assets.py         ← Image & sound loader  ← EDIT TO ADD SPRITES/AUDIO
│   ├── utils.py          ← Shared helpers (dist, glow, grid)
│   ├── player.py         ← Player class (movement, HP, evolution)
│   ├── entities.py       ← Crystal, PoisonCloud, Drone, Portal, Particle
│   ├── hud.py            ← On-screen UI during gameplay
│   ├── screens.py        ← Menu, Game Over, Victory screens
│   └── game.py           ← Game class + difficulty scaling
│
└── assets/               ← Put your image and audio files here
    ├── images/           ← .png sprites
    │   ├── lab_floor.png      (800x600 background)
    │   ├── menu_bg.png        (800x600 menu art)
    │   ├── logo.png           (title logo)
    │   ├── stage1.png         (Alien Larva sprite)
    │   ├── stage2.png         (Alien Creature sprite)
    │   ├── stage3.png         (Mutant Alien sprite)
    │   ├── stage4.png         (Ultimate Alien sprite)
    │   ├── crystal.png        (energy crystal)
    │   ├── poison_cloud.png   (toxic gas, transparent PNG)
    │   ├── drone.png          (security drone)
    │   └── portal.png         (escape portal)
    │
    ├── music/
    │   └── lab_ambient.ogg    (background music, loops)
    │
    └── sfx/
        ├── collect.wav        (crystal pickup)
        ├── hit.wav            (player takes damage)
        ├── evolve.wav         (evolution fanfare)
        ├── portal_open.wav    (portal appears)
        ├── victory.wav        (win)
        └── gameover.wav       (game over)
```

---

## Setup in PyCharm (with Virtual Environment)

### Step 1 — Open the project
1. Open **PyCharm**
2. `File → Open` → select the `alien_evolution/` folder
3. PyCharm will detect it as a project

### Step 2 — Create a virtual environment
1. Go to `File → Settings` (Windows/Linux) or `PyCharm → Preferences` (macOS)
2. Navigate to `Project: alien_evolution → Python Interpreter`
3. Click the gear icon ⚙ → **Add Interpreter → Add Local Interpreter**
4. Choose **Virtualenv Environment**
5. Set **Location** to `alien_evolution/venv`
6. Choose your **Base interpreter** (Python 3.9+ recommended)
7. Click **OK**

### Step 3 — Install dependencies
Either:

**Option A — PyCharm terminal** (recommended):
```bash
pip install -r requirements.txt
```

**Option B — PyCharm package manager**:
1. `File → Settings → Python Interpreter`
2. Click `+` → search `pygame` → Install

### Step 4 — Run the game
- Right-click `main.py` → **Run 'main'**
- Or press `Shift+F10` with `main.py` open

---

## Controls

| Key | Action |
|-----|--------|
| W / ↑ | Move Up |
| S / ↓ | Move Down |
| A / ← | Move Left |
| D / → | Move Right |
| ENTER | Start game (menu) |
| ESC | Return to menu |
| R | Restart (game over / victory) |
| M | Back to menu (game over / victory) |

---

## Evolution Stages

| Stage | Score Needed | Name |
|-------|-------------|------|
| 1 | 0 | Alien Larva |
| 2 | 10 | Alien Creature |
| 3 | 25 | Mutant Alien |
| 4 | 45 | Ultimate Alien → Portal appears! |

---

## Adding Images & Sounds

All asset loading is in **`src/assets.py`**.
Search for these comment tags to find the right place:

| Tag | What to replace |
|-----|----------------|
| `IMAGE: BACKGROUND` | Lab floor texture |
| `IMAGE: MENU_BG` | Menu screen background |
| `IMAGE: LOGO` | Title logo |
| `IMAGE: PLAYER` | Alien sprite (4 stages) |
| `IMAGE: CRYSTAL` | Crystal sprite |
| `IMAGE: POISON` | Toxic cloud PNG |
| `IMAGE: DRONE` | Drone sprite |
| `IMAGE: PORTAL` | Portal sprite |
| `SOUND: MUSIC` | Background music |
| `SOUND: COLLECT` | Crystal pickup SFX |
| `SOUND: HIT` | Damage SFX |
| `SOUND: EVOLVE` | Evolution SFX |
| `SOUND: PORTAL_OPEN` | Portal appears SFX |
| `SOUND: WIN` | Victory SFX |
| `SOUND: GAMEOVER` | Game over SFX |

---

## Customisation Quick Reference

| What to change | File | What to edit |
|----------------|------|-------------|
| Screen size | `src/constants.py` | `SCREEN_W`, `SCREEN_H` |
| Colours | `src/constants.py` | Colour constants |
| Stage names/colours/speed | `src/constants.py` | `STAGES` list |
| Difficulty thresholds | `src/constants.py` | `DIFF_*` constants |
| Player starting HP/speed | `src/player.py` | `Player.__init__` |
| Crystal types & values | `src/entities.py` | `Crystal.TYPES` |
| HUD layout | `src/hud.py` | `draw_hud()` |
| Menu / screens | `src/screens.py` | `draw_menu()` etc. |
