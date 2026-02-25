"""
Zombie entity - chases the player, scales with difficulty.
"""
import pygame
import math
import random
from settings import *


class Zombie(pygame.sprite.Sprite):
    """Zombie that chases the player. Type determines stats."""

    def __init__(self, x, y, zombie_type, asset_surface, difficulty):
        super().__init__()
        self.zombie_type = zombie_type
        self.type_info = ZOMBIE_TYPES[zombie_type]
        self.original_image = asset_surface
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)

        # Stats scaled by difficulty
        base_speed = difficulty["zombie_speed"]
        self.speed = base_speed * self.type_info["speed_mult"]
        self.max_hp = difficulty["zombie_hp"] * self.type_info["hp_mult"]
        self.hp = self.max_hp
        self.damage = difficulty["damage_per_hit"] * self.type_info["damage_mult"]
        self.score_value = self.type_info["score"]

        # Attack cooldown
        self.attack_cooldown = 800  # ms between attacks
        self.last_attack = 0

        # Movement wobble for natural feel
        self.wobble_offset = random.uniform(-0.5, 0.5)
        self.wobble_timer = random.uniform(0, math.pi * 2)

    def update(self, player_pos):
        """Move toward the player."""
        # Direction to player
        direction = player_pos - self.pos
        dist = direction.length()

        if dist > 0:
            direction = direction.normalize()

            # Add slight wobble
            self.wobble_timer += 0.05
            wobble = math.sin(self.wobble_timer) * self.wobble_offset
            perpendicular = pygame.math.Vector2(-direction.y, direction.x)
            move = direction + perpendicular * wobble
            if move.length() > 0:
                move = move.normalize()

            self.pos += move * self.speed
            self.rect.center = (int(self.pos.x), int(self.pos.y))

            # Rotate toward player
            angle = math.degrees(math.atan2(-direction.y, direction.x))
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def can_attack(self):
        """Check attack cooldown."""
        now = pygame.time.get_ticks()
        if now - self.last_attack >= self.attack_cooldown:
            self.last_attack = now
            return True
        return False

    def take_damage(self, amount):
        """Take damage, return True if dead."""
        self.hp -= amount
        return self.hp <= 0

    def draw_health_bar(self, surface, camera):
        """Draw health bar above zombie if damaged."""
        if self.hp >= self.max_hp:
            return
        screen_rect = camera.apply(self)
        bar_width = self.type_info["size"]
        bar_height = 4
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - 8

        # Background
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        # Health fill
        fill = max(0, (self.hp / self.max_hp) * bar_width)
        color = HEALTH_GREEN if self.hp / self.max_hp > 0.5 else RED
        pygame.draw.rect(surface, color, (bar_x, bar_y, int(fill), bar_height))


def spawn_zombie(player_pos, difficulty, assets):
    """Spawn a zombie at a random position away from the player."""
    # Pick zombie type by weight
    types = list(ZOMBIE_TYPES.keys())
    weights = [ZOMBIE_TYPES[t]["weight"] for t in types]
    zombie_type = random.choices(types, weights=weights, k=1)[0]

    # Spawn at random edge position, away from player
    min_dist = 400
    max_dist = 800
    angle = random.uniform(0, math.pi * 2)
    dist = random.uniform(min_dist, max_dist)
    x = player_pos.x + math.cos(angle) * dist
    y = player_pos.y + math.sin(angle) * dist

    # Clamp to world
    x = max(20, min(x, WORLD_WIDTH - 20))
    y = max(20, min(y, WORLD_HEIGHT - 20))

    surface = assets.get(f"zombie_{zombie_type}")
    return Zombie(x, y, zombie_type, surface, difficulty)
