"""
UI elements - menus, HUD, game over screen.
"""
import pygame
import math
from settings import *


class UI:
    """Handles all UI rendering."""

    def __init__(self, screen):
        self.screen = screen
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.font_title = None
        self._init_fonts()

        # Animation state
        self.title_bob = 0
        self.button_hover = {}
        self.selected_difficulty = None

    def _init_fonts(self):
        """Initialize fonts."""
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact", 72)
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)

    # ─── Main Menu ─────────────────────────────────────────
    def draw_main_menu(self):
        """Draw the main menu screen."""
        self.screen.fill(MENU_BG)
        self.title_bob += 0.03
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        # Animated background particles
        now = pygame.time.get_ticks()
        for i in range(20):
            x = (i * 137 + now // 30) % w
            y = (i * 89 + now // 40) % h
            size = 2 + (i % 3)
            alpha = 40 + (i * 7) % 40
            color = (alpha, alpha // 2, alpha // 3)
            pygame.draw.circle(self.screen, color, (x, y), size)

        # Title with bob animation
        bob_y = int(math.sin(self.title_bob) * 8)
        title_surf = self.font_title.render("ZOMBII", True, MENU_ACCENT)
        title_rect = title_surf.get_rect(center=(w // 2, 160 + bob_y))
        # Shadow
        shadow_surf = self.font_title.render("ZOMBII", True, (80, 20, 20))
        self.screen.blit(shadow_surf, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title_surf, title_rect)

        # Subtitle
        sub_surf = self.font_medium.render("Survive the Horde", True, LIGHT_GRAY)
        sub_rect = sub_surf.get_rect(center=(w // 2, 230))
        self.screen.blit(sub_surf, sub_rect)

        # Play button
        play_rect = self._draw_button("PLAY", w // 2, 380, 220, 60, MENU_ACCENT, "play")

        # Quit button
        quit_rect = self._draw_button("QUIT", w // 2, 470, 220, 60, DARK_GRAY, "quit")

        # Controls info
        info_lines = [
            "WASD - Move  |  Mouse - Aim  |  Click - Shoot",
            "1/2/3 - Switch Weapon  |  R - Reload  |  ESC - Pause",
        ]
        for i, line in enumerate(info_lines):
            surf = self.font_small.render(line, True, (100, 100, 110))
            rect = surf.get_rect(center=(w // 2, h - 80 + i * 25))
            self.screen.blit(surf, rect)

        return {"play": play_rect, "quit": quit_rect}

    # ─── Difficulty Select ─────────────────────────────────
    def draw_difficulty_select(self):
        """Draw difficulty selection screen."""
        self.screen.fill(MENU_BG)
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        # Title
        title_surf = self.font_large.render("SELECT DIFFICULTY", True, WHITE)
        title_rect = title_surf.get_rect(center=(w // 2, 80))
        self.screen.blit(title_surf, title_rect)

        # Difficulty cards
        buttons = {}
        difficulties = list(DIFFICULTIES.items())
        card_width = 200
        card_height = 260
        total_width = len(difficulties) * card_width + (len(difficulties) - 1) * 20
        start_x = (w - total_width) // 2

        for i, (key, diff) in enumerate(difficulties):
            x = start_x + i * (card_width + 20)
            y = 150
            rect = pygame.Rect(x, y, card_width, card_height)

            # Hover effect
            mouse = pygame.mouse.get_pos()
            is_hover = rect.collidepoint(mouse)
            bg_color = (60, 60, 80) if is_hover else (35, 35, 55)
            border_color = diff["color"] if is_hover else (60, 60, 80)

            # Card background
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=12)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=12)

            # Colored top bar
            bar_rect = pygame.Rect(x + 3, y + 3, card_width - 6, 6)
            pygame.draw.rect(self.screen, diff["color"], bar_rect, border_radius=3)

            # Label
            label_surf = self.font_medium.render(diff["label"], True, diff["color"])
            label_rect = label_surf.get_rect(center=(x + card_width // 2, y + 50))
            self.screen.blit(label_surf, label_rect)

            # Description
            desc_surf = self.font_small.render(diff["description"], True, LIGHT_GRAY)
            desc_rect = desc_surf.get_rect(center=(x + card_width // 2, y + 90))
            self.screen.blit(desc_surf, desc_rect)

            # Stats
            stats = [
                f"HP: {diff['player_hp']}",
                f"Zombie Spd: {diff['zombie_speed']}",
                f"Max Zombies: {diff['max_zombies']}",
                f"Zombie HP: {diff['zombie_hp']}",
                f"Damage: {diff['damage_per_hit']}",
            ]
            for j, stat in enumerate(stats):
                stat_surf = self.font_small.render(stat, True, (160, 160, 170))
                stat_rect = stat_surf.get_rect(center=(x + card_width // 2, y + 130 + j * 22))
                self.screen.blit(stat_surf, stat_rect)

            buttons[key] = rect

        # Back button
        back_rect = self._draw_button("BACK", w // 2, h - 80, 200, 50, DARK_GRAY, "back")
        buttons["back"] = back_rect

        return buttons

    # ─── HUD ───────────────────────────────────────────────
    def draw_hud(self, player, level_manager):
        """Draw in-game HUD overlay."""
        w = SCREEN_WIDTH

        # Semi-transparent HUD background bar
        hud_surf = pygame.Surface((w, 50), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 140))
        self.screen.blit(hud_surf, (0, 0))

        # Health bar
        hp_pct = player.hp / player.max_hp
        bar_w = 200
        bar_h = 20
        bar_x = 15
        bar_y = 15

        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * hp_pct)
        hp_color = HEALTH_GREEN if hp_pct > 0.5 else YELLOW if hp_pct > 0.25 else HEALTH_RED
        if fill_w > 0:
            pygame.draw.rect(self.screen, hp_color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)

        # HP text
        hp_text = self.font_small.render(f"{int(player.hp)}/{player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + bar_w // 2 - hp_text.get_width() // 2, bar_y + 1))

        # Weapon & ammo
        weapon_info = WEAPONS[player.current_weapon]
        ammo = player.ammo[player.current_weapon]
        reload_text = " [RELOADING]" if player.reloading else ""
        wep_text = self.font_medium.render(
            f"{weapon_info['name']}: {ammo}/{weapon_info['mag_size']}{reload_text}",
            True, weapon_info["color"],
        )
        self.screen.blit(wep_text, (240, 10))

        # Wave & score
        wave_text = self.font_medium.render(
            f"Wave {level_manager.wave}", True, YELLOW,
        )
        self.screen.blit(wave_text, (w - 280, 10))

        score_text = self.font_medium.render(
            f"Score: {player.score}", True, WHITE,
        )
        self.screen.blit(score_text, (w - 150, 10))

        # Wave announcement
        if level_manager.is_announcing():
            announce_surf = self.font_title.render(level_manager.get_wave_text(), True, NEON_RED)
            announce_rect = announce_surf.get_rect(center=(w // 2, SCREEN_HEIGHT // 2 - 50))
            # Glow effect
            glow_surf = self.font_title.render(level_manager.get_wave_text(), True, (80, 20, 20))
            self.screen.blit(glow_surf, (announce_rect.x + 2, announce_rect.y + 2))
            self.screen.blit(announce_surf, announce_rect)

        # Between waves text
        if level_manager.between_waves and level_manager.wave_complete:
            remaining = max(0, level_manager.between_wave_duration -
                          (pygame.time.get_ticks() - level_manager.between_wave_start))
            text = self.font_medium.render(
                f"Next wave in {remaining // 1000 + 1}...", True, YELLOW,
            )
            rect = text.get_rect(center=(w // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, rect)

    # ─── Game Over ─────────────────────────────────────────
    def draw_game_over(self, player, level_manager):
        """Draw game over screen."""
        # Dim overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        # Game Over title
        go_text = self.font_title.render("GAME OVER", True, NEON_RED)
        go_rect = go_text.get_rect(center=(w // 2, h // 2 - 120))
        shadow = self.font_title.render("GAME OVER", True, (80, 10, 10))
        self.screen.blit(shadow, (go_rect.x + 3, go_rect.y + 3))
        self.screen.blit(go_text, go_rect)

        # Stats
        stats = [
            f"Score: {player.score}",
            f"Kills: {player.kills}",
            f"Waves Survived: {level_manager.wave}",
        ]
        for i, stat in enumerate(stats):
            surf = self.font_medium.render(stat, True, WHITE)
            rect = surf.get_rect(center=(w // 2, h // 2 - 30 + i * 40))
            self.screen.blit(surf, rect)

        # Buttons
        buttons = {}
        buttons["restart"] = self._draw_button("PLAY AGAIN", w // 2, h // 2 + 120, 250, 55, MENU_ACCENT, "restart")
        buttons["menu"] = self._draw_button("MAIN MENU", w // 2, h // 2 + 195, 250, 55, DARK_GRAY, "menu")

        return buttons

    # ─── Pause ─────────────────────────────────────────────
    def draw_pause(self):
        """Draw pause overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        pause_text = self.font_title.render("PAUSED", True, WHITE)
        rect = pause_text.get_rect(center=(w // 2, h // 2 - 60))
        self.screen.blit(pause_text, rect)

        buttons = {}
        buttons["resume"] = self._draw_button("RESUME", w // 2, h // 2 + 20, 220, 55, MENU_ACCENT, "resume")
        buttons["menu"] = self._draw_button("MAIN MENU", w // 2, h // 2 + 95, 220, 55, DARK_GRAY, "menu")

        return buttons

    # ─── Helper ────────────────────────────────────────────
    def _draw_button(self, text, cx, cy, width, height, color, key):
        """Draw a styled button and return its rect."""
        rect = pygame.Rect(cx - width // 2, cy - height // 2, width, height)

        mouse = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse)

        # Button bg
        bg_color = tuple(min(255, c + 30) for c in color) if is_hover else color
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=10)
        # Border
        border_color = WHITE if is_hover else (100, 100, 100)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=10)

        # Text
        text_surf = self.font_medium.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

        return rect
