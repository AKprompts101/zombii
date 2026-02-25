"""
Procedural asset generator - creates all game sprites with detailed, realistic pixel art.
Includes obstacle generation. No external image files needed.
"""
import pygame
import math
import random
from settings import *


# ═══════════════════════════════════════════════════════════
#  PLAYER SPRITE — detailed human soldier (top-down)
# ═══════════════════════════════════════════════════════════

def create_player_surface(size=PLAYER_SIZE):
    """Create a detailed top-down soldier sprite facing right."""
    s = size
    surf = pygame.Surface((s, s), pygame.SRCALPHA)

    # ── Legs (behind body) ──
    leg_color = (50, 60, 50)        # dark cargo pants
    leg_highlight = (65, 75, 60)
    # Left leg
    pygame.draw.ellipse(surf, leg_color, (s*0.22, s*0.60, s*0.18, s*0.30))
    pygame.draw.ellipse(surf, leg_highlight, (s*0.24, s*0.62, s*0.14, s*0.26))
    # Right leg
    pygame.draw.ellipse(surf, leg_color, (s*0.22, s*0.10, s*0.18, s*0.30))
    pygame.draw.ellipse(surf, leg_highlight, (s*0.24, s*0.12, s*0.14, s*0.26))

    # Boot tips
    boot_color = (35, 30, 25)
    pygame.draw.ellipse(surf, boot_color, (s*0.15, s*0.65, s*0.12, s*0.14))
    pygame.draw.ellipse(surf, boot_color, (s*0.15, s*0.20, s*0.12, s*0.14))

    # ── Body / torso (tactical vest) ──
    vest_color = (45, 70, 45)       # olive green vest
    vest_dark = (35, 55, 35)
    vest_light = (60, 85, 55)
    body_rect = pygame.Rect(s*0.25, s*0.18, s*0.40, s*0.64)
    pygame.draw.rect(surf, vest_dark, body_rect, border_radius=6)
    pygame.draw.rect(surf, vest_color, body_rect.inflate(-3, -3), border_radius=5)

    # Vest pouches / detail
    pouch_color = (55, 75, 50)
    pygame.draw.rect(surf, pouch_color, (s*0.30, s*0.28, s*0.10, s*0.12), border_radius=2)
    pygame.draw.rect(surf, pouch_color, (s*0.30, s*0.60, s*0.10, s*0.12), border_radius=2)
    # Vest seam line
    pygame.draw.line(surf, vest_dark, (int(s*0.45), int(s*0.22)), (int(s*0.45), int(s*0.78)), 1)
    # Shoulder straps
    pygame.draw.line(surf, vest_light, (int(s*0.28), int(s*0.20)), (int(s*0.35), int(s*0.30)), 2)
    pygame.draw.line(surf, vest_light, (int(s*0.28), int(s*0.78)), (int(s*0.35), int(s*0.68)), 2)

    # ── Arms ──
    skin = (195, 160, 130)          # skin tone
    sleeve_color = (50, 65, 45)
    # Back arm (lower)
    pygame.draw.line(surf, sleeve_color, (int(s*0.45), int(s*0.72)), (int(s*0.62), int(s*0.72)), 5)
    pygame.draw.circle(surf, skin, (int(s*0.62), int(s*0.72)), 4)  # hand
    # Front arm holding gun
    pygame.draw.line(surf, sleeve_color, (int(s*0.48), int(s*0.35)), (int(s*0.70), int(s*0.42)), 5)
    pygame.draw.circle(surf, skin, (int(s*0.70), int(s*0.42)), 4)  # hand

    # ── Gun (assault rifle) ──
    gun_body = (55, 50, 45)
    gun_dark = (35, 32, 28)
    gun_metal = (100, 95, 90)
    # Stock
    pygame.draw.line(surf, gun_body, (int(s*0.52), int(s*0.45)), (int(s*0.62), int(s*0.45)), 4)
    # Barrel
    pygame.draw.line(surf, gun_dark, (int(s*0.62), int(s*0.45)), (int(s*0.95), int(s*0.45)), 3)
    # Muzzle
    pygame.draw.circle(surf, gun_metal, (int(s*0.95), int(s*0.45)), 2)
    # Magazine
    pygame.draw.rect(surf, gun_dark, (int(s*0.60), int(s*0.47), int(s*0.06), int(s*0.10)))
    # Scope bump
    pygame.draw.rect(surf, gun_metal, (int(s*0.66), int(s*0.42), int(s*0.08), int(s*0.04)), border_radius=1)

    # ── Head ──
    head_cx, head_cy = int(s * 0.42), int(s * 0.50)
    head_r = int(s * 0.13)
    # Helmet
    helmet_color = (60, 75, 55)
    helmet_dark = (45, 55, 40)
    pygame.draw.circle(surf, helmet_dark, (head_cx, head_cy), head_r + 2)
    pygame.draw.circle(surf, helmet_color, (head_cx, head_cy), head_r)
    # Helmet band
    pygame.draw.arc(surf, (80, 95, 70), (head_cx - head_r, head_cy - head_r, head_r*2, head_r*2),
                    -0.5, 0.5, 2)
    # Face visible from the right
    face_color = (200, 165, 135)
    pygame.draw.circle(surf, face_color, (head_cx + 3, head_cy), head_r - 3)
    # Eye
    pygame.draw.circle(surf, (40, 40, 40), (head_cx + 6, head_cy - 2), 2)
    pygame.draw.circle(surf, WHITE, (head_cx + 6, head_cy - 2), 1)

    return surf


