"""
Obstacle entity - static cover objects the player can hide behind.
Blocks bullets and player/zombie movement. Provides damage reduction when player is behind cover.
"""
import pygame
import random
import math
from settings import *


class Obstacle(pygame.sprite.Sprite):
    """A static obstacle that provides cover."""

    def __init__(self, x, y, obstacle_type, asset_surface):
        super().__init__()
        self.obstacle_type = obstacle_type
        self.image = asset_surface
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)

        # Collision rect (slightly smaller than visual for forgiving gameplay)
        self.collision_rect = self.rect.inflate(-6, -6)

    def draw(self, surface, camera):
        """Draw the obstacle."""
        screen_rect = camera.apply(self)
        surface.blit(self.image, screen_rect)

        # Optional: draw shadow underneath
        shadow_rect = screen_rect.inflate(-4, -4)
        shadow_rect.y += 3
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 30))
        surface.blit(shadow_surf, shadow_rect)


def generate_obstacles(assets, player_start_pos):
    """Generate random obstacles spread across the world, avoiding player spawn area."""
    obstacles = pygame.sprite.Group()
    placed = []

    attempts = 0
    max_attempts = OBSTACLE_COUNT * 20

    # Weighted random type selection
    types = list(OBSTACLE_TYPES.keys())
    weights = [OBSTACLE_TYPES[t]["weight"] for t in types]

    while len(placed) < OBSTACLE_COUNT and attempts < max_attempts:
        attempts += 1

        # Pick type
        obs_type = random.choices(types, weights=weights, k=1)[0]
        info = OBSTACLE_TYPES[obs_type]

        # Random position (avoid edges and player start)
        margin = 150
        x = random.randint(margin, WORLD_WIDTH - margin)
        y = random.randint(margin, WORLD_HEIGHT - margin)

        # Don't spawn too close to player start
        dist_to_player = math.hypot(x - player_start_pos[0], y - player_start_pos[1])
        if dist_to_player < 200:
            continue

        # Don't spawn too close to other obstacles
        too_close = False
        for ox, oy in placed:
            if math.hypot(x - ox, y - oy) < OBSTACLE_MIN_DIST:
                too_close = True
                break
        if too_close:
            continue

        # Create obstacle
        surface = assets.get(obs_type)
        if surface is None:
            continue

        obstacle = Obstacle(x, y, obs_type, surface)
        obstacles.add(obstacle)
        placed.append((x, y))

    return obstacles


def check_player_behind_cover(player, obstacles, zombie_pos):
    """
    Check if the player is behind an obstacle relative to a zombie's position.
    Returns True if the player is hidden behind cover from this zombie.
    """
    # Cast a line from zombie to player and check if any obstacle intersects
    px, py = player.pos.x, player.pos.y
    zx, zy = zombie_pos.x, zombie_pos.y

    # Direction from zombie to player
    dx = px - zx
    dy = py - zy
    dist = math.hypot(dx, dy)
    if dist < 1:
        return False

    # Check if any obstacle is between zombie and player
    for obstacle in obstacles:
        # Quick distance check - obstacle must be between zombie and player
        ox, oy = obstacle.pos.x, obstacle.pos.y
        obs_dist_to_zombie = math.hypot(ox - zx, oy - zy)
        obs_dist_to_player = math.hypot(ox - px, oy - py)

        # Obstacle should be between them and close to the line of sight
        if obs_dist_to_zombie > dist or obs_dist_to_player > dist:
            continue

        # Player must be close to the obstacle (within ~60px) to count as "hiding"
        if obs_dist_to_player > 70:
            continue

        # Point-to-line distance: check if obstacle center is near the zombie→player line
        # Using cross product formula
        cross = abs(dx * (zy - oy) - dy * (zx - ox))
        line_dist = cross / dist

        if line_dist < 40:  # obstacle radius threshold
            return True

    return False


def resolve_entity_obstacle_collision(entity, obstacles):
    """
    Push an entity (player or zombie) out of any obstacles it overlaps with.
    Returns True if a collision was resolved.
    """
    collided = False
    for obstacle in obstacles:
        if entity.rect.colliderect(obstacle.collision_rect):
            collided = True
            # Find the shortest push-out direction
            overlap_left = entity.rect.right - obstacle.collision_rect.left
            overlap_right = obstacle.collision_rect.right - entity.rect.left
            overlap_top = entity.rect.bottom - obstacle.collision_rect.top
            overlap_bottom = obstacle.collision_rect.bottom - entity.rect.top

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                entity.pos.x -= overlap_left
            elif min_overlap == overlap_right:
                entity.pos.x += overlap_right
            elif min_overlap == overlap_top:
                entity.pos.y -= overlap_top
            elif min_overlap == overlap_bottom:
                entity.pos.y += overlap_bottom

            entity.rect.center = (int(entity.pos.x), int(entity.pos.y))

    return collided
