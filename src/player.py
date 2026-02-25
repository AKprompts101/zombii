"""
Player entity - movement, rotation, health, and weapon management.
"""
import pygame
import math
from settings import *


class Player(pygame.sprite.Sprite):
    """Player sprite with WASD movement, mouse aiming, and weapon switching."""

    def __init__(self, x, y, asset_surface, difficulty):
        super().__init__()
        self.original_image = asset_surface
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.angle = 0
        self.speed = PLAYER_SPEED

        # Health
        self.max_hp = difficulty["player_hp"]
        self.hp = self.max_hp

        # Weapon
        self.current_weapon = "pistol"
        self.weapons_list = ["pistol", "shotgun", "rifle"]
        self.ammo = {
            "pistol": WEAPONS["pistol"]["mag_size"],
            "shotgun": WEAPONS["shotgun"]["mag_size"],
            "rifle": WEAPONS["rifle"]["mag_size"],
        }
        self.last_shot_time = 0
        self.reloading = False
        self.reload_start = 0

        # Score
        self.score = 0
        self.kills = 0

    @property
    def weapon(self):
        return WEAPONS[self.current_weapon]

    def handle_input(self, camera):
        """Handle movement and aiming."""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.pos.x += dx
        self.pos.y += dy

        # Clamp to world
        self.pos.x = max(PLAYER_SIZE, min(self.pos.x, WORLD_WIDTH - PLAYER_SIZE))
        self.pos.y = max(PLAYER_SIZE, min(self.pos.y, WORLD_HEIGHT - PLAYER_SIZE))

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Aim toward mouse (world position)
        mouse_screen = pygame.mouse.get_pos()
        mouse_world = camera.reverse(mouse_screen)
        rel_x = mouse_world[0] - self.pos.x
        rel_y = mouse_world[1] - self.pos.y
        self.angle = math.degrees(math.atan2(-rel_y, rel_x))

        # Rotate image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Weapon switching
        if keys[pygame.K_1]:
            self.switch_weapon("pistol")
        elif keys[pygame.K_2]:
            self.switch_weapon("shotgun")
        elif keys[pygame.K_3]:
            self.switch_weapon("rifle")

    def switch_weapon(self, weapon_name):
        """Switch to a different weapon."""
        if weapon_name != self.current_weapon:
            self.current_weapon = weapon_name
            self.reloading = False

    def can_shoot(self):
        """Check if player can fire."""
        now = pygame.time.get_ticks()
        if self.reloading:
            if now - self.reload_start >= self.weapon["reload_time"]:
                self.ammo[self.current_weapon] = self.weapon["mag_size"]
                self.reloading = False
            else:
                return False

        if self.ammo[self.current_weapon] <= 0:
            self.start_reload()
            return False

        if now - self.last_shot_time < self.weapon["fire_rate"]:
            return False

        return True

    def shoot(self):
        """Consume ammo and mark shot time."""
        self.ammo[self.current_weapon] -= 1
        self.last_shot_time = pygame.time.get_ticks()

    def start_reload(self):
        """Begin reload timer."""
        if not self.reloading and self.ammo[self.current_weapon] < self.weapon["mag_size"]:
            self.reloading = True
            self.reload_start = pygame.time.get_ticks()

    def take_damage(self, amount):
        """Receive damage."""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True  # dead
        return False

    def heal(self, amount):
        """Heal player."""
        self.hp = min(self.max_hp, self.hp + amount)

    def update(self, camera):
        """Update player per frame."""
        self.handle_input(camera)
