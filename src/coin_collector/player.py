from collections.abc import Sequence

import pygame

from coin_collector.settings import (
    INITIAL_LIVES,
    INVULNERABILITY_DURATION,
    PLAYER_COLOR,
    PLAYER_SIZE,
    PLAYER_SPEED,
)


class Player:
    def __init__(self, bounds: pygame.Rect) -> None:
        self.bounds = bounds.copy()
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = bounds.center
        self.position = pygame.Vector2(self.rect.topleft)
        self.speed = PLAYER_SPEED
        self.lives = INITIAL_LIVES
        self.invulnerability_remaining = 0.0

    def update(self, dt: float, keys: Sequence[bool]) -> None:
        self.invulnerability_remaining = max(
            0.0, self.invulnerability_remaining - dt
        )
        direction = pygame.Vector2(
            int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]),
            int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]),
        )
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.position += direction * self.speed * dt
        self.position.x = max(
            self.bounds.left, min(self.position.x, self.bounds.right - self.rect.width)
        )
        self.position.y = max(
            self.bounds.top, min(self.position.y, self.bounds.bottom - self.rect.height)
        )
        self.rect.topleft = round(self.position.x), round(self.position.y)

    def take_damage(self) -> None:
        if self.invulnerability_remaining <= 0 and self.lives > 0:
            self.lives -= 1
            self.invulnerability_remaining = INVULNERABILITY_DURATION

    def draw(self, surface: pygame.Surface) -> None:
        if self.invulnerability_remaining > 0:
            if int(self.invulnerability_remaining * 10) % 2 == 0:
                return
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
