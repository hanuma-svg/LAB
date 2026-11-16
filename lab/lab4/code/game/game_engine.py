import math
import random
from array import array
import pygame
from .hole import Hole

DARK_BROWN = (60, 40, 20)
MOLE_BROWN = (140, 95, 55)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
OVERLAY = (25, 35, 25)


class GameEngine:
    DIFFICULTIES = {
        "1": ("Easy", 0.014, 60),
        "2": ("Medium", 0.022, 45),
        "3": ("Hard", 0.032, 32),
    }

    def __init__(self, width, height, rows=3, cols=3):
        self.width = width
        self.height = height
        self.holes = []
        spacing_x = width // (cols + 1)
        spacing_y = (height - 80) // (rows + 1)
        for r in range(rows):
            for c in range(cols):
                self.holes.append(Hole(spacing_x * (c + 1), 80 + spacing_y * (r + 1)))
        self.round_seconds = 30
        self.score = 0
        self.misses = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.game_over = False
        self.in_menu = True
        self.difficulty_name = "Medium"
        self.spawn_chance = 0.022
        self.mole_up_frames = 45
        self.time_left_frames = 0
        self._game_over_sound_played = False
        self.sounds = self._create_sounds()

    def _create_sounds(self):
        """Generate short tones so the game needs no external audio assets."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return {
                "hit": self._tone(720, 0.09),
                "miss": self._tone(180, 0.12),
                "end": self._tone(260, 0.35),
            }
        except pygame.error:
            return {}

    @staticmethod
    def _tone(frequency, duration):
        sample_rate = 44100
        samples = array("h")
        for index in range(int(sample_rate * duration)):
            envelope = min(1.0, index / 500) * min(1.0, (sample_rate * duration - index) / 1000)
            samples.append(int(12000 * envelope * math.sin(2 * math.pi * frequency * index / sample_rate)))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _play(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def start_round(self, difficulty_key="2"):
        name, self.spawn_chance, self.mole_up_frames = self.DIFFICULTIES[difficulty_key]
        self.difficulty_name = name
        self.score = 0
        self.misses = 0
        self.time_left_frames = self.round_seconds * 60
        self.game_over = False
        self.in_menu = False
        self._game_over_sound_played = False
        for hole in self.holes:
            hole.whack()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return "quit"
            if self.in_menu and event.unicode in self.DIFFICULTIES:
                self.start_round(event.unicode)
                return
            if self.game_over and event.key == pygame.K_r:
                self.in_menu = True
                return
        if not self.in_menu and not self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        candidates = [hole for hole in self.holes if hole.active and hole.contains_point(pos)]
        if candidates:
            target = min(candidates, key=lambda hole: math.dist(pos, (hole.center_x, hole.center_y)))
            target.whack()
            self.score += 1
            self._play("hit")
        else:
            self.misses += 1
            self._play("miss")

    def handle_input(self):
        pass

    def update(self):
        if self.in_menu or self.game_over:
            return
        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.game_over = True
            for hole in self.holes:
                hole.whack()
            if not self._game_over_sound_played:
                self._play("end")
                self._game_over_sound_played = True
            return
        for hole in self.holes:
            hole.update()
            if not hole.active and random.random() < self.spawn_chance:
                hole.pop_up(self.mole_up_frames)

    def render(self, screen):
        if self.in_menu:
            self._render_menu(screen)
            return
        for hole in self.holes:
            pygame.draw.circle(screen, DARK_BROWN, (hole.center_x, hole.center_y), 40)
            if hole.active:
                pygame.draw.circle(screen, MOLE_BROWN, (hole.center_x, hole.center_y), 32)
        screen.blit(self.font.render(f"Score: {self.score}", True, BLACK), (10, 10))
        seconds_left = max(0, self.time_left_frames // 60)
        screen.blit(self.font.render(f"Time: {seconds_left}s", True, BLACK), (self.width - 140, 10))
        screen.blit(self.small_font.render(self.difficulty_name, True, BLACK), (10, 48))
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*OVERLAY, 235))
            screen.blit(overlay, (0, 0))
            self._center_text(screen, "TIME'S UP!", self.title_font, 185)
            self._center_text(screen, f"Final score: {self.score}", self.font, 255)
            self._center_text(screen, "Press R to replay", self.font, 315)
            self._center_text(screen, "Press Q to exit", self.small_font, 360)

    def _render_menu(self, screen):
        screen.fill((120, 170, 90))
        self._center_text(screen, "WHACK-A-MOLE", self.title_font, 125)
        self._center_text(screen, "Choose your difficulty", self.font, 205)
        self._center_text(screen, "1  Easy   - slower moles", self.font, 275)
        self._center_text(screen, "2  Medium - balanced", self.font, 325)
        self._center_text(screen, "3  Hard   - fast moles", self.font, 375)
        self._center_text(screen, "Press Q to exit", self.small_font, 450)

    def _center_text(self, screen, text, font, y):
        surface = font.render(text, True, WHITE)
        screen.blit(surface, surface.get_rect(center=(self.width // 2, y)))
