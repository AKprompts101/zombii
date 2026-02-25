"""
Weapon system - handles shooting logic with spread and multi-bullet.
"""
import math
import random
import pygame
from settings import WEAPONS
from bullet import Bullet


def fire_weapon(player, assets):
    """Fire the player's current weapon, returning a list of Bullet sprites."""
    if not player.can_shoot():
        return []

    player.shoot()
    weapon = WEAPONS[player.current_weapon]
    bullets = []

    base_angle = player.angle
    bullet_surface = assets.get(f"bullet_{player.current_weapon}")

    for _ in range(weapon["bullets_per_shot"]):
        # Apply spread
        spread = random.uniform(-weapon["spread"], weapon["spread"])
        angle = base_angle + spread

        # Spawn bullet at player's position offset toward aim direction
        offset_dist = 25
        rad = math.radians(angle)
        bx = player.pos.x + math.cos(rad) * offset_dist
        by = player.pos.y - math.sin(rad) * offset_dist

        bullet = Bullet(bx, by, angle, player.current_weapon, bullet_surface)
        bullets.append(bullet)

    return bullets
