import pygame

from coin_collector.settings import ENEMY_COLOR, ENEMY_SIZE, ENEMY_SPEED


class Enemy:
    def __init__(
        self, bounds: pygame.Rect, center: tuple[int, int], direction: tuple[float, float]
    ) -> None:
        self.bounds = bounds.copy()
        self.rect = pygame.Rect(0, 0, ENEMY_SIZE, ENEMY_SIZE)
        self.rect.center = center
        self.position = pygame.Vector2(self.rect.topleft)
        self.direction = pygame.Vector2(direction).normalize()
        self.speed = ENEMY_SPEED

    def update(self, dt: float) -> None:
        self.position += self.direction * self.speed * dt
        if self.position.x <= self.bounds.left:
            self.position.x = self.bounds.left
            self.direction.x = abs(self.direction.x)
        elif self.position.x >= self.bounds.right - self.rect.width:
            self.position.x = self.bounds.right - self.rect.width
            self.direction.x = -abs(self.direction.x)
        if self.position.y <= self.bounds.top:
            self.position.y = self.bounds.top
            self.direction.y = abs(self.direction.y)
        elif self.position.y >= self.bounds.bottom - self.rect.height:
            self.position.y = self.bounds.bottom - self.rect.height
            self.direction.y = -abs(self.direction.y)
        self.rect.topleft = round(self.position.x), round(self.position.y)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, ENEMY_COLOR, self.rect)
