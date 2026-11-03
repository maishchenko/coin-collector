import pygame

from coin_collector.settings import (
    BORDER_COLOR,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    COIN_SCORE,
    ENEMY_COLOR,
    FIELD_COLOR,
    MUTED_COLOR,
    SCREEN_WIDTH,
    TEXT_COLOR,
    WIN_SCORE,
)

NICKNAME_RECT = pygame.Rect(220, 195, 360, 44)
START_BUTTON = pygame.Rect(250, 285, 300, 46)
LEADERBOARD_BUTTON = pygame.Rect(250, 345, 300, 46)
MENU_BUTTON = pygame.Rect(250, 525, 300, 44)


def draw_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    y: int,
    color: tuple[int, int, int] = TEXT_COLOR,
) -> None:
    rendered = font.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(midtop=(SCREEN_WIDTH // 2, y)))


def draw_button(
    surface: pygame.Surface, font: pygame.font.Font, rect: pygame.Rect, label: str
) -> None:
    color = BUTTON_HOVER_COLOR if rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=6)
    rendered = font.render(label, True, TEXT_COLOR)
    surface.blit(rendered, rendered.get_rect(center=rect.center))


def draw_menu(
    surface: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    nickname: str,
    error: str,
) -> None:
    draw_text(surface, title_font, "Coin Collector", 55)
    draw_text(surface, font, "Соберите 100 очков быстрее всех", 120, MUTED_COLOR)
    draw_text(surface, font, "Введите никнейм:", 160)
    pygame.draw.rect(surface, FIELD_COLOR, NICKNAME_RECT, border_radius=4)
    pygame.draw.rect(surface, BORDER_COLOR, NICKNAME_RECT, width=2, border_radius=4)
    rendered = font.render(nickname + "|", True, TEXT_COLOR)
    # Длинный никнейм прокручивается внутри поля, а не выходит за его края.
    previous_clip = surface.get_clip()
    surface.set_clip(NICKNAME_RECT.inflate(-24, -4))
    text_x = min(NICKNAME_RECT.x + 12, NICKNAME_RECT.right - 12 - rendered.get_width())
    surface.blit(rendered, (text_x, NICKNAME_RECT.y + 8))
    surface.set_clip(previous_clip)
    if error:
        draw_text(surface, font, error, 246, ENEMY_COLOR)
    draw_button(surface, font, START_BUTTON, "Начать игру")
    draw_button(surface, font, LEADERBOARD_BUTTON, "Топ-5 игроков")
    draw_text(surface, font, f"Монета: +{COIN_SCORE} очков. Для победы: {WIN_SCORE}.", 430)
    draw_text(surface, font, "У вас 3 жизни. После урона — 1 секунда защиты.", 467, MUTED_COLOR)
    draw_text(surface, font, "Стрелки — движение · Enter — старт · ESC — меню", 510, MUTED_COLOR)


def draw_game_hud(
    surface: pygame.Surface, font: pygame.font.Font, nickname: str, score: int,
    lives: int, elapsed_ms: int,
) -> None:
    surface.blit(font.render(f"Игрок: {nickname}", True, TEXT_COLOR), (20, 16))
    surface.blit(font.render(f"Жизни: {lives}", True, TEXT_COLOR), (640, 16))
    label = (
        f"Очки: {score} / {WIN_SCORE}   До победы: {max(0, WIN_SCORE - score)}"
        f"   Время: {elapsed_ms / 1000:.3f} с"
    )
    surface.blit(font.render(label, True, TEXT_COLOR), (20, 55))
    surface.blit(font.render("ESC — меню", True, MUTED_COLOR), (640, 55))


def draw_scores(
    surface: pygame.Surface, font: pygame.font.Font, scores: list[tuple[str, int]], y: int
) -> None:
    if not scores:
        draw_text(surface, font, "Побед с записанным временем пока нет", y, MUTED_COLOR)
    for place, (nickname, duration_ms) in enumerate(scores, start=1):
        row_y = y + (place - 1) * 36
        previous_clip = surface.get_clip()
        surface.set_clip(pygame.Rect(190, row_y, 300, 36))
        surface.blit(font.render(f"{place}.  {nickname.capitalize()}", True, TEXT_COLOR), (190, row_y))
        surface.set_clip(previous_clip)
        rendered = font.render(f"{duration_ms / 1000:.3f} с", True, TEXT_COLOR)
        surface.blit(rendered, rendered.get_rect(topright=(650, row_y)))


def draw_game_over(
    surface: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    nickname: str,
    score: int,
    is_win: bool,
    scores: list[tuple[str, int]],
    elapsed_ms: int,
) -> None:
    draw_text(surface, title_font, "Победа!" if is_win else "Поражение!", 55)
    draw_text(surface, font, f"Игрок: {nickname}", 125)
    draw_text(surface, font, f"Итоговый счёт: {score}", 165)
    draw_text(surface, font, f"Время партии: {elapsed_ms / 1000:.3f} с", 200)
    draw_text(surface, font, "Топ-5: быстрее всех до 100 очков", 245, MUTED_COLOR)
    draw_scores(surface, font, scores, 280)
    draw_text(surface, font, "R — начать новую игру · ESC — главное меню", 475, MUTED_COLOR)
    draw_button(surface, font, MENU_BUTTON, "В главное меню")


def draw_leaderboard(
    surface: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    scores: list[tuple[str, int]],
) -> None:
    draw_text(surface, title_font, "Топ-5 игроков", 75)
    draw_text(surface, font, "Время сбора 100 очков · меньше — лучше", 135, MUTED_COLOR)
    draw_scores(surface, font, scores, 180)
    draw_text(surface, font, "ESC — вернуться в главное меню", 470, MUTED_COLOR)
    draw_button(surface, font, MENU_BUTTON, "В главное меню")
