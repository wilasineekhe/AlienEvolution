"""
player.py
============================================================
Player class — the alien organism the user controls.

Stats, movement, damage, evolution, and drawing all live
here.  Edit STAGES in constants.py to change evolution.

IMAGE: PLAYER
  To use sprites instead of drawn circles, find the
  draw() method below and follow the instructions there.
============================================================
"""

import pygame
import math
from src.constants import SCREEN_W, SCREEN_H, STAGES, WHITE, YELLOW, CYAN, PORTAL_CRYSTAL_GOAL
from src.utils     import draw_glow_circle
from src.assets    import play_sfx


class Player:
    def __init__(self, assets: dict, start_hp: int = 7):
        """
        assets — the dict returned by assets.load_assets()
                 stored here so draw() can use sprites.
        """
        self.assets = assets

        # ── Position ──────────────────────────────────────
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2

        # ── Stats ─────────────────────────────────────────
        self.stage    = 0
        self._apply_stage_stats()
        self.hp       = start_hp
        self.max_hp   = start_hp
        self.score    = 0
        self.is_alive = True
        self.escaped  = False

        # ── Timers / animation state ───────────────────────
        self.armor            = 0    # จำนวนเกราะ (0-3)
        self.crystals_total   = 0    # crystal ที่เก็บทั้งหมด (ทุก stage)
        self.crystals_stage4  = 0    # crystal ที่เก็บตอน stage 4 (เพื่อเปิด portal)
        self.max_armor        = 3    # เกราะสูงสุด 3 ชั้น
        self.armor_flash      = 0    # frames ของ shield flash เมื่อโดนตี
        self.invincible_timer = 0    # frames of post-hit invincibility
        self.evolve_flash     = 0    # frames of evolution glow ring
        self.pulse            = 0.0  # sine oscillator for body pulse

    # ── Internal helpers ──────────────────────────────────

    def _apply_stage_stats(self):
        """Copy radius/speed/colours from the STAGES table."""
        _, _, self.radius, self.speed, \
            self.body_color, self.glow_color, self.pulse_color = STAGES[self.stage]

    # ── Input / movement ──────────────────────────────────

    def handle_input(self, keys):
        """
        Translate keyboard state into movement.
        Supports WASD and Arrow keys.
        Diagonal movement is normalised to prevent speed boost.
        """
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += self.speed

        # Normalise diagonal so speed stays constant
        if dx != 0 and dy != 0:
            factor = self.speed / math.sqrt(dx * dx + dy * dy)
            dx *= factor
            dy *= factor

        # Clamp to screen boundaries
        self.x = max(self.radius, min(SCREEN_W - self.radius, self.x + dx))
        self.y = max(self.radius, min(SCREEN_H - self.radius, self.y + dy))

    # ── Evolution ─────────────────────────────────────────

    def check_evolution(self):
        """
        Compare score against STAGES thresholds.
        Evolves to highest unlocked stage.
        Returns True if a new stage was reached.
        """
        new_stage = 0
        for i, (_, threshold, *_rest) in enumerate(STAGES):
            if self.score >= threshold:
                new_stage = i

        if new_stage > self.stage:
            self.stage = new_stage
            self._apply_stage_stats()
            self.evolve_flash = 90        # ~1.5 s at 60 fps
            # SOUND: EVOLVE
            play_sfx(self.assets.get("sfx_evolve"))
            return True
        return False

    # ── Health ────────────────────────────────────────────

    def take_damage(self):
        """
        ถ้ามีเกราะ → เกราะลด 1 ชั้น HP ไม่ลด  flash สีฟ้า
        ถ้าไม่มีเกราะ → HP ลด 1  flash สีแดง
        ทั้งคู่ใช้ invincibility timer เหมือนกัน
        """
        if self.invincible_timer > 0:
            return
        if self.armor > 0:
            self.armor -= 1
            self.armor_flash  = 20   # flash สีฟ้าสั้นๆ
            self.invincible_timer = 90
            # SOUND: HIT (armor hit)
            play_sfx(self.assets.get("sfx_hit"))
        else:
            self.hp -= 1
            self.invincible_timer = 90
            # SOUND: HIT
            play_sfx(self.assets.get("sfx_hit"))
            if self.hp <= 0:
                self.is_alive = False

    # ── Per-frame update ──────────────────────────────────

    def update(self):
        """Tick all animation/invincibility timers."""
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.armor_flash > 0:
            self.armor_flash -= 1
        if self.evolve_flash > 0:
            self.evolve_flash -= 1
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)

    # ── Drawing ───────────────────────────────────────────

    def draw(self, surface):
        """
        Draw the alien.

        IMAGE: PLAYER
        -------------------------------------------------------
        To use sprite images replace the body-drawing block
        (marked below) with:

            img_list = self.assets.get("player")   # list of 4 images
            if img_list:
                size = self.radius * 2
                img  = pygame.transform.scale(img_list[self.stage], (size, size))
                surface.blit(img, (int(self.x - self.radius),
                                   int(self.y - self.radius)))
            else:
                # fallback: draw circle (keep the code below)
                ...
        -------------------------------------------------------
        """
        if not self.is_alive:
            return

        # Blink rapidly while invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return

        pos    = (int(self.x), int(self.y))
        pulse_r = self.radius + int(math.sin(self.pulse) * 3)

        # ── Glow halo ─────────────────────────────────────
        glow_col = self.glow_color if self.evolve_flash == 0 else (255, 255, 120)
        draw_glow_circle(surface, glow_col, pos, pulse_r, layers=5)

        # ── Body circle ───────────────────────────────────
        # IMAGE: PLAYER — replace these three draw calls with sprite blit
        pygame.draw.circle(surface, self.body_color, pos, pulse_r)

        # Inner highlight ring
        inner_pos = (int(self.x - self.radius * 0.2),
                     int(self.y - self.radius * 0.2))
        pygame.draw.circle(surface, WHITE, inner_pos, max(4, self.radius // 3), 2)

        # Nucleus dot
        pygame.draw.circle(surface, self.pulse_color, pos, self.radius // 4)

        # ── Armor shield ring ─────────────────────────────
        if self.armor > 0:
            shield_r = pulse_r + 8 + self.armor * 3
            shield_alpha = 120 + int(math.sin(self.pulse * 2) * 40)
            for layer in range(self.armor):
                lr = shield_r - layer * 4
                ss = pygame.Surface((lr * 2 + 4, lr * 2 + 4), pygame.SRCALPHA)
                a  = max(40, shield_alpha - layer * 30)
                pygame.draw.circle(ss, (80, 180, 255, a),
                                   (lr + 2, lr + 2), lr, 2)
                surface.blit(ss, (int(self.x) - lr - 2, int(self.y) - lr - 2))

        # Armor flash (สีฟ้าสว่างตอนโดนตีแต่เกราะรับ)
        if self.armor_flash > 0:
            af    = self.armor_flash
            af_r  = pulse_r + 14
            af_s  = pygame.Surface((af_r * 2 + 4, af_r * 2 + 4), pygame.SRCALPHA)
            af_al = int(200 * af / 20)
            pygame.draw.circle(af_s, (100, 200, 255, af_al),
                               (af_r + 2, af_r + 2), af_r, 4)
            surface.blit(af_s, (int(self.x) - af_r - 2, int(self.y) - af_r - 2))

        # ── Evolution flash ring ───────────────────────────
        if self.evolve_flash > 0:
            alpha  = min(255, self.evolve_flash * 3)
            ring_r = self.radius + (90 - self.evolve_flash) // 2
            ring_size = ring_r * 4
            ring_surf = pygame.Surface((ring_size, ring_size), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*YELLOW, alpha),
                               (ring_r * 2, ring_r * 2), ring_r, 3)
            surface.blit(ring_surf,
                         (int(self.x) - ring_r * 2, int(self.y) - ring_r * 2))