# ═══════════════════════════════════════════════════════════
#  ZOMBIE SPRITES — detailed undead characters (top-down)
# ═══════════════════════════════════════════════════════════

def create_zombie_surface(zombie_type="normal"):
    """Create a detailed top-down zombie sprite."""
    z_info = ZOMBIE_TYPES[zombie_type]
    s = z_info["size"]
    base_color = z_info["color"]
    dark = tuple(max(0, c - 60) for c in base_color)
    light = tuple(min(255, c + 30) for c in base_color)
    rot_color = tuple(max(0, c - 30) for c in base_color)  # rotting flesh tint

    surf = pygame.Surface((s, s), pygame.SRCALPHA)

    # ── Legs (shambling) ──
    pant_color = (60, 50, 40) if zombie_type != "fast" else (70, 60, 30)
    pant_torn = (45, 38, 30)
    # Left leg (dragged back for shambling feel)
    pygame.draw.ellipse(surf, pant_color, (s*0.18, s*0.58, s*0.20, s*0.30))
    pygame.draw.line(surf, pant_torn, (int(s*0.22), int(s*0.75)), (int(s*0.32), int(s*0.80)), 2)
    # Right leg
    pygame.draw.ellipse(surf, pant_color, (s*0.18, s*0.12, s*0.20, s*0.30))
    # Torn fabric
    pygame.draw.line(surf, pant_torn, (int(s*0.20), int(s*0.25)), (int(s*0.28), int(s*0.18)), 1)

    # ── Body / torso (torn, bloody shirt) ──
    shirt_color = rot_color
    shirt_dark = dark
    body_rect = pygame.Rect(s*0.22, s*0.16, s*0.42, s*0.68)
    pygame.draw.rect(surf, shirt_dark, body_rect, border_radius=5)
    pygame.draw.rect(surf, shirt_color, body_rect.inflate(-3, -3), border_radius=4)

    # Blood stains on chest
    blood = (120, 15, 10)
    blood_light = (160, 25, 15)
    pygame.draw.circle(surf, blood, (int(s*0.38), int(s*0.45)), int(s*0.06))
    pygame.draw.circle(surf, blood_light, (int(s*0.50), int(s*0.60)), int(s*0.04))
    pygame.draw.circle(surf, blood, (int(s*0.35), int(s*0.65)), int(s*0.03))
    # Torn shirt lines
    pygame.draw.line(surf, shirt_dark, (int(s*0.30), int(s*0.30)), (int(s*0.40), int(s*0.38)), 1)
    pygame.draw.line(surf, shirt_dark, (int(s*0.42), int(s*0.55)), (int(s*0.55), int(s*0.50)), 1)

    # ── Arms (reaching forward, clawed hands) ──
    flesh = tuple(max(0, c - 20) for c in base_color)
    # Upper arms
    pygame.draw.line(surf, flesh, (int(s*0.48), int(s*0.20)), (int(s*0.78), int(s*0.12)), 5)
    pygame.draw.line(surf, flesh, (int(s*0.48), int(s*0.78)), (int(s*0.78), int(s*0.85)), 5)
    # Clawed hands
    claw_color = (80, 70, 50)
    for dy in [-3, 0, 3]:
        pygame.draw.line(surf, claw_color, (int(s*0.78), int(s*0.12+dy)),
                        (int(s*0.88), int(s*0.10+dy)), 2)
        pygame.draw.line(surf, claw_color, (int(s*0.78), int(s*0.85+dy)),
                        (int(s*0.88), int(s*0.83+dy)), 2)

    # Wound / exposed bone on arm
    pygame.draw.circle(surf, blood, (int(s*0.62), int(s*0.18)), 3)

    # ── Head ──
    head_cx, head_cy = int(s * 0.40), int(s * 0.50)
    head_r = int(s * 0.14)
    head_color = tuple(max(0, min(255, c + 10)) for c in base_color)
    jaw_color = tuple(max(0, c - 40) for c in head_color)

    # Head shape
    pygame.draw.circle(surf, dark, (head_cx, head_cy), head_r + 1)
    pygame.draw.circle(surf, head_color, (head_cx, head_cy), head_r)

    # Sunken, glowing eyes
    eye_glow = (255, 40, 20) if zombie_type != "fast" else (255, 220, 30)
    eye_dark = (180, 20, 10) if zombie_type != "fast" else (200, 160, 20)
    pygame.draw.circle(surf, eye_dark, (head_cx + 4, head_cy - 4), 4)
    pygame.draw.circle(surf, eye_glow, (head_cx + 4, head_cy - 4), 2)
    pygame.draw.circle(surf, eye_dark, (head_cx + 4, head_cy + 4), 4)
    pygame.draw.circle(surf, eye_glow, (head_cx + 4, head_cy + 4), 2)
    # Pupil shine
    pygame.draw.circle(surf, (255, 200, 180), (head_cx + 5, head_cy - 4), 1)
    pygame.draw.circle(surf, (255, 200, 180), (head_cx + 5, head_cy + 4), 1)

    # Mouth (open, showing teeth)
    pygame.draw.ellipse(surf, jaw_color, (head_cx + 2, head_cy - 3, head_r - 2, 6))
    pygame.draw.line(surf, (200, 190, 170), (head_cx + 4, head_cy - 1),
                    (head_cx + head_r - 2, head_cy - 1), 1)  # teeth

    # Hair patches (messy)
    hair_color = (50, 40, 30)
    pygame.draw.arc(surf, hair_color,
                    (head_cx - head_r, head_cy - head_r, head_r*2, head_r*2),
                    2.0, 4.5, 3)

    # Tank zombie gets extra bulk
    if zombie_type == "tank":
        # Extra shoulder bulk
        pygame.draw.ellipse(surf, shirt_color, (s*0.25, s*0.10, s*0.20, s*0.16))
        pygame.draw.ellipse(surf, shirt_color, (s*0.25, s*0.74, s*0.20, s*0.16))
        # Chains / armor
        chain_col = (120, 110, 100)
        pygame.draw.line(surf, chain_col, (int(s*0.30), int(s*0.25)), (int(s*0.55), int(s*0.35)), 2)
        pygame.draw.line(surf, chain_col, (int(s*0.30), int(s*0.75)), (int(s*0.55), int(s*0.65)), 2)

    return surf


