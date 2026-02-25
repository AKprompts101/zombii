"""
Bullet entity - projectile fired by the player.
"""
import pygame
import math
from settings import *


class Bullet(pygame.sprite.Sprite):
    """A bullet that travels in a straight line."""

    def __init__(self, x, y, angle_deg, weapon_name, asset_surface):
        super().__init__()
        self.image = asset_surface
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)

        weapon = WEAPONS[weapon_name]
        self.speed = weapon["bullet_speed"]
        self.damage = weapon["damage"]

        # Convert angle to radians and get velocity
        angle_rad = math.radians(angle_deg)
        self.velocity = pygame.math.Vector2(
            math.cos(angle_rad) * self.speed,
            -math.sin(angle_rad) * self.speed,
        )

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000  # ms before auto-destroy

    def update(self):
        """Move bullet and check lifetime."""
        self.pos += self.velocity
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Remove if out of world or too old
        now = pygame.time.get_ticks()
        if (
            self.pos.x < -50
            or self.pos.x > WORLD_WIDTH + 50
            or self.pos.y < -50
            or self.pos.y > WORLD_HEIGHT + 50
            or now - self.spawn_time > self.lifetime
        ):
            self.kill()
