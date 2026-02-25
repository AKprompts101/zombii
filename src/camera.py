"""
Camera system that follows the player around the world.
"""
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT


class Camera:
    """Simple camera offset that follows a target."""

    def __init__(self):
        self.offset = pygame.math.Vector2(0, 0)
        self.target = None

    def follow(self, target):
        """Set the target to follow."""
        self.target = target

    def update(self):
        """Update camera offset to center on target."""
        if self.target is None:
            return

        # Center the target on screen
        target_x = self.target.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.target.rect.centery - SCREEN_HEIGHT // 2

        # Clamp to world bounds
        target_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
        target_y = max(0, min(target_y, WORLD_HEIGHT - SCREEN_HEIGHT))

        # Smooth follow with lerp
        self.offset.x += (target_x - self.offset.x) * 0.1
        self.offset.y += (target_y - self.offset.y) * 0.1

    def apply(self, entity):
        """Return the screen position for an entity."""
        return pygame.Rect(
            entity.rect.x - int(self.offset.x),
            entity.rect.y - int(self.offset.y),
            entity.rect.width,
            entity.rect.height,
        )

    def apply_pos(self, pos):
        """Apply camera offset to a position tuple."""
        return (pos[0] - int(self.offset.x), pos[1] - int(self.offset.y))

    def reverse(self, screen_pos):
        """Convert screen position to world position."""
        return (
            screen_pos[0] + int(self.offset.x),
            screen_pos[1] + int(self.offset.y),
        )