# ═══════════════════════════════════════════════════════════
#  OBSTACLE SPRITES
# ═══════════════════════════════════════════════════════════

def create_barricade_surface(w=80, h=30):
    """Wooden barricade / makeshift wall."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    wood_base = (100, 70, 35)
    wood_dark = (70, 48, 22)
    wood_light = (130, 95, 50)
    nail_color = (160, 155, 150)

    # Planks
    plank_h = h // 3
    for i in range(3):
        y = i * plank_h
        shade = random.randint(-10, 10)
        color = tuple(max(0, min(255, c + shade)) for c in wood_base)
        pygame.draw.rect(surf, color, (2, y + 1, w - 4, plank_h - 2), border_radius=2)
        pygame.draw.rect(surf, wood_dark, (2, y + 1, w - 4, plank_h - 2), 1, border_radius=2)
        # Wood grain
        for _ in range(3):
            gx = random.randint(5, w - 10)
            pygame.draw.line(surf, wood_light, (gx, y + 2), (gx + random.randint(5, 15), y + 2), 1)

    # Cross brace
    pygame.draw.line(surf, wood_dark, (4, 2), (w - 4, h - 2), 3)
    # Nails
    for nx, ny in [(8, 4), (w - 10, 4), (8, h - 6), (w - 10, h - 6)]:
        pygame.draw.circle(surf, nail_color, (nx, ny), 2)

    return surf


def create_car_surface(w=100, h=55):
    """Abandoned car wreck (top-down)."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Shadow under car
    pygame.draw.ellipse(surf, (20, 20, 18), (4, 4, w - 8, h - 8))

    # Car body - random rust color
    colors = [(120, 45, 35), (80, 90, 100), (60, 70, 55), (100, 85, 40)]
    body_color = random.choice(colors)
    body_dark = tuple(max(0, c - 30) for c in body_color)
    body_light = tuple(min(255, c + 40) for c in body_color)

    # Main body
    body = pygame.Rect(10, 6, w - 20, h - 12)
    pygame.draw.rect(surf, body_dark, body, border_radius=8)
    pygame.draw.rect(surf, body_color, body.inflate(-3, -3), border_radius=6)

    # Windshield
    wind_color = (100, 130, 150, 180)
    wind_cracked = (80, 100, 120)
    wind_rect = pygame.Rect(w - 30, 12, 14, h - 24)
    pygame.draw.rect(surf, wind_cracked, wind_rect, border_radius=3)
    # Crack lines
    cx, cy = wind_rect.centerx, wind_rect.centery
    for angle in range(0, 360, 45):
        ex = cx + int(6 * math.cos(math.radians(angle)))
        ey = cy + int(6 * math.sin(math.radians(angle)))
        pygame.draw.line(surf, (140, 160, 170), (cx, cy), (ex, ey), 1)

    # Rear window
    rear_rect = pygame.Rect(16, 14, 10, h - 28)
    pygame.draw.rect(surf, wind_cracked, rear_rect, border_radius=2)

    # Wheels (4 corners)
    wheel_color = (30, 28, 25)
    wheel_rim = (70, 68, 65)
    for wx, wy in [(12, 4), (12, h - 10), (w - 22, 4), (w - 22, h - 10)]:
        pygame.draw.ellipse(surf, wheel_color, (wx, wy, 14, 8))
        pygame.draw.ellipse(surf, wheel_rim, (wx + 3, wy + 2, 8, 4))

    # Headlights
    pygame.draw.circle(surf, (180, 170, 100), (w - 14, 14), 4)
    pygame.draw.circle(surf, (180, 170, 100), (w - 14, h - 14), 4)

    # Rust spots
    rust = (100, 55, 25)
    for _ in range(5):
        rx = random.randint(18, w - 24)
        ry = random.randint(10, h - 10)
        pygame.draw.circle(surf, rust, (rx, ry), random.randint(2, 5))

    # Dents / damage
    pygame.draw.arc(surf, body_dark, (w//2-10, 8, 20, 12), 0, math.pi, 2)

    return surf


def create_crate_surface(size=40):
    """Wooden supply crate."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    s = size
    wood = (120, 85, 45)
    wood_dark = (85, 60, 30)
    wood_light = (150, 110, 65)
    metal = (140, 135, 125)
    metal_dark = (100, 95, 85)

    # Main crate body
    pygame.draw.rect(surf, wood_dark, (0, 0, s, s), border_radius=4)
    pygame.draw.rect(surf, wood, (2, 2, s-4, s-4), border_radius=3)

    # Planks (horizontal lines)
    for y in range(0, s, s // 4):
        pygame.draw.line(surf, wood_dark, (3, y), (s - 3, y), 1)

    # Cross braces
    pygame.draw.line(surf, wood_dark, (s//4, 3), (s//4, s-3), 2)
    pygame.draw.line(surf, wood_dark, (s*3//4, 3), (s*3//4, s-3), 2)

    # Metal straps
    pygame.draw.rect(surf, metal, (4, s//3 - 2, s - 8, 4), border_radius=1)
    pygame.draw.rect(surf, metal, (4, s*2//3 - 2, s - 8, 4), border_radius=1)
    # Strap bolts
    for bx in [8, s - 12]:
        pygame.draw.circle(surf, metal_dark, (bx, s//3), 2)
        pygame.draw.circle(surf, metal_dark, (bx, s*2//3), 2)

    # Stencil text (supply marking)
    pygame.draw.line(surf, wood_dark, (s//2-5, s//2-3), (s//2+5, s//2-3), 2)
    pygame.draw.line(surf, wood_dark, (s//2-4, s//2+2), (s//2+4, s//2+2), 2)

    return surf


def create_concrete_wall(w=60, h=60):
    """Concrete wall / pillar."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    concrete = (110, 108, 105)
    concrete_dark = (80, 78, 75)
    concrete_light = (135, 132, 128)

    # Main wall
    pygame.draw.rect(surf, concrete_dark, (0, 0, w, h), border_radius=3)
    pygame.draw.rect(surf, concrete, (2, 2, w-4, h-4), border_radius=2)

    # Texture / speckles
    for _ in range(30):
        sx = random.randint(3, w - 4)
        sy = random.randint(3, h - 4)
        shade = random.randint(-15, 15)
        color = tuple(max(0, min(255, c + shade)) for c in concrete)
        pygame.draw.rect(surf, color, (sx, sy, 2, 2))

    # Cracks
    crack_color = (70, 68, 65)
    cx = random.randint(w//4, w*3//4)
    cy = random.randint(h//4, h*3//4)
    for _ in range(3):
        ex = cx + random.randint(-15, 15)
        ey = cy + random.randint(-15, 15)
        pygame.draw.line(surf, crack_color, (cx, cy), (ex, ey), 1)
        cx, cy = ex, ey

    # Top shadow edge
    pygame.draw.line(surf, concrete_light, (3, 3), (w - 3, 3), 2)
    pygame.draw.line(surf, concrete_dark, (3, h - 3), (w - 3, h - 3), 2)

    return surf


def create_sandbag_surface(w=70, h=35):
    """Sandbag wall."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    bag_colors = [(140, 130, 100), (150, 140, 110), (130, 120, 90)]
    bag_dark = (100, 90, 65)
    bag_tie = (90, 80, 55)

    # Stack of sandbags (2 rows)
    bag_w = w // 3
    bag_h = h // 2
    for row in range(2):
        offset = (bag_w // 2) * (row % 2)  # staggered
        for col in range(4):
            bx = col * bag_w - bag_w // 2 + offset
            by = row * bag_h
            if bx < -bag_w // 2 or bx > w:
                continue
            color = bag_colors[(row + col) % len(bag_colors)]
            rect = pygame.Rect(bx + 2, by + 2, bag_w - 4, bag_h - 4)
            pygame.draw.ellipse(surf, bag_dark, rect.inflate(2, 2))
            pygame.draw.ellipse(surf, color, rect)
            # Bag tie
            pygame.draw.circle(surf, bag_tie, (rect.centerx, rect.centery), 2)
            # Fabric texture
            pygame.draw.line(surf, bag_dark,
                           (rect.left + 3, rect.centery),
                           (rect.right - 3, rect.centery), 1)

    return surf


# ═══════════════════════════════════════════════════════════
#  BULLETS, CROSSHAIR, GROUND, PICKUPS  (kept from original)
# ═══════════════════════════════════════════════════════════

def create_bullet_surface(color=YELLOW, size=6):
    """Create a bullet sprite."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    pygame.draw.circle(surf, WHITE, (size // 2, size // 2), size // 4)
    return surf


def create_crosshair(size=32):
    """Create a crosshair cursor."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    gap = 4
    length = 10
    width = 2
    pygame.draw.line(surf, RED, (center, center - gap - length), (center, center - gap), width)
    pygame.draw.line(surf, RED, (center, center + gap), (center, center + gap + length), width)
    pygame.draw.line(surf, RED, (center - gap - length, center), (center - gap, center), width)
    pygame.draw.line(surf, RED, (center + gap, center), (center + gap + length, center), width)
    pygame.draw.circle(surf, RED, (center, center), 2)
    return surf


def create_ground_tile(size=TILE_SIZE):
    """Create a ground tile with dirt / road texture."""
    surf = pygame.Surface((size, size))
    surf.fill((35, 35, 30))
    for _ in range(25):
        x = random.randint(0, size - 2)
        y = random.randint(0, size - 2)
        shade = random.randint(28, 45)
        pygame.draw.rect(surf, (shade, shade, shade - 5), (x, y, 2, 2))
    # Subtle grass tufts
    for _ in range(3):
        gx = random.randint(5, size - 5)
        gy = random.randint(5, size - 5)
        pygame.draw.line(surf, (40, 55, 30), (gx, gy), (gx + random.randint(-3, 3), gy - 4), 1)
    pygame.draw.line(surf, (28, 28, 25), (0, 0), (size, 0), 1)
    pygame.draw.line(surf, (28, 28, 25), (0, 0), (0, size), 1)
    return surf


def create_health_pickup(size=20):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surf, WHITE, (2, 2, size - 4, size - 4), border_radius=3)
    cross_w = 4
    cx, cy = size // 2, size // 2
    pygame.draw.rect(surf, RED, (cx - cross_w // 2, cy - size // 3, cross_w, size * 2 // 3))
    pygame.draw.rect(surf, RED, (cx - size // 3, cy - cross_w // 2, size * 2 // 3, cross_w))
    return surf


def create_ammo_pickup(size=20):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surf, (180, 150, 50), (4, 2, size - 8, size - 4), border_radius=2)
    pygame.draw.rect(surf, YELLOW, (6, 4, size - 12, size - 8), border_radius=1)
    pygame.draw.line(surf, (140, 110, 30), (size // 2, 4), (size // 2, size - 4), 1)
    return surf


# ═══════════════════════════════════════════════════════════
#  ASSET MANAGER
# ═══════════════════════════════════════════════════════════

class AssetManager:
    """Loads and caches all game assets."""

    def __init__(self):
        self.assets = {}
        self._generate_all()

    def _generate_all(self):
        # Player
        self.assets["player"] = create_player_surface()

        # Zombies
        for z_type in ZOMBIE_TYPES:
            self.assets[f"zombie_{z_type}"] = create_zombie_surface(z_type)

        # Bullets
        for w_name, w_data in WEAPONS.items():
            self.assets[f"bullet_{w_name}"] = create_bullet_surface(w_data["color"])

        # Obstacles
        self.assets["barricade"] = create_barricade_surface()
        self.assets["car"] = create_car_surface()
        self.assets["crate"] = create_crate_surface()
        self.assets["concrete_wall"] = create_concrete_wall()
        self.assets["sandbag"] = create_sandbag_surface()

        # Other
        self.assets["crosshair"] = create_crosshair()
        self.assets["ground_tile"] = create_ground_tile()
        self.assets["health_pickup"] = create_health_pickup()
        self.assets["ammo_pickup"] = create_ammo_pickup()

    def get(self, name):
        return self.assets.get(name)
