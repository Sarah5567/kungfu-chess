import pytest
from unittest.mock import MagicMock
from Score import Score

def test_score_initial_value():
    score = Score()
    assert score.score == 0

@pytest.mark.parametrize("captured_type, expected_score", [
    ("P", 1),
    ("B", 3),
    ("N", 3),
    ("R", 5),
    ("Q", 9),
    ("K", 0),
])
def test_score_update_score_adds_correct_value(captured_type, expected_score):
    event = MagicMock()
    event.data = {"captured_piece": captured_type + "x"}  # כל מחרוזת שמתחילה באות המתאימה

    score = Score()
    score.update_score(event)

    assert score.score == expected_score

def test_score_accumulates_score_correctly():
    score = Score()

    event1 = MagicMock()
    event1.data = {"captured_piece": "P1"}

    event2 = MagicMock()
    event2.data = {"captured_piece": "Q5"}

    score.update_score(event1)
    score.update_score(event2)

    assert score.score == 1 + 9
