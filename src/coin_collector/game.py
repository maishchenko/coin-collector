from enum import Enum, auto
from pathlib import Path
from time import perf_counter

import pygame

from coin_collector import ui
from coin_collector.coin import Coin
from coin_collector.database import Database
from coin_collector.enemy import Enemy
from coin_collector.player import Player
from coin_collector.settings import (
    BACKGROUND_COLOR,
    BORDER_COLOR,
    COIN_COUNT,
    COIN_SCORE,
    DATABASE_PATH,
    ENEMY_COUNT,
    FIELD_COLOR,
    FIELD_HEIGHT,
    FIELD_LEFT,
    FIELD_TOP,
    FIELD_WIDTH,
    FPS,
    MAX_NICKNAME_LENGTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WIN_SCORE,
)


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    LEADERBOARD = auto()


class Game:
    def __init__(self, db_path: str | Path = DATABASE_PATH) -> None:
        # Звука в игре нет, поэтому достаточно модулей окна и шрифтов.
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Coin Collector — Сбор монет")
        font_path = pygame.font.match_font("dejavusans,arial,liberationsans")
        self.font = pygame.font.Font(font_path, 22)
        self.title_font = pygame.font.Font(font_path, 42)
        self.clock = pygame.time.Clock()
        self.database = Database(db_path)
        self.bounds = pygame.Rect(FIELD_LEFT, FIELD_TOP, FIELD_WIDTH, FIELD_HEIGHT)
        self.state = GameState.MENU
        self.running = True
        self.nickname = ""
        self.error = ""
        self.score = 0
        self.started_at = 0.0
        self.elapsed_ms = 0
        self.is_win = False
        self.top_scores: list[tuple[str, int]] = []
        self.player = Player(self.bounds)
        self.enemies: list[Enemy] = []
        self.coins: list[Coin] = []

    def start_game(self) -> None:
        nickname = self.nickname.strip().lower()
        if not nickname:
            self.error = "Введите непустой никнейм"
            return
        self.nickname = nickname
        self.error = ""
        self.score = 0
        self.is_win = False
        self.player = Player(self.bounds)
        self.enemies = []
        for index in range(ENEMY_COUNT):
            center = (
                self.bounds.left + (index + 1) * self.bounds.width // (ENEMY_COUNT + 1),
                self.bounds.top + (65 if index % 2 == 0 else self.bounds.height - 65),
            )
            direction = (1.0 if index % 2 == 0 else -1.0, 0.7)
            self.enemies.append(Enemy(self.bounds, center, direction))
        self.coins = []
        for _ in range(COIN_COUNT):
            coin = Coin(self.bounds)
            coin.respawn(
                [self.player.rect]
                + [enemy.rect for enemy in self.enemies]
                + [other.rect for other in self.coins]
            )
            self.coins.append(coin)
        self.state = GameState.PLAYING
        self.started_at = perf_counter()
        self.elapsed_ms = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU
            self.error = ""
            return
        if self.state == GameState.MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                    self.error = ""
                elif event.key == pygame.K_RETURN:
                    self.start_game()
                else:
                    text = getattr(event, "unicode", "")
                    if text and text.isprintable():
                        self.nickname = (self.nickname + text)[:MAX_NICKNAME_LENGTH]
                        self.error = ""
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ui.START_BUTTON.collidepoint(event.pos):
                    self.start_game()
                elif ui.LEADERBOARD_BUTTON.collidepoint(event.pos):
                    self.top_scores = self.database.get_top_scores()
                    self.state = GameState.LEADERBOARD
        elif self.state == GameState.GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.start_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ui.MENU_BUTTON.collidepoint(event.pos):
                    self.state = GameState.MENU
        elif self.state == GameState.LEADERBOARD:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ui.MENU_BUTTON.collidepoint(event.pos):
                    self.state = GameState.MENU

    def update(self, dt: float) -> None:
        if self.state != GameState.PLAYING:
            return
        # Реальное время не зависит от ограничения dt для движения объектов.
        self.elapsed_ms = round((perf_counter() - self.started_at) * 1000)
        self.player.update(dt, pygame.key.get_pressed())
        for enemy in self.enemies:
            enemy.update(dt)
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage()
        if self.player.lives <= 0:
            self.finish_game(False)
            return
        for coin in self.coins:
            if self.player.rect.colliderect(coin.rect):
                self.score += COIN_SCORE
                coin.respawn(
                    [self.player.rect]
                    + [enemy.rect for enemy in self.enemies]
                    + [other.rect for other in self.coins if other is not coin]
                )
                if self.score >= WIN_SCORE:
                    self.finish_game(True)
                    return

    def finish_game(self, is_win: bool) -> None:
        # Переход состояния сохраняет результат ровно один раз за завершённую игру.
        if self.state != GameState.PLAYING:
            return
        self.database.save_score(self.nickname, self.score, is_win, self.elapsed_ms)
        self.is_win = is_win
        self.state = GameState.GAME_OVER
        self.top_scores = self.database.get_top_scores()

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        if self.state == GameState.MENU:
            ui.draw_menu(self.screen, self.font, self.title_font, self.nickname, self.error)
        elif self.state == GameState.PLAYING:
            pygame.draw.rect(self.screen, FIELD_COLOR, self.bounds)
            for coin in self.coins:
                coin.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            self.player.draw(self.screen)
            pygame.draw.rect(self.screen, BORDER_COLOR, self.bounds, width=1)
            ui.draw_game_hud(
                self.screen, self.font, self.nickname, self.score,
                self.player.lives, self.elapsed_ms,
            )
        elif self.state == GameState.GAME_OVER:
            ui.draw_game_over(
                self.screen, self.font, self.title_font, self.nickname,
                self.score, self.is_win, self.top_scores, self.elapsed_ms,
            )
        elif self.state == GameState.LEADERBOARD:
            ui.draw_leaderboard(self.screen, self.font, self.title_font, self.top_scores)

    def run(self) -> None:
        try:
            while self.running:
                # После перетаскивания окна не делаем скачок через всё поле.
                dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
                for event in pygame.event.get():
                    self.handle_event(event)
                if not self.running:
                    break
                if self.state == GameState.PLAYING:
                    self.update(dt)
                self.draw()
                pygame.display.flip()
        finally:
            pygame.quit()
