"""
Game settings, constants, and difficulty configurations.
"""
import pygame

# ─── Display ───────────────────────────────────────────────
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "🧟 ZOMBII - Zombie Shooter"

# ─── World ─────────────────────────────────────────────────
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
TILE_SIZE = 64

# ─── Colors ────────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (139, 0, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 80, 0)
YELLOW = (255, 215, 0)
BLUE = (30, 100, 200)
DARK_BLUE = (20, 60, 140)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY = (40, 40, 40)
DARKER_GRAY = (25, 25, 25)
ORANGE = (255, 140, 0)
PURPLE = (128, 0, 200)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 50, 50)
BLOOD_RED = (138, 7, 7)
BG_COLOR = (30, 30, 30)

# ─── UI Colors ─────────────────────────────────────────────
MENU_BG = (15, 15, 25)
MENU_ACCENT = (200, 50, 50)
BUTTON_COLOR = (50, 50, 70)
BUTTON_HOVER = (70, 70, 100)
HEALTH_GREEN = (50, 205, 50)
HEALTH_RED = (220, 20, 60)
HUD_BG = (0, 0, 0, 150)

# ─── Player ────────────────────────────────────────────────
PLAYER_SIZE = 40
PLAYER_SPEED = 4

# ─── Zombie Types ──────────────────────────────────────────
ZOMBIE_TYPES = {
    "normal": {
        "color": (50, 160, 50),
        "size": 36,
        "hp_mult": 1.0,
        "speed_mult": 1.0,
        "damage_mult": 1.0,
        "score": 100,
        "weight": 60,  # spawn weight
    },
    "fast": {
        "color": (220, 200, 30),
        "size": 30,
        "hp_mult": 0.6,
        "speed_mult": 1.8,
        "damage_mult": 0.7,
        "score": 150,
        "weight": 25,
    },
    "tank": {
        "color": (200, 40, 40),
        "size": 48,
        "hp_mult": 3.0,
        "speed_mult": 0.6,
        "damage_mult": 2.0,
        "score": 300,
        "weight": 15,
    },
}

# ─── Weapons ───────────────────────────────────────────────
WEAPONS = {
    "pistol": {
        "name": "Pistol",
        "damage": 25,
        "fire_rate": 250,      # ms between shots
        "bullet_speed": 12,
        "spread": 3,           # degrees of spread
        "bullets_per_shot": 1,
        "mag_size": 15,
        "reload_time": 1000,   # ms
        "color": YELLOW,
    },
    "shotgun": {
        "name": "Shotgun",
        "damage": 15,
        "fire_rate": 600,
        "bullet_speed": 10,
        "spread": 20,
        "bullets_per_shot": 5,
        "mag_size": 8,
        "reload_time": 1800,
        "color": ORANGE,
    },
    "rifle": {
        "name": "Rifle",
        "damage": 50,
        "fire_rate": 150,
        "bullet_speed": 16,
        "spread": 1,
        "bullets_per_shot": 1,
        "mag_size": 30,
        "reload_time": 2000,
        "color": (0, 200, 255),
    },
}

# ─── Difficulty Configurations ─────────────────────────────
DIFFICULTIES = {
    "easy": {
        "label": "EASY",
        "color": HEALTH_GREEN,
        "description": "Relaxed pace, fewer zombies",
        "zombie_speed": 1.0,
        "spawn_interval": 3000,   # ms between spawns
        "zombie_hp": 1,
        "max_zombies": 10,
        "player_hp": 200,
        "damage_per_hit": 10,
        "zombies_per_wave_base": 5,
        "wave_growth": 3,
    },
    "medium": {
        "label": "MEDIUM",
        "color": YELLOW,
        "description": "Balanced challenge",
        "zombie_speed": 2.0,
        "spawn_interval": 2000,
        "zombie_hp": 2,
        "max_zombies": 20,
        "player_hp": 150,
        "damage_per_hit": 20,
        "zombies_per_wave_base": 8,
        "wave_growth": 4,
    },
    "hard": {
        "label": "HARD",
        "color": RED,
        "description": "Fast and deadly hordes",
        "zombie_speed": 3.5,
        "spawn_interval": 1000,
        "zombie_hp": 3,
        "max_zombies": 35,
        "player_hp": 100,
        "damage_per_hit": 30,
        "zombies_per_wave_base": 12,
        "wave_growth": 6,
    },
    "extreme": {
        "label": "EXTREME HARD",
        "color": PURPLE,
        "description": "Relentless nightmare swarm",
        "zombie_speed": 5.0,
        "spawn_interval": 500,
        "zombie_hp": 5,
        "max_zombies": 50,
        "player_hp": 75,
        "damage_per_hit": 40,
        "zombies_per_wave_base": 18,
        "wave_growth": 10,
    },
}

# ─── Particles ─────────────────────────────────────────────
PARTICLE_COUNT = 8
PARTICLE_SPEED = 4
PARTICLE_LIFETIME = 300  # ms

# ─── Obstacles ─────────────────────────────────────────────
OBSTACLE_TYPES = {
    "barricade": {"width": 80, "height": 30, "weight": 30},
    "car":       {"width": 100, "height": 55, "weight": 15},
    "crate":     {"width": 40, "height": 40, "weight": 25},
    "concrete_wall": {"width": 60, "height": 60, "weight": 15},
    "sandbag":   {"width": 70, "height": 35, "weight": 15},
}
OBSTACLE_COUNT = 40          # Total obstacles in the world
OBSTACLE_MIN_DIST = 120       # Min distance between obstacles
COVER_DAMAGE_REDUCTION = 0.8  # 80% damage blocked when behind cover

# ─── Game States ───────────────────────────────────────────
STATE_MENU = "menu"
STATE_DIFFICULTY = "difficulty"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

