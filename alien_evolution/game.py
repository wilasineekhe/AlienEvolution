"""
game.py
=======
The Game class owns all gameplay objects, runs the game loop logic,
handles collisions, difficulty scaling, and draws each frame.
"""

import pygame

from settings import (
    DIFF_ADD_POISON, DIFF_SPEED_DRONE, DIFF_ADD_DRONE, DIFF_PORTAL_SCORE
)
from entities import Player, Crystal, PoisonCloud, Drone, Portal
from utils    import dist, spawn_particles, play_sfx, draw_grid
from hud      import draw_hud


class Game:
    def __init__(self, sounds, fonts, images):
        self.sounds = sounds
        self.fonts  = fonts
        self.images = images
        self.reset()

    def reset(self):
        """Initialise (or restart) all game objects."""
        self.player    = Player()
        self.crystals  = [Crystal() for _ in range(4)]
        self.poisons   = [PoisonCloud() for _ in range(2)]
        self.drones    = [Drone(speed=2.5)]
        self.portal    = None
        self.particles = []
        self.start_ticks          = pygame.time.get_ticks()
        self.score_milestones_hit = set()   # prevents re-triggering events

        # SOUND: MUSIC — restart background music each new game
        pygame.mixer.music.play(-1)

    def elapsed_seconds(self):
        """Return how many seconds have passed since the game started."""
        return (pygame.time.get_ticks() - self.start_ticks) / 1000.0

    # ── Difficulty ────────────────────────────────────────────────

    def difficulty_scaling(self):
        """
        Trigger difficulty increases at specific score thresholds.
        All thresholds are defined in settings.py so they are easy to change.
        """
        score = self.player.score

        # Extra poison cloud
        if score >= DIFF_ADD_POISON and DIFF_ADD_POISON not in self.score_milestones_hit:
            self.score_milestones_hit.add(DIFF_ADD_POISON)
            self.poisons.append(PoisonCloud(self.player.x, self.player.y))

        # Speed up existing drones
        if score >= DIFF_SPEED_DRONE and DIFF_SPEED_DRONE not in self.score_milestones_hit:
            self.score_milestones_hit.add(DIFF_SPEED_DRONE)
            for d in self.drones:
                d.vx *= 1.4
                d.vy *= 1.4

        # Second drone
        if score >= DIFF_ADD_DRONE and DIFF_ADD_DRONE not in self.score_milestones_hit:
            self.score_milestones_hit.add(DIFF_ADD_DRONE)
            self.drones.append(Drone(speed=3.5))

        # Spawn escape portal at final stage
        if (score >= DIFF_PORTAL_SCORE
                and self.portal is None
                and self.player.stage == 3):
            self.portal = Portal(sounds=self.sounds)

    # ── Update ────────────────────────────────────────────────────

    def update(self):
        """Master update — called every frame while the game is running."""
        player = self.player
        keys   = pygame.key.get_pressed()

        # Player movement
        player.handle_input(keys)
        player.update()

        # Crystal collection
        for crystal in self.crystals:
            crystal.update()
            if dist(player.x, player.y, crystal.x, crystal.y) < player.radius + crystal.radius:
                # SOUND: COLLECT
                play_sfx(self.sounds, "collect")
                spawn_particles(self.particles, int(crystal.x), int(crystal.y),
                                crystal.color, count=14)
                player.score += crystal.value
                player.check_evolution(self.sounds)
                crystal.respawn(player.x, player.y, player.radius)

        # Poison cloud damage
        for poison in self.poisons:
            poison.update()
            if dist(player.x, player.y, poison.x, poison.y) < player.radius + poison.radius - 4:
                player.take_damage(self.sounds)

        # Drone collision damage
        for drone in self.drones:
            drone.update()
            if dist(player.x, player.y, drone.x, drone.y) < player.radius + drone.size:
                player.take_damage(self.sounds)

        # Portal touch → win
        if self.portal:
            self.portal.update()
            if dist(player.x, player.y, self.portal.x, self.portal.y) < player.radius + self.portal.radius:
                player.escaped = True
                # SOUND: WIN
                play_sfx(self.sounds, "win")

        # Particle updates (remove dead ones)
        self.particles = [p for p in self.particles if not p.is_dead()]
        for p in self.particles:
            p.update()

        # Difficulty events
        self.difficulty_scaling()

    # ── Draw ──────────────────────────────────────────────────────

    def draw(self, surface):
        """Draw everything for one gameplay frame."""
        draw_grid(surface, self.images)

        for poison in self.poisons:
            poison.draw(surface, self.images)

        for crystal in self.crystals:
            crystal.draw(surface, self.images)

        if self.portal:
            self.portal.draw(surface, self.fonts, self.images)

        for drone in self.drones:
            drone.draw(surface, self.images)

        self.player.draw(surface, self.images)

        for p in self.particles:
            p.draw(surface)

        draw_hud(surface, self.player, self.elapsed_seconds(), self.fonts)
