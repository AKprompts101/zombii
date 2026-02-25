"""
ZOMBII - Zombie Shooter Game
Main entry point: game loop, state machine, and core game logic.
"""
import pygame
import sys
import math
import os

# Ensure we can import from src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from settings import *
from assets_manager import AssetManager
from player import Player
from zombie import Zombie, spawn_zombie
from bullet import Bullet
from weapon import fire_weapon
from level import LevelManager
from camera import Camera
from particles import ParticleManager
from ui import UI
from obstacle import generate_obstacles, resolve_entity_obstacle_collision, check_player_behind_cover


class Game:
    """Main game class - manages the entire game lifecycle."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Load assets
        self.assets = AssetManager()

        # Custom cursor
        pygame.mouse.set_visible(False)
        self.crosshair = self.assets.get("crosshair")

        # UI
        self.ui = UI(self.screen)

        # Game state
        self.state = STATE_MENU
        self.running = True
        self.difficulty_key = None
        self.difficulty = None

        # Sprite groups (initialized on game start)
        self.all_sprites = None
        self.zombies = None
        self.bullets = None
        self.player = None
        self.camera = None
        self.level_manager = None
        self.particles = None
        self.obstacles = None

        # Ground tile cache
        self.ground_tile = self.assets.get("ground_tile")

    def _start_game(self, difficulty_key):
        """Initialize a new game with the given difficulty."""
        self.difficulty_key = difficulty_key
        self.difficulty = DIFFICULTIES[difficulty_key]

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        # Player
        player_surf = self.assets.get("player")
        self.player = Player(
            WORLD_WIDTH // 2, WORLD_HEIGHT // 2,
            player_surf, self.difficulty,
        )
        self.all_sprites.add(self.player)

        # Camera
        self.camera = Camera()
        self.camera.follow(self.player)

        # Level manager
        self.level_manager = LevelManager(self.difficulty)

        # Particles
        self.particles = ParticleManager()

        # Obstacles
        self.obstacles = generate_obstacles(self.assets, (self.player.pos.x, self.player.pos.y))

        self.state = STATE_PLAYING

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Process input events based on current state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

            if event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_click(self, pos):
        """Handle mouse clicks based on state."""
        if self.state == STATE_MENU:
            buttons = self.ui.draw_main_menu()
            if buttons["play"].collidepoint(pos):
                self.state = STATE_DIFFICULTY
            elif buttons["quit"].collidepoint(pos):
                self.running = False

        elif self.state == STATE_DIFFICULTY:
            buttons = self.ui.draw_difficulty_select()
            for key in DIFFICULTIES:
                if key in buttons and buttons[key].collidepoint(pos):
                    self._start_game(key)
                    return
            if "back" in buttons and buttons["back"].collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_GAME_OVER:
            buttons = self.ui.draw_game_over(self.player, self.level_manager)
            if buttons["restart"].collidepoint(pos):
                self._start_game(self.difficulty_key)
            elif buttons["menu"].collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_PAUSED:
            buttons = self.ui.draw_pause()
            if buttons["resume"].collidepoint(pos):
                self.state = STATE_PLAYING
            elif buttons["menu"].collidepoint(pos):
                self.state = STATE_MENU

    def _handle_key(self, key):
        """Handle key presses."""
        if key == pygame.K_ESCAPE:
            if self.state == STATE_PLAYING:
                self.state = STATE_PAUSED
            elif self.state == STATE_PAUSED:
                self.state = STATE_PLAYING
            elif self.state == STATE_DIFFICULTY:
                self.state = STATE_MENU

        if self.state == STATE_PLAYING and key == pygame.K_r:
            if self.player:
                self.player.start_reload()

    def _update(self):
        """Update game logic."""
        if self.state != STATE_PLAYING:
            return

        # Player
        self.player.update(self.camera)

        # Camera
        self.camera.update()

        # Player-Obstacle collision
        if self.obstacles:
            resolve_entity_obstacle_collision(self.player, self.obstacles)

        # Shooting (hold to fire)
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            new_bullets = fire_weapon(self.player, self.assets)
            for b in new_bullets:
                self.bullets.add(b)
                self.all_sprites.add(b)

        # Bullets
        for bullet in list(self.bullets):
            bullet.update()

        # Zombie spawning
        if self.level_manager.should_spawn(len(self.zombies)):
            zombie = spawn_zombie(self.player.pos, self.difficulty, self.assets)
            self.zombies.add(zombie)
            self.all_sprites.add(zombie)

        # Zombie AI
        for zombie in self.zombies:
            zombie.update(self.player.pos)
            if self.obstacles:
                resolve_entity_obstacle_collision(zombie, self.obstacles)

        # Bullet-obstacle collisions
        for bullet in list(self.bullets):
            for obstacle in self.obstacles:
                if bullet.rect.colliderect(obstacle.collision_rect):
                    self.particles.emit(bullet.pos.x, bullet.pos.y, (150, 150, 150), 5)
                    bullet.kill()
                    break

        # Bullet-zombie collisions
        for bullet in list(self.bullets):
            for zombie in list(self.zombies):
                if bullet.rect.colliderect(zombie.rect):
                    # Hit!
                    self.particles.emit(
                        zombie.pos.x, zombie.pos.y,
                        BLOOD_RED, 6,
                    )
                    if zombie.take_damage(bullet.damage):
                        # Kill
                        self.particles.emit(
                            zombie.pos.x, zombie.pos.y,
                            DARK_RED, 12,
                        )
                        self.player.score += zombie.score_value
                        self.player.kills += 1
                        zombie.kill()
                        self.level_manager.on_zombie_killed(len(self.zombies))
                    bullet.kill()
                    break

        # Zombie-player collision (damage)
        for zombie in self.zombies:
            if zombie.rect.colliderect(self.player.rect):
                if zombie.can_attack():
                    # Check cover
                    is_covered = check_player_behind_cover(self.player, self.obstacles, zombie.pos)
                    dmg = zombie.damage * (1 - COVER_DAMAGE_REDUCTION) if is_covered else zombie.damage
                    dead = self.player.take_damage(dmg)

                    self.particles.emit(
                        self.player.pos.x, self.player.pos.y,
                        RED, 4,
                    )
                    if dead:
                        self.state = STATE_GAME_OVER
                        return

        # Level / wave management
        self.level_manager.update()

        # Particles
        self.particles.update()

    def _draw(self):
        """Render everything."""
        if self.state == STATE_MENU:
            self.ui.draw_main_menu()

        elif self.state == STATE_DIFFICULTY:
            self.ui.draw_difficulty_select()

        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self._draw_game_world()
            self.ui.draw_hud(self.player, self.level_manager)
            if self.state == STATE_PAUSED:
                self.ui.draw_pause()

        elif self.state == STATE_GAME_OVER:
            self._draw_game_world()
            self.ui.draw_game_over(self.player, self.level_manager)

        # Custom crosshair cursor (always on top)
        mouse_pos = pygame.mouse.get_pos()
        if self.crosshair:
            ch_rect = self.crosshair.get_rect(center=mouse_pos)
            self.screen.blit(self.crosshair, ch_rect)

        pygame.display.flip()

    def _draw_game_world(self):
        """Draw the game world with camera offset."""
        self.screen.fill(BG_COLOR)

        if not self.camera:
            return

        cam_x = int(self.camera.offset.x)
        cam_y = int(self.camera.offset.y)

        # Draw ground tiles
        tile_size = TILE_SIZE
        start_col = max(0, cam_x // tile_size)
        end_col = min(WORLD_WIDTH // tile_size, (cam_x + SCREEN_WIDTH) // tile_size + 1)
        start_row = max(0, cam_y // tile_size)
        end_row = min(WORLD_HEIGHT // tile_size, (cam_y + SCREEN_HEIGHT) // tile_size + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                x = col * tile_size - cam_x
                y = row * tile_size - cam_y
                self.screen.blit(self.ground_tile, (x, y))

        # Draw world border
        border_rect = pygame.Rect(-cam_x, -cam_y, WORLD_WIDTH, WORLD_HEIGHT)
        pygame.draw.rect(self.screen, DARK_RED, border_rect, 4)

        # Draw bullets
        for bullet in self.bullets:
            screen_rect = self.camera.apply(bullet)
            self.screen.blit(bullet.image, screen_rect)

        # Y-sort rendering for depth (obstacles, zombies, player)
        render_group = []
        if self.obstacles:
            render_group.extend(self.obstacles.sprites())
        if self.zombies:
            render_group.extend(self.zombies.sprites())
        if self.player:
            render_group.append(self.player)

        render_group.sort(key=lambda s: s.rect.bottom)

        for sprite in render_group:
            if hasattr(sprite, 'obstacle_type'):
                sprite.draw(self.screen, self.camera)
            else:
                screen_rect = self.camera.apply(sprite)
                self.screen.blit(sprite.image, screen_rect)
                if hasattr(sprite, 'draw_health_bar'):
                    sprite.draw_health_bar(self.screen, self.camera)

        # Draw particles
        self.particles.draw(self.screen, self.camera.offset)


if __name__ == "__main__":
    game = Game()
    game.run()
