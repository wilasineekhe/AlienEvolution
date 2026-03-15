"""
game.py  — v5  MEDIUM difficulty
============================================================
ปรับระดับ "กลาง" — ชนะได้แน่ถ้าระวัง ไม่ตายง่ายเกินไป

สรุปการปรับทั้งหมดจาก v4:
────────────────────────────────────────────────────────────
  ผู้เล่น
    HP เริ่มต้น       5 → 7         (ทนมากขึ้น)
    Invincibility     60 → 90 frames (grace period นานขึ้น)

  Stage 1 — เหมือนเดิม แค่ drone ช้าลง
    Drone speed       2.2 → 1.8
    Poison clouds     2   → 2  (เท่าเดิม)

  Stage 2 — ลด hunter ออก 1 ตัว, laser เตือนนานขึ้น
    Hunter speed      1.6 → 1.4
    Laser warn time   100 → 120 frames (2 วิ)
    Laser fire time   24  → 20 frames  (สั้นลง ตีน้อยลง)
    เพิ่ม poison      1   → ไม่เพิ่ม poison ตอน stage 2

  Stage 3 — bomb ช้าลง, drifting poison แค่ 1 ก้อน
    Hunter speed      2.0 → 1.7
    Bomb fuse         240 → 300 frames (5 วิ)
    Bomb blast radius 70  → 60
    Drifting poison   2   → 1 ก้อน

  Stage 4 — rage น้อยลง, drone ไม่เพิ่ม
    Rage interval     12  → 18 วิ
    Rage duration     3   → 2.5 วิ
    Rage multiplier   1.8 → 1.5
    Hunter speed      2.8 → 2.3
    ไม่ spawn drone เพิ่ม (เหลือ 1 ตัวเดิม)

  HealthOrb
    Spawn interval    20/15/10/8 วิ → 12/10/8/6 วิ  (บ่อยขึ้นทุก stage)
    Orb lifetime      8 วิ → 10 วิ  (เก็บได้นานขึ้น)
    Max orbs on map   2   → 3       (โอกาสเห็นบนแมพมากขึ้น)
    spawn แม้ HP เต็ม  ไม่  → ยังไม่ spawn ตอน HP เต็ม (เหมือนเดิม)
============================================================
"""

import pygame
import math
import random

from src.constants import DIFF_PORTAL_SCORE, PORTAL_CRYSTAL_GOAL, STAGES
from src.player    import Player
from src.entities  import (Crystal, PoisonCloud, Drone, HunterDrone,
                            LaserBeam, BombMine, Portal, HealthOrb,
                            ArmorOrb, spawn_particles)
from src.hud       import draw_hud
from src.utils     import draw_grid, dist
from src.assets    import play_sfx

# ── Rage Mode ─────────────────────────────────────────────
RAGE_INTERVAL   = 25 * 60   # ทุก 25 วิ (ลดจาก 18 — stage 4 พอดี)
RAGE_DURATION   = int(2.5 * 60)  # นาน 2.5 วิ
RAGE_MULTIPLIER = 1.3        # ×1.3 (ลดจาก 1.5 — ไม่เร็วเกินจนหนีไม่ทัน)

# ── HealthOrb spawn interval ตาม stage (วินาที) ──────────
HP_ORB_INTERVAL  = {0: 12, 1: 10, 2: 8, 3: 5}  # stage 4 orb ทุก 5 วิ
HP_ORB_MAX_MAP   = 3     # orb บนแมพได้พร้อมกันสูงสุด 3 ลูก
HP_ORB_LIFETIME  = 10 * 60  # 10 วิ

# ── ArmorOrb spawn interval ตาม stage (วินาที) ───────────
ARMOR_ORB_INTERVAL = {0: 30, 1: 22, 2: 16, 3: 12}  # หายากกว่า HP orb
ARMOR_ORB_LIFETIME = 12 * 60  # 12 วิ


