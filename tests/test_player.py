from collections import defaultdict

import pygame
import pytest

from coin_collector.player import Player
from coin_collector.settings import INITIAL_LIVES, INVULNERABILITY_DURATION


@pytest.mark.parametrize("key", [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])
def test_player_stays_inside_bounds(key: int) -> None:
    bounds = pygame.Rect(20, 100, 760, 480)
    player = Player(bounds)
    keys = defaultdict(bool, {key: True})
    player.update(100.0, keys)
    assert bounds.contains(player.rect)
    # Точные координаты тоже ограничены: после упора можно сразу двигаться обратно.
    assert player.position == pygame.Vector2(player.rect.topleft)


def test_damage_removes_one_life() -> None:
    player = Player(pygame.Rect(0, 0, 800, 600))
    player.take_damage()
    assert player.lives == INITIAL_LIVES - 1


def test_invulnerability_blocks_damage_and_expires() -> None:
    player = Player(pygame.Rect(0, 0, 800, 600))
    player.take_damage()
    player.update(INVULNERABILITY_DURATION / 2, defaultdict(bool))
    player.take_damage()
    assert player.lives == INITIAL_LIVES - 1
    player.update(INVULNERABILITY_DURATION / 2, defaultdict(bool))
    player.take_damage()
    assert player.lives == INITIAL_LIVES - 2


def test_movement_uses_delta_time() -> None:
    bounds = pygame.Rect(0, 0, 800, 600)
    first, second = Player(bounds), Player(bounds)
    keys = defaultdict(bool, {pygame.K_RIGHT: True})
    first.update(0.5, keys)
    for _ in range(50):
        second.update(0.01, keys)
    assert first.position.distance_to(second.position) < 0.000001
    assert first.rect == second.rect


def test_diagonal_movement_has_same_speed() -> None:
    player = Player(pygame.Rect(0, 0, 800, 600))
    start = player.position.copy()
    player.update(0.1, defaultdict(bool, {pygame.K_RIGHT: True, pygame.K_DOWN: True}))
    assert player.position.distance_to(start) == pytest.approx(player.speed * 0.1)
