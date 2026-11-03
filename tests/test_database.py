import sqlite3
from pathlib import Path

from coin_collector.database import Database


def test_database_created_on_first_use(tmp_path: Path) -> None:
    path = tmp_path / "data" / "scores.db"
    assert not path.exists()
    database = Database(path)
    assert path.is_file()
    assert database.get_top_scores() == []


def test_saved_score_survives_reopening(tmp_path: Path) -> None:
    path = tmp_path / "scores.db"
    database = Database(path)
    nickname = "О'Брайен'); DROP TABLE scores; --"
    database.save_score(nickname, 100, True, 12345)
    reopened = Database(path)
    assert reopened.get_top_scores() == [(nickname.lower(), 12345)]
    reopened.save_score("игрок", 100, True, 23456)
    assert reopened.get_top_scores() == [(nickname.lower(), 12345), ("игрок", 23456)]


def test_top_five_sorted_by_fastest_win_then_earliest_result(tmp_path: Path) -> None:
    database = Database(tmp_path / "scores.db")
    for name, duration in [
        ("медленный", 90000), ("первый", 20000), ("быстрый", 10000),
        ("второй", 20000), ("третий", 20000), ("средний", 30000),
        ("последний", 100000),
    ]:
        database.save_score(name, 100, True, duration)
    assert database.get_top_scores() == [
        ("быстрый", 10000), ("первый", 20000), ("второй", 20000),
        ("третий", 20000), ("средний", 30000),
    ]
    assert database.get_top_scores(2) == [("быстрый", 10000), ("первый", 20000)]
    assert len(database.get_top_scores(100)) == 5


def test_only_best_time_per_nickname_is_ranked(tmp_path: Path) -> None:
    database = Database(tmp_path / "scores.db")
    for duration in [12435, 9742, 10767, 14571, 9742]:
        database.save_score("максим", 100, True, duration)
    database.save_score("анна", 100, True, 11000)
    database.save_score("максим", 90, False, 1000)
    assert database.get_top_scores() == [("максим", 9742), ("анна", 11000)]
    database.save_score("анна", 100, True, 9000)
    assert database.get_top_scores() == [("анна", 9000), ("максим", 9742)]


def test_equal_personal_bests_use_order_of_best_results(tmp_path: Path) -> None:
    database = Database(tmp_path / "scores.db")
    database.save_score("первый участник", 100, True, 30000)
    database.save_score("первый рекорд", 100, True, 10000)
    database.save_score("первый участник", 100, True, 10000)
    database.save_score("первый рекорд", 100, True, 10000)
    assert database.get_top_scores() == [
        ("первый рекорд", 10000), ("первый участник", 10000),
    ]


def test_losses_and_unknown_times_are_excluded(tmp_path: Path) -> None:
    database = Database(tmp_path / "scores.db")
    database.save_score("поражение", 90, False, 1000)
    database.save_score("без времени", 100, True)
    database.save_score("победитель", 100, True, 25000)
    assert database.get_top_scores() == [("победитель", 25000)]


def test_nicknames_are_lowercased_before_saving(tmp_path: Path) -> None:
    database = Database(tmp_path / "scores.db")
    for nickname, duration in [
        ("Максим", 12435), ("МАКСИМ", 9742), (" максим ", 10767),
        ("ФЁДОР", 6732), ("Фёдор", 8000),
        ("Alice", 11000), ("ALICE", 10000),
    ]:
        database.save_score(nickname, 100, True, duration)
    assert database.get_top_scores() == [
        ("фёдор", 6732), ("максим", 9742), ("alice", 10000),
    ]


def test_existing_nicknames_are_normalized_on_reopening(tmp_path: Path) -> None:
    path = tmp_path / "scores.db"
    Database(path)
    connection = sqlite3.connect(path)
    try:
        with connection:
            connection.executemany(
                """INSERT INTO scores (nickname, score, is_win, duration_ms)
                   VALUES (?, ?, ?, ?)""",
                [("Максим", 100, 1, 9742), ("максим", 100, 1, 9990),
                 (" МАКСИМ ", 100, 1, 10767), ("ФЁДОР", 100, 1, 6732)],
            )
    finally:
        connection.close()
    expected = [("фёдор", 6732), ("максим", 9742)]
    assert Database(path).get_top_scores() == expected
    assert Database(path).get_top_scores() == expected  # Повторное открытие безопасно.
    connection = sqlite3.connect(path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM scores").fetchone() == (4,)
        assert connection.execute(
            "SELECT DISTINCT nickname FROM scores ORDER BY nickname"
        ).fetchall() == [("максим",), ("фёдор",)]
    finally:
        connection.close()


def test_legacy_database_is_migrated_without_losing_scores(tmp_path: Path) -> None:
    path = tmp_path / "scores.db"
    # Воспроизводим схему предыдущей версии приложения.
    connection = sqlite3.connect(path)
    try:
        with connection:
            connection.execute("""CREATE TABLE scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT, nickname TEXT NOT NULL,
                score INTEGER NOT NULL, is_win INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")
            connection.execute(
                "INSERT INTO scores (nickname, score, is_win) VALUES (?, ?, ?)",
                ("старый игрок", 100, 1),
            )
    finally:
        connection.close()
    database = Database(path)
    assert database.get_top_scores() == []
    database.save_score("новый игрок", 100, True, 50000)
    assert Database(path).get_top_scores() == [("новый игрок", 50000)]
    connection = sqlite3.connect(path)
    try:
        assert connection.execute(
            "SELECT nickname, duration_ms FROM scores ORDER BY id"
        ).fetchall() == [("старый игрок", None), ("новый игрок", 50000)]
    finally:
        connection.close()
