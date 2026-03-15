"""
entities.py
===========
All game object classes.

Classes:
  - Player       — the alien organism controlled by the player
  - Crystal      — collectable energy crystals
  - PoisonCloud  — stationary toxic gas hazard
  - Drone        — moving security drone hazard
  - Portal       — escape portal (win condition)
  - Particle     — short-lived sparkle effect
"""

import pygame
import math
import random

from settings import (
    SCREEN_W, SCREEN_H, STAGES,
    WHITE, YELLOW, CYAN, RED, ORANGE, PINK, GREEN_NEON, GRAY
)
from utils import dist, draw_glow_circle, play_sfx


# ─────────────────────────────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────────────────────────────

class Player:
    def __init__(self):
        self.x       = SCREEN_W // 2
        self.y       = SCREEN_H // 2
        self.stage   = 0
        self._apply_stage_stats()
        self.hp            = 5
        self.max_hp        = 5
        self.score         = 0
        self.is_alive      = True
        self.escaped       = False
        self.invincible_timer = 0     # frames of invincibility after hit
        self.evolve_flash     = 0     # frames of evolution ring effect
        self.pulse            = 0.0  # sine oscillator for body pulse

    # ── Internal ──────────────────────────────────────────────────

    def _apply_stage_stats(self):
        """Pull radius, speed, and colours from the STAGES table."""
        _, _, self.radius, self.speed, \
            self.body_color, self.glow_color, self.pulse_color = STAGES[self.stage]

    # ── Public API ────────────────────────────────────────────────

    def handle_input(self, keys):
        """Move player based on WASD / arrow keys. Clamp to screen edges."""
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += self.speed

        # Normalise diagonal so speed is consistent
        if dx != 0 and dy != 0:
            factor = self.speed / math.sqrt(dx * dx + dy * dy)
            dx *= factor
            dy *= factor

        self.x = max(self.radius, min(SCREEN_W - self.radius, self.x + dx))
        self.y = max(self.radius, min(SCREEN_H - self.radius, self.y + dy))

    def check_evolution(self, sounds):
        """Evolve to the next stage if score threshold is met."""
        new_stage = 0
        for i, (_, threshold, *_rest) in enumerate(STAGES):
            if self.score >= threshold:
                new_stage = i
        if new_stage > self.stage:
            self.stage = new_stage
            self._apply_stage_stats()
            self.evolve_flash = 90      # ~1.5 seconds at 60 fps
            # SOUND: EVOLVE
            play_sfx(sounds, "evolve")
            return True
        return False

    def take_damage(self, sounds):
        """Subtract 1 HP if not invincible. Trigger death if HP reaches 0."""
        if self.invincible_timer <= 0:
            self.hp -= 1
            self.invincible_timer = 60  # 1 second grace period
            # SOUND: HIT
            play_sfx(sounds, "hit")
            if self.hp <= 0:
                self.is_alive = False

    def update(self):
        """Tick timers and oscillators."""
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.evolve_flash > 0:
            self.evolve_flash -= 1
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)

    def draw(self, surface, images=None):
        """
        Draw the alien organism.

        IMAGE: PLAYER
        If images["player"] is a list of 4 surfaces (one per stage),
        replace the drawn shape with the appropriate sprite:

            def draw(self, surface, images=None):
                if not self.is_alive:
                    return
                if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
                    return
                if images and images.get("player"):
                    img = images["player"][self.stage]
                    d   = self.radius * 2
                    img = pygame.transform.scale(img, (d, d))
                    surface.blit(img, (int(self.x - self.radius), int(self.y - self.radius)))
                    return
                # ... rest of drawn code below
        """
        if not self.is_alive:
            return

        # Blink during invincibility
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return

        pos     = (int(self.x), int(self.y))
        pulse_r = self.radius + int(math.sin(self.pulse) * 3)

        # Glow ring
        glow_col = self.glow_color if self.evolve_flash == 0 else (255, 255, 120)
        draw_glow_circle(surface, glow_col, pos, pulse_r, layers=5)

        # Body
        pygame.draw.circle(surface, self.body_color, pos, pulse_r)

        # Highlight
        inner_pos = (int(self.x - self.radius * 0.2), int(self.y - self.radius * 0.2))
        pygame.draw.circle(surface, WHITE, inner_pos, max(4, self.radius // 3), 2)

        # Nucleus
        pygame.draw.circle(surface, self.pulse_color, pos, self.radius // 4)

        # Evolution flash ring
        if self.evolve_flash > 0:
            alpha  = min(255, self.evolve_flash * 3)
            ring_r = self.radius + (90 - self.evolve_flash) // 2
            ring_surf = pygame.Surface((ring_r * 4, ring_r * 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*YELLOW, alpha),
                               (ring_r * 2, ring_r * 2), ring_r, 3)
            surface.blit(ring_surf,
                         (int(self.x) - ring_r * 2, int(self.y) - ring_r * 2))


# ─────────────────────────────────────────────────────────────────
# CRYSTAL
# ─────────────────────────────────────────────────────────────────

class Crystal:
    # (name, color, score_value, radius, rarity_weight)
    TYPES = [
        ("Basic",    CYAN,           1,  8,  70),
        ("Rare",     PINK,           3, 11,  25),
        ("Evo Core", (255, 220, 50), 5, 14,   5),
    ]

    def __init__(self, avoid_x=None, avoid_y=None, avoid_r=0):
        self.pulse = random.uniform(0, 2 * math.pi)
        self.respawn(avoid_x, avoid_y, avoid_r)

    def _pick_type(self):
        """Weighted random selection of crystal type."""
        weights  = [t[4] for t in self.TYPES]
        total    = sum(weights)
        roll     = random.uniform(0, total)
        cumul    = 0
        idx      = 0
        for i, w in enumerate(weights):
            cumul += w
            if roll <= cumul:
                idx = i
                break
        _, self.color, self.value, self.radius, _ = self.TYPES[idx]

    def respawn(self, avoid_x=None, avoid_y=None, avoid_r=0):
        """Place at a random position, keeping away from the player."""
        for _ in range(50):
            x = random.randint(30, SCREEN_W - 30)
            y = random.randint(30, SCREEN_H - 30)
            if avoid_x is None or dist(x, y, avoid_x, avoid_y) > avoid_r + 40:
                self.x, self.y = x, y
                break
        else:
            self.x = random.randint(30, SCREEN_W - 30)
            self.y = random.randint(30, SCREEN_H - 30)
        self._pick_type()

    def update(self):
        self.pulse = (self.pulse + 0.07) % (2 * math.pi)

    def draw(self, surface, images=None):
        """
        Draw a diamond-shaped crystal.

        IMAGE: CRYSTAL
        Replace with:
            if images and images.get("crystal"):
                r   = self.radius
                img = pygame.transform.scale(images["crystal"], (r*2, r*2))
                surface.blit(img, (int(self.x - r), int(self.y - r)))
                return
        """
        pos = (int(self.x), int(self.y))
        r   = self.radius + int(math.sin(self.pulse) * 2)

        draw_glow_circle(surface, self.color, pos, r, layers=3)

        # Diamond polygon
        pts = [
            (self.x,     self.y - r),
            (self.x + r, self.y),
            (self.x,     self.y + r),
            (self.x - r, self.y),
        ]
        pygame.draw.polygon(surface, self.color, [(int(p[0]), int(p[1])) for p in pts])
        pygame.draw.polygon(surface, WHITE,      [(int(p[0]), int(p[1])) for p in pts], 1)

        # Inner sparkle
        pygame.draw.circle(surface, WHITE,
                           (int(self.x - 2), int(self.y - 2)), max(1, r // 3))


# ─────────────────────────────────────────────────────────────────
# POISON CLOUD
# ─────────────────────────────────────────────────────────────────

class PoisonCloud:
    def __init__(self, player_x=SCREEN_W // 2, player_y=SCREEN_H // 2):
        self.pulse       = random.uniform(0, 2 * math.pi)
        self.alpha_cycle = random.uniform(0, 2 * math.pi)
        self._spawn(player_x, player_y)

    def _spawn(self, player_x, player_y):
        """Spawn at least 120 px away from the player."""
        for _ in range(50):
            x = random.randint(50, SCREEN_W - 50)
            y = random.randint(50, SCREEN_H - 50)
            if dist(x, y, player_x, player_y) > 120:
                self.x, self.y = x, y
                break
        else:
            self.x = random.randint(50, SCREEN_W - 50)
            self.y = random.randint(50, SCREEN_H - 50)
        self.radius = random.randint(28, 42)

    def update(self):
        self.pulse       = (self.pulse       + 0.04) % (2 * math.pi)
        self.alpha_cycle = (self.alpha_cycle + 0.03) % (2 * math.pi)

    def draw(self, surface, images=None):
        """
        Draw a pulsing translucent toxic cloud.

        IMAGE: POISON
        Replace with:
            if images and images.get("poison"):
                alpha = int(140 + math.sin(self.alpha_cycle) * 40)
                img   = images["poison"].copy()
                img   = pygame.transform.scale(img, (self.radius*2, self.radius*2))
                img.set_alpha(alpha)
                surface.blit(img, (int(self.x - self.radius), int(self.y - self.radius)))
                return
        """
        pos   = (int(self.x), int(self.y))
        r     = self.radius + int(math.sin(self.pulse) * 4)
        alpha = int(140 + math.sin(self.alpha_cycle) * 40)

        for layer_r, layer_a in [(r, alpha), (r * 7 // 10, min(255, alpha + 40))]:
            cloud_surf = pygame.Surface((layer_r * 2 + 4, layer_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(cloud_surf, (60, 200, 80, layer_a),
                               (layer_r + 2, layer_r + 2), layer_r)
            surface.blit(cloud_surf, (pos[0] - layer_r - 2, pos[1] - layer_r - 2))

        # Centre dot
        pygame.draw.circle(surface, (30, 120, 40), pos, max(4, r // 4))


# ─────────────────────────────────────────────────────────────────
# DRONE HAZARD
# ─────────────────────────────────────────────────────────────────

class Drone:
    def __init__(self, speed=2.5):
        self.x    = random.randint(60, SCREEN_W - 60)
        self.y    = random.randint(60, SCREEN_H - 60)
        angle     = random.uniform(0, 2 * math.pi)
        self.vx   = math.cos(angle) * speed
        self.vy   = math.sin(angle) * speed
        self.size  = 16
        self.pulse = 0.0

    def update(self):
        """Move and bounce off screen walls."""
        self.x += self.vx
        self.y += self.vy
        if self.x - self.size < 0 or self.x + self.size > SCREEN_W:
            self.vx *= -1
        if self.y - self.size < 0 or self.y + self.size > SCREEN_H:
            self.vy *= -1
        self.x = max(self.size, min(SCREEN_W - self.size, self.x))
        self.y = max(self.size, min(SCREEN_H - self.size, self.y))
        self.pulse = (self.pulse + 0.08) % (2 * math.pi)

    def draw(self, surface, images=None):
        """
        Draw the security drone.

        IMAGE: DRONE
        Replace with:
            if images and images.get("drone"):
                s   = self.size
                img = pygame.transform.scale(images["drone"], (s*2, s*2))
                surface.blit(img, (int(self.x - s), int(self.y - s)))
                return
        """
        pos = (int(self.x), int(self.y))
        s   = self.size

        draw_glow_circle(surface, RED, pos, s, layers=3)

        rect = pygame.Rect(int(self.x - s), int(self.y - s), s * 2, s * 2)
        pygame.draw.rect(surface, (180, 20, 20), rect, border_radius=4)
        pygame.draw.rect(surface, RED,           rect, 2, border_radius=4)

        # Blinking eye
        eye_r  = max(3, s // 3)
        blink  = int(math.sin(self.pulse * 3) * eye_r * 0.4)
        pygame.draw.circle(surface, (255, 80, 80), pos, eye_r + blink)
        pygame.draw.circle(surface, WHITE, pos, max(1, eye_r // 2))

        # Antennae
        pygame.draw.line(surface, ORANGE,
                         (int(self.x - 5), int(self.y - s)),
                         (int(self.x - 5), int(self.y - s - 8)), 2)
        pygame.draw.line(surface, ORANGE,
                         (int(self.x + 5), int(self.y - s)),
                         (int(self.x + 5), int(self.y - s - 8)), 2)


# ─────────────────────────────────────────────────────────────────
# ESCAPE PORTAL
# ─────────────────────────────────────────────────────────────────

class Portal:
    def __init__(self, sounds=None):
        self.x      = random.randint(80, SCREEN_W - 80)
        self.y      = random.randint(80, SCREEN_H - 80)
        self.radius = 32
        self.active = True
        self.spin   = 0.0
        self.pulse  = 0.0
        # SOUND: PORTAL_OPEN
        if sounds:
            play_sfx(sounds, "portal")

    def update(self):
        self.spin  = (self.spin  + 0.05) % (2 * math.pi)
        self.pulse = (self.pulse + 0.06) % (2 * math.pi)

    def draw(self, surface, fonts, images=None):
        """
        Draw the animated escape portal.

        IMAGE: PORTAL
        Replace with:
            if images and images.get("portal"):
                r   = self.radius
                img = pygame.transform.scale(images["portal"], (r*2, r*2))
                surface.blit(img, (int(self.x - r), int(self.y - r)))
                return
        """
        pos = (int(self.x), int(self.y))
        r   = self.radius + int(math.sin(self.pulse) * 5)

        draw_glow_circle(surface, CYAN, pos, r + 10, layers=6)

        # Spinning dot ring
        for i in range(12):
            angle = self.spin + i * (2 * math.pi / 12)
            dx    = int(self.x + math.cos(angle) * (r + 6))
            dy    = int(self.y + math.sin(angle) * (r + 6))
            col   = (0, 200 + int(math.sin(angle + self.spin) * 55), 255)
            pygame.draw.circle(surface, col, (dx, dy), 4)

        # Body
        pygame.draw.circle(surface, (0, 30, 60), pos, r)
        pygame.draw.circle(surface, CYAN, pos, r, 3)

        # Swirl lines
        for i in range(3):
            ang = self.spin * 2 + i * (2 * math.pi / 3)
            sx  = int(self.x + math.cos(ang) * r * 0.5)
            sy  = int(self.y + math.sin(ang) * r * 0.5)
            pygame.draw.line(surface, CYAN, pos, (sx, sy), 2)

        # Label
        label = fonts["tiny"].render("ESCAPE", True, CYAN)
        surface.blit(label, (int(self.x) - label.get_width() // 2, int(self.y) + r + 4))


# ─────────────────────────────────────────────────────────────────
# PARTICLE (sparkle on crystal collect)
# ─────────────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color):
        self.x        = x
        self.y        = y
        self.color    = color
        angle         = random.uniform(0, 2 * math.pi)
        speed         = random.uniform(1, 4)
        self.vx       = math.cos(angle) * speed
        self.vy       = math.sin(angle) * speed
        self.life     = random.randint(20, 40)
        self.max_life = self.life
        self.r        = random.randint(2, 5)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.05     # slight gravity
        self.life -= 1

    def is_dead(self):
        return self.life <= 0

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        size  = max(1, int(self.r * self.life / self.max_life))
        surf  = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (size, size), size)
        surface.blit(surf, (int(self.x) - size, int(self.y) - size))
