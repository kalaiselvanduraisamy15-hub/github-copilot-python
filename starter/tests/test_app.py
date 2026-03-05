import sqlite3
from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
import app as sudoku_app
import sudoku_logic


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test_scores.db"
    sudoku_app.DB_PATH = str(db_file)
    sudoku_app.init_db()

    sudoku_app.CURRENT["puzzle"] = None
    sudoku_app.CURRENT["solution"] = None
    sudoku_app.CURRENT["difficulty"] = "medium"
    sudoku_app.CURRENT["start_time"] = None
    sudoku_app.CURRENT["hints_used"] = 0

    sudoku_app.app.config["TESTING"] = True
    with sudoku_app.app.test_client() as test_client:
        yield test_client


def test_new_game_returns_board_and_difficulty(client):
    response = client.get("/new?difficulty=hard")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["difficulty"] == "hard"
    assert len(payload["puzzle"]) == 9
    assert all(len(row) == 9 for row in payload["puzzle"])


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_generated_puzzle_has_unique_solution(client, difficulty):
    response = client.get(f"/new?difficulty={difficulty}")
    assert response.status_code == 200

    puzzle = response.get_json()["puzzle"]
    count = sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle), limit=2)
    assert count == 1


def test_check_fails_without_game(client):
    response = client.post("/check", json={"board": [[0] * 9 for _ in range(9)]})
    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_check_solved_board_returns_solved_true(client):
    client.get("/new?difficulty=easy")
    solved_board = sudoku_app.CURRENT["solution"]

    response = client.post("/check", json={"board": solved_board})
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["solved"] is True
    assert payload["incorrect"] == []


def test_hint_returns_cell_and_increments_usage(client):
    client.get("/new?difficulty=medium")
    board = [[0] * 9 for _ in range(9)]

    response = client.post("/hint", json={"board": board})
    assert response.status_code == 200

    payload = response.get_json()
    assert {"row", "col", "value", "hints_used"}.issubset(payload.keys())
    assert payload["hints_used"] == 1
    assert 0 <= payload["row"] < 9
    assert 0 <= payload["col"] < 9
    assert 1 <= payload["value"] <= 9


def test_score_submission_and_scores_endpoint(client):
    client.get("/new?difficulty=hard")
    solved_board = sudoku_app.CURRENT["solution"]

    score_response = client.post("/score", json={"name": "Tester", "board": solved_board})
    assert score_response.status_code == 200

    score_payload = score_response.get_json()
    assert score_payload["name"] == "Tester"
    assert score_payload["difficulty"] == "hard"

    list_response = client.get("/scores")
    assert list_response.status_code == 200
    scores = list_response.get_json()["scores"]
    assert any(row["name"] == "Tester" and row["difficulty"] == "hard" for row in scores)

    conn = sqlite3.connect(sudoku_app.DB_PATH)
    try:
        count = conn.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
        assert count >= 1
    finally:
        conn.close()
