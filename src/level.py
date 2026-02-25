"""
Wave / level management system.
"""
import pygame
from settings import *


class LevelManager:
    """Manages waves of zombies."""

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.wave = 0
        self.zombies_spawned = 0
        self.zombies_to_spawn = 0
        self.zombies_killed = 0
        self.wave_active = False
        self.wave_complete = False
        self.wave_announce_time = 0
        self.announce_duration = 2000  # ms to show wave announcement
        self.last_spawn_time = 0
        self.between_waves = True
        self.between_wave_start = pygame.time.get_ticks()
        self.between_wave_duration = 3000  # 3s break

        # Start first wave
        self._start_next_wave()

    def _start_next_wave(self):
        """Initialize the next wave."""
        self.wave += 1
        self.zombies_to_spawn = (
            self.difficulty["zombies_per_wave_base"]
            + (self.wave - 1) * self.difficulty["wave_growth"]
        )
        self.zombies_spawned = 0
        self.zombies_killed = 0
        self.wave_active = True
        self.wave_complete = False
        self.wave_announce_time = pygame.time.get_ticks()
        self.between_waves = False

    def should_spawn(self, current_zombie_count):
        """Check if it's time to spawn a new zombie."""
        if not self.wave_active or self.between_waves:
            return False

        now = pygame.time.get_ticks()

        # Don't spawn during wave announcement
        if now - self.wave_announce_time < self.announce_duration:
            return False

        # Check spawn cooldown
        if now - self.last_spawn_time < self.difficulty["spawn_interval"]:
            return False

        # Check if we have more to spawn and haven't hit max
        if (
            self.zombies_spawned < self.zombies_to_spawn
            and current_zombie_count < self.difficulty["max_zombies"]
        ):
            self.last_spawn_time = now
            self.zombies_spawned += 1
            return True

        return False

    def on_zombie_killed(self, current_zombie_count):
        """Call when a zombie dies."""
        self.zombies_killed += 1

        # Wave complete when all spawned zombies are killed
        if self.zombies_killed >= self.zombies_to_spawn and current_zombie_count <= 1:
            self.wave_active = False
            self.wave_complete = True
            self.between_waves = True
            self.between_wave_start = pygame.time.get_ticks()

    def update(self):
        """Check for wave transitions."""
        if self.between_waves and self.wave_complete:
            now = pygame.time.get_ticks()
            if now - self.between_wave_start >= self.between_wave_duration:
                self._start_next_wave()

    def is_announcing(self):
        """Check if we're in the wave announcement phase."""
        return (
            self.wave_active
            and pygame.time.get_ticks() - self.wave_announce_time < self.announce_duration
        )

    def get_wave_text(self):
        """Get current wave announcement text."""
        return f"WAVE {self.wave}"

    def get_zombies_remaining(self):
        """Get how many zombies are left in this wave."""
        return max(0, self.zombies_to_spawn - self.zombies_killed)
