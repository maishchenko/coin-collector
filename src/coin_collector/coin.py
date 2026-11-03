import random
from collections.abc import Sequence

import pygame

from coin_collector.settings import COIN_COLOR, COIN_RADIUS


class Coin:
    def __init__(self, bounds: pygame.Rect) -> None:
        self.bounds = bounds.copy()
        self.rect = pygame.Rect(bounds.left, bounds.top, COIN_RADIUS * 2, COIN_RADIUS * 2)

    def respawn(self, occupied_rects: Sequence[pygame.Rect]) -> None:
        for _ in range(1000):
            self.rect.topleft = (
                random.randint(self.bounds.left, self.bounds.right - self.rect.width),
                random.randint(self.bounds.top, self.bounds.bottom - self.rect.height),
            )
            if self.rect.collidelist(occupied_rects) == -1:
                return
        # Запасной поиск гарантирует завершение даже при неудачной серии случайных мест.
        for y in range(self.bounds.top, self.bounds.bottom - self.rect.height + 1):
            for x in range(self.bounds.left, self.bounds.right - self.rect.width + 1):
                self.rect.topleft = x, y
                if self.rect.collidelist(occupied_rects) == -1:
                    return
        raise ValueError("На поле нет свободного места для монеты")

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, COIN_COLOR, self.rect.center, COIN_RADIUS)
