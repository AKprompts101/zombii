"""
Particle effects for hits and kills.
"""
import pygame
import random
import math
from settings import PARTICLE_COUNT, PARTICLE_SPEED, PARTICLE_LIFETIME


class Particle:
    """A single particle."""

    def __init__(self, x, y, color):
        self.pos = pygame.math.Vector2(x, y)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, PARTICLE_SPEED)
        self.vel = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        self.color = color
        self.size = random.randint(2, 5)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = PARTICLE_LIFETIME + random.randint(-50, 50)
        self.alive = True

    def update(self):
        """Move and fade."""
        self.pos += self.vel
        self.vel *= 0.95  # friction
        self.size = max(0, self.size - 0.05)
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.alive = False

    def draw(self, surface, camera_offset):
        """Draw the particle."""
        screen_x = int(self.pos.x - camera_offset.x)
        screen_y = int(self.pos.y - camera_offset.y)
        if 0 <= screen_x <= surface.get_width() and 0 <= screen_y <= surface.get_height():
            pygame.draw.circle(surface, self.color, (screen_x, screen_y), max(1, int(self.size)))


class ParticleManager:
    """Manages all active particles."""

    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=PARTICLE_COUNT):
        """Spawn a burst of particles."""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        """Update all particles and remove dead ones."""
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

    def draw(self, surface, camera_offset):
        """Draw all particles."""
        for p in self.particles:
            p.draw(surface, camera_offset)
