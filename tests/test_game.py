from pathlib import Path

import pygame

from coin_collector.game import Game, GameState


def test_timer_win_single_save_and_restart(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    current_time = [100.0]
    monkeypatch.setattr("coin_collector.game.perf_counter", lambda: current_time[0])
    game = Game(tmp_path / "scores.db")
    try:
        game.nickname = "Игрок"
        game.start_game()
        assert game.nickname == "игрок"
        current_time[0] = 112.345
        game.update(0.01)
        assert game.elapsed_ms == 12345  # Время не ограничено dt движения.
        game.score = 90
        game.coins[0].rect.center = game.player.rect.center
        game.update(0)
        assert game.state == GameState.GAME_OVER
        assert game.database.get_top_scores() == [("игрок", 12345)]
        current_time[0] = 200.0
        game.update(0.01)
        game.finish_game(True)
        game.draw()
        assert game.elapsed_ms == 12345
        assert game.database.get_top_scores() == [("игрок", 12345)]
        game.start_game()
        assert game.elapsed_ms == 0
        current_time[0] = 203.5
        game.update(0.01)
        assert game.elapsed_ms == 3500
        game.player.lives = 0
        game.update(0)
        assert not game.is_win
        assert game.database.get_top_scores() == [("игрок", 12345)]
        game.draw()
        game.state = GameState.LEADERBOARD
        game.draw()
    finally:
        pygame.quit()
