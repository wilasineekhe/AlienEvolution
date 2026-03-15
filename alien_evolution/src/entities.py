"""
entities.py
============================================================
All non-player game objects:

  Crystal       — collectible energy crystals
  PoisonCloud   — toxic gas zone (stationary or drifting)
  Drone         — bouncing security drone
  HunterDrone   — [NEW] stage 2+  locks onto player and chases
  LaserBeam     — [NEW] stage 2+  sweeping laser line
  BombMine      — [NEW] stage 3+  timed area explosion
  Portal        — escape portal (final stage win trigger)
  Particle      — sparkle / explosion particles

IMAGE tags mark every place a sprite can replace drawn shapes.
============================================================
"""

import pygame
import random
import math
from src.constants import (
    SCREEN_W, SCREEN_H,
    CYAN, PINK, WHITE, ORANGE, RED, GRAY, YELLOW, PURPLE
)
from src.utils  import draw_glow_circle
from src.assets import play_sfx


# ──────────────────────────────────────────────────────────
# CRYSTAL
# ──────────────────────────────────────────────────────────

class Crystal:
    TYPES = [
        ("Basic",    CYAN,           1,  8,  70),
        ("Rare",     PINK,           3, 11,  25),
        ("Evo Core", (255, 220, 50), 5, 14,   5),
    ]

    def __init__(self, assets: dict, avoid_x=None, avoid_y=None, avoid_r=0):
        self.assets = assets
        self.pulse  = random.uniform(0, 2 * math.pi)
        self.respawn(avoid_x, avoid_y, avoid_r)

    def respawn(self, avoid_x=None, avoid_y=None, avoid_r=0):
        from src.utils import dist
        for _ in range(50):
            x = random.randint(30, SCREEN_W - 30)
            y = random.randint(30, SCREEN_H - 30)
            if avoid_x is None or dist(x, y, avoid_x, avoid_y) > avoid_r + 40:
                self.x, self.y = x, y
                break
        else:
            self.x = random.randint(30, SCREEN_W - 30)
            self.y = random.randint(30, SCREEN_H - 30)

        weights = [t[4] for t in self.TYPES]
        total   = sum(weights)
        pick    = random.uniform(0, total)
        cumul   = 0
        self.type_idx = 0
        for i, w in enumerate(weights):
            cumul += w
            if pick <= cumul:
                self.type_idx = i
                break
        _, self.color, self.value, self.radius, _ = self.TYPES[self.type_idx]

    def update(self):
        self.pulse = (self.pulse + 0.07) % (2 * math.pi)

    def draw(self, surface):
        """
        IMAGE: CRYSTAL
        Replace with:
            img = self.assets.get("crystal")
            if img:
                size = self.radius * 2
                scaled = pygame.transform.scale(img, (size, size))
                surface.blit(scaled,
                             (int(self.x - self.radius),
                              int(self.y - self.radius)))
                return
        """
        pos = (int(self.x), int(self.y))
        r   = self.radius + int(math.sin(self.pulse) * 2)
        draw_glow_circle(surface, self.color, pos, r, layers=3)
        pts = [
            (self.x,     self.y - r),
            (self.x + r, self.y),
            (self.x,     self.y + r),
            (self.x - r, self.y),
        ]
        pygame.draw.polygon(surface, self.color,
                            [(int(p[0]), int(p[1])) for p in pts])
        pygame.draw.polygon(surface, WHITE,
                            [(int(p[0]), int(p[1])) for p in pts], 1)
        pygame.draw.circle(surface, WHITE,
                           (int(self.x - 2), int(self.y - 2)), max(1, r // 3))


# ──────────────────────────────────────────────────────────
# POISON CLOUD  (now supports slow drift)
# ──────────────────────────────────────────────────────────

class PoisonCloud:
    """
    Toxic gas cloud.
    stage < 3  → stationary
    stage >= 3 → drifts slowly and bounces off walls
    """

    def __init__(self, assets: dict,
                 player_x=SCREEN_W // 2, player_y=SCREEN_H // 2,
                 drifting=False):
        self.assets      = assets
        self.pulse       = random.uniform(0, 2 * math.pi)
        self.alpha_cycle = random.uniform(0, 2 * math.pi)
        self.drifting    = drifting
        self._spawn(player_x, player_y)

        # Drift velocity (only used when drifting=True)
        angle    = random.uniform(0, 2 * math.pi)
        speed    = random.uniform(0.4, 0.9)
        self.vx  = math.cos(angle) * speed
        self.vy  = math.sin(angle) * speed

    def _spawn(self, player_x, player_y):
        from src.utils import dist
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

        # DIFFICULTY 3: drifting clouds (stage 3+)
        if self.drifting:
            self.x += self.vx
            self.y += self.vy
            if self.x - self.radius < 0 or self.x + self.radius > SCREEN_W:
                self.vx *= -1
            if self.y - self.radius < 0 or self.y + self.radius > SCREEN_H:
                self.vy *= -1
            self.x = max(self.radius, min(SCREEN_W - self.radius, self.x))
            self.y = max(self.radius, min(SCREEN_H - self.radius, self.y))

    def draw(self, surface):
        """
        IMAGE: POISON
        Replace with:
            img = self.assets.get("poison")
            if img:
                alpha = int(140 + math.sin(self.alpha_cycle) * 40)
                temp  = img.copy()
                temp.set_alpha(alpha)
                size  = self.radius * 2
                scaled = pygame.transform.scale(temp, (size, size))
                surface.blit(scaled,
                             (int(self.x - self.radius),
                              int(self.y - self.radius)))
                return
        """
        pos   = (int(self.x), int(self.y))
        r     = self.radius + int(math.sin(self.pulse) * 4)
        alpha = int(140 + math.sin(self.alpha_cycle) * 40)

        for layer_r, layer_a in [(r, alpha), (r * 7 // 10, min(255, alpha + 40))]:
            s = pygame.Surface((layer_r * 2 + 4, layer_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (60, 200, 80, layer_a),
                               (layer_r + 2, layer_r + 2), layer_r)
            surface.blit(s, (pos[0] - layer_r - 2, pos[1] - layer_r - 2))

        pygame.draw.circle(surface, (30, 120, 40), pos, max(4, r // 4))

        # Small arrow indicator when drifting
        if self.drifting:
            ax = int(self.x + self.vx * 18)
            ay = int(self.y + self.vy * 18)
            pygame.draw.line(surface, (80, 255, 100), pos, (ax, ay), 2)


# ──────────────────────────────────────────────────────────
# DRONE  (original bouncing drone)
# ──────────────────────────────────────────────────────────

class Drone:
    """Bouncing security drone — travels diagonally, bounces off walls."""

    def __init__(self, assets: dict, speed=2.5):
        self.assets = assets
        self.x      = random.randint(60, SCREEN_W - 60)
        self.y      = random.randint(60, SCREEN_H - 60)
        angle       = random.uniform(0, 2 * math.pi)
        self.vx     = math.cos(angle) * speed
        self.vy     = math.sin(angle) * speed
        self.size   = 16
        self.pulse  = 0.0
        self.rage   = False   # True during Rage Mode (stage 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x - self.size < 0 or self.x + self.size > SCREEN_W:
            self.vx *= -1
        if self.y - self.size < 0 or self.y + self.size > SCREEN_H:
            self.vy *= -1
        self.x = max(self.size, min(SCREEN_W - self.size, self.x))
        self.y = max(self.size, min(SCREEN_H - self.size, self.y))
        self.pulse = (self.pulse + 0.08) % (2 * math.pi)

    def draw(self, surface):
        """
        IMAGE: DRONE
        Replace with:
            img = self.assets.get("drone")
            if img:
                size = self.size * 2
                scaled = pygame.transform.scale(img, (size, size))
                surface.blit(scaled,
                             (int(self.x - self.size),
                              int(self.y - self.size)))
                return
        """
        pos  = (int(self.x), int(self.y))
        s    = self.size
        col  = (255, 80, 0) if self.rage else RED
        draw_glow_circle(surface, col, pos, s, layers=3)
        rect = pygame.Rect(int(self.x - s), int(self.y - s), s * 2, s * 2)
        body = (200, 60, 0) if self.rage else (180, 20, 20)
        pygame.draw.rect(surface, body, rect, border_radius=4)
        pygame.draw.rect(surface, col,  rect, 2, border_radius=4)
        eye_r = max(3, s // 3)
        blink = int(math.sin(self.pulse * 3) * eye_r * 0.4)
        pygame.draw.circle(surface, (255, 80, 80), pos, eye_r + blink)
        pygame.draw.circle(surface, WHITE, pos, max(1, eye_r // 2))
        pygame.draw.line(surface, ORANGE,
                         (int(self.x - 5), int(self.y - s)),
                         (int(self.x - 5), int(self.y - s - 8)), 2)
        pygame.draw.line(surface, ORANGE,
                         (int(self.x + 5), int(self.y - s)),
                         (int(self.x + 5), int(self.y - s - 8)), 2)


# ──────────────────────────────────────────────────────────
# [NEW] DIFFICULTY 1: HUNTER DRONE  (stage 2+)
# ──────────────────────────────────────────────────────────

class HunterDrone:
    """
    ไล่ตามผู้เล่นตรงๆ ด้วย homing movement
    เคลื่อนที่ช้ากว่า Drone แต่หันหัวตามผู้เล่นตลอดเวลา
    stage 2 speed=1.8 / stage 3 speed=2.4 / stage 4 speed=3.2

    IMAGE: DRONE  (reuse drone sprite if desired)
    """

    def __init__(self, assets: dict, speed=1.8):
        self.assets    = assets
        self.x         = float(random.choice([60, SCREEN_W - 60]))
        self.y         = float(random.choice([60, SCREEN_H - 60]))
        self.speed     = speed
        self.size      = 18
        self.pulse     = random.uniform(0, 2 * math.pi)
        self.angle     = 0.0   # current facing angle (radians)
        self.trail     = []    # last N positions for motion trail

    def update(self, player_x, player_y):
        """Steer toward the player each frame."""
        dx = player_x - self.x
        dy = player_y - self.y
        length = math.sqrt(dx * dx + dy * dy) or 1
        self.angle = math.atan2(dy, dx)

        self.x += (dx / length) * self.speed
        self.y += (dy / length) * self.speed

        # Clamp to screen
        self.x = max(self.size, min(SCREEN_W - self.size, self.x))
        self.y = max(self.size, min(SCREEN_H - self.size, self.y))

        self.pulse = (self.pulse + 0.10) % (2 * math.pi)

        # Store trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 12:
            self.trail.pop(0)

    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        s   = self.size

        # Motion trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(60 * i / len(self.trail))
            r_t   = max(2, s * i // len(self.trail) // 2)
            ts = pygame.Surface((r_t * 2, r_t * 2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255, 40, 200, alpha), (r_t, r_t), r_t)
            surface.blit(ts, (tx - r_t, ty - r_t))

        # Glow
        draw_glow_circle(surface, (255, 0, 200), pos, s, layers=4)

        # Body — rotated triangle pointing toward player
        tip_x = int(self.x + math.cos(self.angle) * s)
        tip_y = int(self.y + math.sin(self.angle) * s)
        left_x = int(self.x + math.cos(self.angle + 2.4) * s * 0.7)
        left_y = int(self.y + math.sin(self.angle + 2.4) * s * 0.7)
        right_x = int(self.x + math.cos(self.angle - 2.4) * s * 0.7)
        right_y = int(self.y + math.sin(self.angle - 2.4) * s * 0.7)
        pygame.draw.polygon(surface, (180, 0, 160),
                            [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])
        pygame.draw.polygon(surface, (255, 80, 220),
                            [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)], 2)

        # Core
        eye_r = max(3, s // 4)
        blink = int(math.sin(self.pulse * 4) * 2)
        pygame.draw.circle(surface, (255, 0, 255), pos, eye_r + blink)


# ──────────────────────────────────────────────────────────
# [NEW] DIFFICULTY 2: LASER BEAM  (stage 2+)
# ──────────────────────────────────────────────────────────

class LaserBeam:
    """
    เลเซอร์ยิงข้ามจอ มี 3 phase:
      WARN  (1.5s) — เส้นสีแดงจางๆ เตือนว่าจะยิง
      FIRE  (0.4s) — เส้นสีขาวสว่างจ้า ทำ damage
      COOL  (1.0s) — หายไป รอ recharge

    ยิงตามแนว horizontal หรือ vertical สลับกัน
    """

    WARN_TIME = 120   # frames — 2 วิ เตือน (medium)
    FIRE_TIME = 20    # frames — สั้นลง ทำ damage น้อยลง
    COOL_TIME = 60    # frames

    def __init__(self, assets: dict):
        self.assets  = assets
        self._reset()

    def _reset(self):
        self.phase   = "WARN"
        self.timer   = self.WARN_TIME
        self.axis    = random.choice(["H", "V"])   # Horizontal / Vertical
        if self.axis == "H":
            self.pos = random.randint(60, SCREEN_H - 60)   # y position
        else:
            self.pos = random.randint(60, SCREEN_W - 60)   # x position
        self.active  = False   # True only during FIRE phase

    def update(self):
        self.timer -= 1
        if self.phase == "WARN" and self.timer <= 0:
            self.phase  = "FIRE"
            self.timer  = self.FIRE_TIME
            self.active = True
        elif self.phase == "FIRE" and self.timer <= 0:
            self.phase  = "COOL"
            self.timer  = self.COOL_TIME
            self.active = False
        elif self.phase == "COOL" and self.timer <= 0:
            self._reset()

    def hits_player(self, player_x, player_y, player_radius):
        """True if the player circle overlaps the live laser."""
        if not self.active:
            return False
        thickness = 12
        if self.axis == "H":
            return abs(player_y - self.pos) < player_radius + thickness // 2
        else:
            return abs(player_x - self.pos) < player_radius + thickness // 2

    def draw(self, surface):
        if self.phase == "WARN":
            # Dashed warning line
            alpha = int(80 + 80 * math.sin(self.timer * 0.15))
            warn_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            if self.axis == "H":
                pygame.draw.line(warn_surf, (255, 60, 60, alpha),
                                 (0, self.pos), (SCREEN_W, self.pos), 3)
                # Warning arrows
                for ax in range(30, SCREEN_W, 80):
                    pygame.draw.polygon(warn_surf, (255, 60, 60, alpha),
                                        [(ax, self.pos - 8),
                                         (ax + 12, self.pos),
                                         (ax, self.pos + 8)])
            else:
                pygame.draw.line(warn_surf, (255, 60, 60, alpha),
                                 (self.pos, 0), (self.pos, SCREEN_H), 3)
                for ay in range(30, SCREEN_H, 80):
                    pygame.draw.polygon(warn_surf, (255, 60, 60, alpha),
                                        [(self.pos - 8, ay),
                                         (self.pos, ay + 12),
                                         (self.pos + 8, ay)])
            surface.blit(warn_surf, (0, 0))

        elif self.phase == "FIRE":
            # Bright white/red beam with glow
            fade = self.timer / self.FIRE_TIME
            for thickness, col, a in [
                (28, (255, 60,  60),  int(60  * fade)),
                (12, (255, 140, 140), int(120 * fade)),
                (4,  (255, 255, 255), int(255 * fade)),
            ]:
                beam = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                if self.axis == "H":
                    pygame.draw.line(beam, (*col, a),
                                     (0, self.pos), (SCREEN_W, self.pos), thickness)
                else:
                    pygame.draw.line(beam, (*col, a),
                                     (self.pos, 0), (self.pos, SCREEN_H), thickness)
                surface.blit(beam, (0, 0))


# ──────────────────────────────────────────────────────────
# [NEW] DIFFICULTY 4: BOMB MINE  (stage 3+)
# ──────────────────────────────────────────────────────────

class BombMine:
    """
    วางระเบิดนิ่งๆ ที่จุดสุ่ม นับถอยหลัง 3 วินาที แล้วระเบิด
    ถ้าผู้เล่นอยู่ในรัศมีระเบิด → เสีย HP

    หลังระเบิดแล้วรอ RESPAWN_TIME วินาที แล้ว spawn ใหม่
    """

    FUSE_TIME    = 300   # frames — 5 วิ (medium, ง่ายกว่าเดิม)
    EXPLODE_TIME = 30    # frames explosion visible
    RESPAWN_TIME = 180   # frames before next bomb appears
    BLAST_RADIUS = 60    # pixel radius (medium — เล็กลงจาก 70)

    def __init__(self, assets: dict, player_x=400, player_y=300, lifetime=None):
        self.assets  = assets
        self._place(player_x, player_y)
        self.fuse    = self.FUSE_TIME
        self.phase   = "ARMED"   # ARMED → EXPLODING → WAITING
        self.exp_timer  = 0
        self.wait_timer = 0
        self.pulse   = 0.0

    def _place(self, px, py):
        from src.utils import dist
        for _ in range(50):
            x = random.randint(60, SCREEN_W - 60)
            y = random.randint(60, SCREEN_H - 60)
            if dist(x, y, px, py) > 100:
                self.x, self.y = x, y
                return
        self.x = random.randint(60, SCREEN_W - 60)
        self.y = random.randint(60, SCREEN_H - 60)

    def update(self, player_x, player_y):
        """Returns True at the moment of explosion (so Game can deal damage)."""
        self.pulse = (self.pulse + 0.12) % (2 * math.pi)
        just_exploded = False

        if self.phase == "ARMED":
            self.fuse -= 1
            if self.fuse <= 0:
                self.phase     = "EXPLODING"
                self.exp_timer = self.EXPLODE_TIME
                just_exploded  = True

        elif self.phase == "EXPLODING":
            self.exp_timer -= 1
            if self.exp_timer <= 0:
                self.phase      = "WAITING"
                self.wait_timer = self.RESPAWN_TIME

        elif self.phase == "WAITING":
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                self._place(player_x, player_y)
                self.fuse  = self.FUSE_TIME
                self.phase = "ARMED"

        return just_exploded

    def in_blast_radius(self, px, py, player_radius):
        from src.utils import dist
        return dist(px, py, self.x, self.y) < self.BLAST_RADIUS + player_radius

    def draw(self, surface):
        if self.phase == "WAITING":
            return

        pos = (int(self.x), int(self.y))

        if self.phase == "ARMED":
            # Urgency: blinks faster as fuse counts down
            fuse_ratio = self.fuse / self.FUSE_TIME
            blink_speed = 0.06 + (1 - fuse_ratio) * 0.30
            self.pulse  = (self.pulse + blink_speed) % (2 * math.pi)
            glow_alpha  = int(100 + 155 * abs(math.sin(self.pulse)))
            r           = 14

            # Danger zone preview ring (fades in as fuse burns)
            ring_alpha = int(40 * (1 - fuse_ratio))
            ring_surf = pygame.Surface((self.BLAST_RADIUS * 2 + 4,
                                        self.BLAST_RADIUS * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 80, 0, ring_alpha),
                               (self.BLAST_RADIUS + 2, self.BLAST_RADIUS + 2),
                               self.BLAST_RADIUS, 2)
            surface.blit(ring_surf,
                         (pos[0] - self.BLAST_RADIUS - 2,
                          pos[1] - self.BLAST_RADIUS - 2))

            # Body
            glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 80, 0, glow_alpha),
                               (r * 2, r * 2), r + 4)
            surface.blit(glow_surf, (pos[0] - r * 2, pos[1] - r * 2))
            pygame.draw.circle(surface, (60, 20, 0),  pos, r)
            pygame.draw.circle(surface, (255, 100, 0), pos, r, 2)

            # Countdown number
            secs = max(0, int(math.ceil(self.fuse / 60)))
            font = pygame.font.SysFont("Consolas", 14, bold=True)
            txt  = font.render(str(secs), True,
                               (255, 255, 0) if secs > 1 else (255, 40, 40))
            surface.blit(txt, (pos[0] - txt.get_width() // 2,
                               pos[1] - txt.get_height() // 2))

        elif self.phase == "EXPLODING":
            # Expanding blast ring
            fade  = self.exp_timer / self.EXPLODE_TIME
            blast_r = int(self.BLAST_RADIUS * (1 - fade) + 20)
            for rad, col, alp in [
                (blast_r + 20, (255, 140, 0), int(80 * fade)),
                (blast_r,      (255, 60,  0), int(160 * fade)),
                (blast_r // 2, (255, 220, 80), int(220 * fade)),
            ]:
                es = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(es, (*col, alp), (rad + 2, rad + 2), rad)
                surface.blit(es, (pos[0] - rad - 2, pos[1] - rad - 2))


# ──────────────────────────────────────────────────────────
# ESCAPE PORTAL
# ──────────────────────────────────────────────────────────

class Portal:
    def __init__(self, assets: dict):
        self.assets = assets
        self.x      = random.randint(80, SCREEN_W - 80)
        self.y      = random.randint(80, SCREEN_H - 80)
        self.radius = 32
        self.spin   = 0.0
        self.pulse  = 0.0
        # SOUND: PORTAL_OPEN
        play_sfx(assets.get("sfx_portal"))

    def update(self):
        self.spin  = (self.spin  + 0.05) % (2 * math.pi)
        self.pulse = (self.pulse + 0.06) % (2 * math.pi)

    def draw(self, surface):
        """
        IMAGE: PORTAL
        Replace with:
            img = self.assets.get("portal")
            if img:
                size = self.radius * 2
                angle = math.degrees(self.spin)
                rotated = pygame.transform.rotate(
                    pygame.transform.scale(img, (size, size)), angle)
                surface.blit(rotated,
                             (int(self.x - size // 2),
                              int(self.y - size // 2)))
                return
        """
        pos = (int(self.x), int(self.y))
        r   = self.radius + int(math.sin(self.pulse) * 5)
        draw_glow_circle(surface, CYAN, pos, r + 10, layers=6)
        for i in range(12):
            angle = self.spin + i * (2 * math.pi / 12)
            dx = int(self.x + math.cos(angle) * (r + 6))
            dy = int(self.y + math.sin(angle) * (r + 6))
            col = (0, 200 + int(math.sin(angle + self.spin) * 55), 255)
            pygame.draw.circle(surface, col, (dx, dy), 4)
        pygame.draw.circle(surface, (0, 30, 60), pos, r)
        pygame.draw.circle(surface, CYAN, pos, r, 3)
        for i in range(3):
            a  = self.spin * 2 + i * (2 * math.pi / 3)
            sx = int(self.x + math.cos(a) * r * 0.5)
            sy = int(self.y + math.sin(a) * r * 0.5)
            pygame.draw.line(surface, CYAN, pos, (sx, sy), 2)
        lbl = pygame.font.SysFont("Consolas", 14).render("ESCAPE", True, CYAN)
        surface.blit(lbl, (int(self.x) - lbl.get_width() // 2, int(self.y) + r + 4))


# ──────────────────────────────────────────────────────────
# PARTICLE
# ──────────────────────────────────────────────────────────

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
        self.vy  += 0.05
        self.life -= 1

    def is_dead(self):
        return self.life <= 0

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        size  = max(1, int(self.r * self.life / self.max_life))
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
        surface.blit(s, (int(self.x) - size, int(self.y) - size))


def spawn_particles(particles: list, x, y, color, count=12):
    for _ in range(count):
        particles.append(Particle(x, y, color))


# ──────────────────────────────────────────────────────────
# HEALTH ORB  — เก็บแล้ว +1 HP (ไม่เกิน max_hp)
# ──────────────────────────────────────────────────────────

class HealthOrb:
    """
    ไอเทมเก็บ HP สีเขียว/ชมพู วางบนแมพ
    เมื่อเก็บ → +1 HP (ไม่เกิน max_hp)

    spawn_interval  — วินาทีก่อน spawn ครั้งแรก
    Orb จะหายไปเองใน LIFETIME วินาที ถ้าไม่ถูกเก็บ

    IMAGE: HealthOrb
        img = self.assets.get("hp_orb")
        if img:
            scaled = pygame.transform.scale(img, (r*2, r*2))
            surface.blit(scaled, (int(self.x - r), int(self.y - r)))
            return
    """

    LIFETIME = 8 * 60   # 8 วินาที แล้วหายไป

    def __init__(self, assets: dict, player_x=400, player_y=300, lifetime=None):
        self.assets  = assets
        self.radius  = 12
        self.pulse   = 0.0
        self.life    = lifetime if lifetime is not None else self.LIFETIME
        self._place(player_x, player_y)

    def _place(self, px, py):
        from src.utils import dist
        for _ in range(60):
            x = random.randint(40, SCREEN_W - 40)
            y = random.randint(40, SCREEN_H - 40)
            if dist(x, y, px, py) > 80:
                self.x, self.y = float(x), float(y)
                return
        self.x = random.randint(40, SCREEN_W - 40)
        self.y = random.randint(40, SCREEN_H - 40)

    def update(self):
        """Returns True เมื่อหมดอายุ (ให้ Game ลบออก)"""
        self.pulse = (self.pulse + 0.09) % (2 * math.pi)
        self.life -= 1
        return self.life <= 0

    def is_collected(self, px, py, player_radius):
        from src.utils import dist
        return dist(px, py, self.x, self.y) < player_radius + self.radius

    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        r   = self.radius + int(math.sin(self.pulse) * 3)

        # กระพริบเร็วขึ้นตอนใกล้หมดอายุ
        if self.life < 120:
            blink_speed = 0.06 + (1 - self.life / 120) * 0.20
            self.pulse  = (self.pulse + blink_speed) % (2 * math.pi)
            if self.life < 60 and (self.life // 8) % 2 == 0:
                return   # กระพริบหายตอนจวนหมด

        # Glow สีเขียวนีออน
        glow_surf = pygame.Surface((r * 4 + 8, r * 4 + 8), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            alpha = int(50 * i / 4)
            pygame.draw.circle(glow_surf, (80, 255, 160, alpha),
                               (r * 2 + 4, r * 2 + 4), r + i * 5)
        surface.blit(glow_surf, (pos[0] - r * 2 - 4, pos[1] - r * 2 - 4))

        # Body — วงกลมสีเขียวอ่อน
        pygame.draw.circle(surface, (30, 60, 40), pos, r)
        pygame.draw.circle(surface, (80, 255, 160), pos, r, 2)

        # Cross / plus ข้างใน (สัญลักษณ์ HP)
        cross_len = r - 3
        col = (120, 255, 180)
        pygame.draw.line(surface, col,
                         (pos[0], pos[1] - cross_len),
                         (pos[0], pos[1] + cross_len), 2)
        pygame.draw.line(surface, col,
                         (pos[0] - cross_len, pos[1]),
                         (pos[0] + cross_len, pos[1]), 2)

        # "+1" label เล็กๆ ด้านบน
        font = pygame.font.SysFont("Consolas", 11, bold=True)
        txt  = font.render("+HP", True, (160, 255, 200))
        surface.blit(txt, (pos[0] - txt.get_width() // 2, pos[1] - r - 14))


# ──────────────────────────────────────────────────────────
# ARMOR ORB  — เก็บแล้วได้เกราะป้องกัน 1 ชั้น
# เกราะดูดซับดาเมจ 1 ครั้งก่อนที่ HP จะลด
# ──────────────────────────────────────────────────────────

class ArmorOrb:
    """
    ไอเทมสีฟ้า/เงิน เก็บแล้วได้เกราะ 1 ชั้น
    เกราะสูงสุด 3 ชั้น  ถ้าเต็มแล้วจะไม่ spawn ใหม่

    เกราะทำงานอย่างไร:
      - โดนตี → เกราะหายไป 1 ชั้นก่อน  HP ไม่ลด
      - เกราะ 0 → HP ลดตามปกติ

    IMAGE: ArmorOrb
        img = self.assets.get("armor_orb")
        if img:
            scaled = pygame.transform.scale(img, (r*2, r*2))
            surface.blit(scaled, (int(self.x - r), int(self.y - r)))
            return
    """

    MAX_ARMOR   = 3       # เกราะสูงสุด 3 ชั้น
    LIFETIME    = 12 * 60 # 12 วินาที แล้วหายไป

    def __init__(self, assets: dict, player_x=400, player_y=300, lifetime=None):
        self.assets = assets
        self.radius = 13
        self.pulse  = random.uniform(0, 2 * math.pi)
        self.spin   = 0.0
        self.life   = lifetime if lifetime is not None else self.LIFETIME
        self._place(player_x, player_y)

    def _place(self, px, py):
        from src.utils import dist
        for _ in range(60):
            x = random.randint(40, SCREEN_W - 40)
            y = random.randint(40, SCREEN_H - 40)
            if dist(x, y, px, py) > 90:
                self.x, self.y = float(x), float(y)
                return
        self.x = random.randint(40, SCREEN_W - 40)
        self.y = random.randint(40, SCREEN_H - 40)

    def is_collected(self, px, py, player_radius):
        from src.utils import dist
        return dist(px, py, self.x, self.y) < player_radius + self.radius

    def draw(self, surface):
        # กะพริบเร็วตอนใกล้หมดอายุ
        if self.life < 60 and (self.life // 6) % 2 == 0:
            return

        pos = (int(self.x), int(self.y))
        r   = self.radius + int(math.sin(self.pulse) * 3)

        # Glow สีฟ้าเงิน
        for i in range(4, 0, -1):
            alpha = int(45 * i / 4)
            gs = pygame.Surface((r * 4 + 8, r * 4 + 8), pygame.SRCALPHA)
            pygame.draw.circle(gs, (80, 180, 255, alpha),
                               (r * 2 + 4, r * 2 + 4), r + i * 5)
            surface.blit(gs, (pos[0] - r * 2 - 4, pos[1] - r * 2 - 4))

        # Body
        pygame.draw.circle(surface, (10, 30, 60), pos, r)
        pygame.draw.circle(surface, (100, 200, 255), pos, r, 2)

        # วงแหวนหมุน (สัญลักษณ์เกราะ)
        num_dots = 6
        for i in range(num_dots):
            angle = self.spin + i * (2 * math.pi / num_dots)
            dx = int(self.x + math.cos(angle) * (r - 3))
            dy = int(self.y + math.sin(angle) * (r - 3))
            pygame.draw.circle(surface, (160, 220, 255), (dx, dy), 2)

        # โล่ข้างใน
        shield_pts = []
        for i in range(6):
            a = self.spin * 0.5 + i * math.pi / 3
            shield_pts.append((
                int(self.x + math.cos(a) * (r * 0.55)),
                int(self.y + math.sin(a) * (r * 0.55))
            ))
        if len(shield_pts) >= 3:
            pygame.draw.polygon(surface, (60, 140, 220), shield_pts, 2)

        # "+ARM" label
        font = pygame.font.SysFont("Consolas", 11, bold=True)
        txt  = font.render("+ARM", True, (160, 220, 255))
        surface.blit(txt, (pos[0] - txt.get_width() // 2, pos[1] - r - 14))