class Game:
    def __init__(self, assets: dict, fonts: dict):
        self.assets = assets
        self.fonts  = fonts
        self.reset()

    def reset(self):
        self.player   = Player(self.assets, start_hp=7)   # HP เริ่มต้น 7
        self.crystals = [Crystal(self.assets) for _ in range(4)]
        self.poisons  = [PoisonCloud(self.assets) for _ in range(2)]
        self.drones   = [Drone(self.assets, speed=1.8)]   # ช้าลง
        self.hunters  = []
        self.lasers   = []
        self.bombs    = []
        self.hp_orbs    = []
        self.armor_orbs = []

        self.portal      = None
        self.particles   = []
        self.start_ticks = pygame.time.get_ticks()
        self.end_ticks   = None

        self.rage_timer  = RAGE_INTERVAL
        self.rage_active = False
        self.rage_dur    = 0
        self.rage_flash  = 0

        self._hp_orb_timer    = HP_ORB_INTERVAL[0] * 60
        self._armor_orb_timer = ARMOR_ORB_INTERVAL[0] * 60
        self._last_stage      = 0

        # SOUND: MUSIC
        # pygame.mixer.music.play(-1)

    # ── Timer ─────────────────────────────────────────────

    def elapsed_seconds(self) -> float:
        stop = self.end_ticks if self.end_ticks is not None else pygame.time.get_ticks()
        return (stop - self.start_ticks) / 1000.0

    def freeze_timer(self):
        if self.end_ticks is None:
            self.end_ticks = pygame.time.get_ticks()

    # ── Stage spawning ────────────────────────────────────

    def _spawn_for_stage(self, stage):
        px, py = self.player.x, self.player.y

        if stage == 1:
            # Stage 2: Hunter ช้า + Laser เตือนนาน
            self.hunters.append(HunterDrone(self.assets, speed=1.4))
            self.lasers.append(LaserBeam(self.assets))
            # ไม่เพิ่ม poison เพิ่ม (มี 2 อยู่แล้ว)

        elif stage == 2:
            # Stage 3: Poison drift 1 ก้อน + Bomb + Hunter อีก 1
            self.poisons.append(PoisonCloud(self.assets, px, py, drifting=True))
            self.bombs.append(BombMine(self.assets, px, py))
            self.hunters.append(HunterDrone(self.assets, speed=1.7))
            self.lasers.append(LaserBeam(self.assets))

        elif stage == 3:
            # Stage 4: Hunter เร็วขึ้น + Bomb เพิ่ม (ไม่เพิ่ม drone)
            self.hunters.append(HunterDrone(self.assets, speed=1.8))  # stage 4 hunter — ช้าลงจาก 2.3
            # ไม่เพิ่ม Bomb ใน stage 4 — มี 1 ตัวจาก stage 3 พอแล้ว
            # Rage Mode จะ kick in อัตโนมัติ

        # อัปเดต HP + Armor orb interval
        self._hp_orb_timer    = HP_ORB_INTERVAL[stage] * 60
        self._armor_orb_timer = ARMOR_ORB_INTERVAL[stage] * 60

    # ── HealthOrb ─────────────────────────────────────────

    def _update_hp_orbs(self):
        # หมดอายุ
        self.hp_orbs = [o for o in self.hp_orbs
                        if not self._tick_orb(o)]

        # Spawn
        self._hp_orb_timer -= 1
        if self._hp_orb_timer <= 0:
            self._hp_orb_timer = HP_ORB_INTERVAL[self.player.stage] * 60
            if (self.player.hp < self.player.max_hp
                    and len(self.hp_orbs) < HP_ORB_MAX_MAP):
                self.hp_orbs.append(
                    HealthOrb(self.assets,
                              self.player.x, self.player.y,
                              lifetime=HP_ORB_LIFETIME))

    def _tick_orb(self, orb):
        """Tick orb lifetime. Returns True if expired."""
        orb.life -= 1
        orb.pulse = (orb.pulse + 0.09) % (2 * 3.14159)
        return orb.life <= 0

    # ── ArmorOrb ──────────────────────────────────────────

    def _update_armor_orbs(self):
        """
        spawn ArmorOrb ทุก N วิ
        ไม่ spawn ถ้าเกราะเต็ม (3 ชั้น) หรือมี orb บนแมพ 2 ลูกแล้ว
        """
        player = self.player

        # tick lifetime + remove expired
        alive = []
        for orb in self.armor_orbs:
            orb.life -= 1
            orb.pulse = (orb.pulse + 0.08) % (2 * 3.14159)
            orb.spin  = (orb.spin  + 0.05) % (2 * 3.14159)
            if orb.life > 0:
                alive.append(orb)
        self.armor_orbs = alive

        # spawn
        self._armor_orb_timer -= 1
        if self._armor_orb_timer <= 0:
            self._armor_orb_timer = ARMOR_ORB_INTERVAL[player.stage] * 60
            if (player.armor < player.max_armor
                    and len(self.armor_orbs) < 2):
                self.armor_orbs.append(
                    ArmorOrb(self.assets, player.x, player.y,
                             lifetime=ARMOR_ORB_LIFETIME))

    # ── Rage Mode ─────────────────────────────────────────

    def _update_rage(self):
        if self.player.stage < 3:
            return
        if not self.rage_active:
            self.rage_timer -= 1
            if self.rage_timer <= 0:
                self.rage_active = True
                self.rage_dur    = RAGE_DURATION
                self.rage_flash  = 15
                for d in self.drones:
                    d.vx *= RAGE_MULTIPLIER
                    d.vy *= RAGE_MULTIPLIER
                    d.rage = True
        else:
            self.rage_dur -= 1
            if self.rage_flash > 0:
                self.rage_flash -= 1
            if self.rage_dur <= 0:
                self.rage_active = False
                self.rage_timer  = RAGE_INTERVAL
                for d in self.drones:
                    d.vx /= RAGE_MULTIPLIER
                    d.vy /= RAGE_MULTIPLIER
                    d.rage = False

    # ── Update ────────────────────────────────────────────

    def update(self):
        player = self.player
        keys   = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        # Evolution check
        if player.stage > self._last_stage:
            self._spawn_for_stage(player.stage)
            self._last_stage = player.stage

        # Crystals
        for crystal in self.crystals:
            crystal.update()
            if dist(player.x, player.y, crystal.x, crystal.y) < player.radius + crystal.radius:
                play_sfx(self.assets.get("sfx_collect"))
                spawn_particles(self.particles,
                                int(crystal.x), int(crystal.y),
                                crystal.color, count=14)
                player.score         += crystal.value
                player.crystals_total += 1
                if player.stage == 3:          # นับเฉพาะตอน Ultimate Alien
                    player.crystals_stage4 += 1
                player.check_evolution()
                crystal.respawn(player.x, player.y, player.radius)

        # Poison
        for poison in self.poisons:
            poison.update()
            if dist(player.x, player.y, poison.x, poison.y) < player.radius + poison.radius - 4:
                player.take_damage()

        # Drones
        for drone in self.drones:
            drone.update()
            if dist(player.x, player.y, drone.x, drone.y) < player.radius + drone.size:
                player.take_damage()

        # Hunters
        for hunter in self.hunters:
            hunter.update(player.x, player.y)
            if dist(player.x, player.y, hunter.x, hunter.y) < player.radius + hunter.size:
                player.take_damage()

        # Lasers
        for laser in self.lasers:
            laser.update()
            if laser.hits_player(player.x, player.y, player.radius):
                player.take_damage()

        # Bombs
        for bomb in self.bombs:
            just_exploded = bomb.update(player.x, player.y)
            if just_exploded and bomb.in_blast_radius(player.x, player.y, player.radius):
                player.take_damage()
                spawn_particles(self.particles,
                                int(bomb.x), int(bomb.y),
                                (255, 120, 0), count=30)

        # HealthOrb — update lifetime + collect
        self._update_hp_orbs()
        collected = [o for o in self.hp_orbs
                     if o.is_collected(player.x, player.y, player.radius)]
        for orb in collected:
            self.hp_orbs.remove(orb)
            player.hp = min(player.max_hp, player.hp + 1)
            spawn_particles(self.particles,
                            int(orb.x), int(orb.y),
                            (80, 255, 160), count=18)
            play_sfx(self.assets.get("sfx_collect"))

        # ArmorOrb — update + collect
        self._update_armor_orbs()
        collected_armor = [o for o in self.armor_orbs
                           if o.is_collected(player.x, player.y, player.radius)]
        for orb in collected_armor:
            self.armor_orbs.remove(orb)
            player.armor = min(player.max_armor, player.armor + 1)
            spawn_particles(self.particles,
                            int(orb.x), int(orb.y),
                            (80, 180, 255), count=18)
            play_sfx(self.assets.get("sfx_collect"))

        # Rage
        self._update_rage()

        # Portal — เปิดเมื่อเก็บ crystal ครบ PORTAL_CRYSTAL_GOAL ชิ้นใน stage 4
        if (player.stage == 3
                and player.crystals_stage4 >= PORTAL_CRYSTAL_GOAL
                and self.portal is None):
            self.portal = Portal(self.assets)
        if self.portal:
            self.portal.update()
            if dist(player.x, player.y, self.portal.x, self.portal.y) < player.radius + self.portal.radius:
                player.escaped = True
                play_sfx(self.assets.get("sfx_win"))

        # Particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]

    # ── Draw ──────────────────────────────────────────────

    def draw(self, surface):
        draw_grid(surface)

        if self.rage_flash > 0:
            fs = pygame.Surface((surface.get_width(), surface.get_height()),
                                 pygame.SRCALPHA)
            fs.fill((255, 0, 0, int(60 * self.rage_flash / 15)))
            surface.blit(fs, (0, 0))

        for obj in self.poisons:   obj.draw(surface)
        for obj in self.crystals:  obj.draw(surface)
        for obj in self.lasers:    obj.draw(surface)
        for obj in self.bombs:     obj.draw(surface)
        for obj in self.hp_orbs:   obj.draw(surface)
        for obj in self.armor_orbs: obj.draw(surface)
        if self.portal:            self.portal.draw(surface)
        for obj in self.drones:    obj.draw(surface)
        for obj in self.hunters:   obj.draw(surface)

        self.player.draw(surface)
        for p in self.particles:   p.draw(surface)

        if self.rage_active:
            self._draw_rage_banner(surface)

        draw_hud(surface, self.player, self.fonts, self.elapsed_seconds(),
                 hp_orbs_on_map=len(self.hp_orbs),
                 armor_orbs_on_map=len(self.armor_orbs))

    def _draw_rage_banner(self, surface):
        tick = pygame.time.get_ticks()
        if (tick // 200) % 2 == 0:
            font  = pygame.font.SysFont("Consolas", 24, bold=True)
            txt   = font.render("RAGE MODE", True, (255, 100, 0))
            x     = surface.get_width() // 2 - txt.get_width() // 2
            surface.blit(txt, (x, 14))
            bar_w = int(240 * self.rage_dur / RAGE_DURATION)
            bar_x = surface.get_width() // 2 - 120
            pygame.draw.rect(surface, (50, 10, 0),   (bar_x, 42, 240, 7), border_radius=3)
            pygame.draw.rect(surface, (255, 100, 0), (bar_x, 42, bar_w, 7), border_radius=3)
            pygame.draw.rect(surface, (255, 160, 0), (bar_x, 42, 240, 7), 1, border_radius=3)
