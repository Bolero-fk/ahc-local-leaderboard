from typing import Optional

import pytest
from rich.text import Text

from ahc_local_leaderboard.view.score_formatter import ScoreFormatter


@pytest.mark.parametrize("value", [None, -100000, -1, 0, 1, 100000])
def test_format_optional_int(value: Optional[int]) -> None:
    assert ScoreFormatter.format_optional_int(value) == Text(str(value), style=ScoreFormatter.DEFAULT_STYLE)


@pytest.mark.parametrize("score", [0, 1, 100000])
@pytest.mark.parametrize("invalid_count", [0, 1, 100000])
def test_format_total_absolute_score(score: int, invalid_count: int) -> None:

    result = ScoreFormatter.format_total_absolute_score(total_absolute_score=score, invalid_score_count=invalid_count)

    expected_text = Text(str(score), style=ScoreFormatter.DEFAULT_STYLE)
    if 0 < invalid_count:
        expected_text.append(f" ({invalid_count})", style=ScoreFormatter.ERROR_STYLE)

    assert result == expected_text


@pytest.mark.parametrize("score", [-100000, -1])
@pytest.mark.parametrize("invalid_count", [-100000, -1])
def test_format_total_absolute_score_assertions(score: int, invalid_count: int) -> None:
    with pytest.raises(AssertionError):
        ScoreFormatter.get_relative_score_color(score, invalid_count)


@pytest.mark.parametrize("score", [None, -100000, -1, 0, 1, 100000])
def test_format_absolute_score(score: Optional[int]) -> None:
    assert ScoreFormatter.format_absolute_score(score) == Text(str(score), style=ScoreFormatter.DEFAULT_STYLE)


def _test_red_increases_when_score_decreases(max_score: int, threshold_ratio: float) -> None:
    color_thr = int(max_score * threshold_ratio)

    previous_red = ScoreFormatter.get_relative_score_color(color_thr, max_score).get_truecolor().red

    for score in range(color_thr - 1, -1, -10):
        color = ScoreFormatter.get_relative_score_color(score, max_score)
        current_red = color.get_truecolor().red
        assert current_red >= previous_red
        previous_red = current_red


def _test_green_increases_when_score_increases(max_score: int, threshold_ratio: float) -> None:
    color_thr = int(max_score * threshold_ratio)

    previous_green = ScoreFormatter.get_relative_score_color(color_thr, max_score).get_truecolor().green

    for score in range(color_thr + 1, max_score + 1, 10):
        color = ScoreFormatter.get_relative_score_color(score, max_score)
        current_green = color.get_truecolor().green
        assert current_green >= previous_green
        previous_green = current_green


@pytest.mark.parametrize("max_score", [0, 1, 100000])
@pytest.mark.parametrize("threshold_ratio", [0, 0.1, 0.75, 1])
def test_get_relative_score_color(max_score: int, threshold_ratio: float) -> None:
    _test_red_increases_when_score_decreases(max_score, threshold_ratio)
    _test_green_increases_when_score_increases(max_score, threshold_ratio)


def test_get_relative_score_color_assertions() -> None:
    max_score = 100

    with pytest.raises(AssertionError):
        ScoreFormatter.get_relative_score_color(-10, max_score)

    with pytest.raises(AssertionError):
        ScoreFormatter.get_relative_score_color(max_score + 10, max_score)

    with pytest.raises(AssertionError):
        ScoreFormatter.get_relative_score_color(max_score - 10, max_score, threshold_ratio=1.1)


@pytest.mark.parametrize("score", [0, 1, 100000])
@pytest.mark.parametrize("max_score", [0, 1, 100000])
def test_format_relative_score(score: int, max_score: int) -> None:

    if score <= max_score:
        result = ScoreFormatter.format_relative_score(score, max_score)
        assert isinstance(result, Text)
        assert result.plain == str(score)
    else:
        with pytest.raises(AssertionError):
            ScoreFormatter.format_relative_score(score, max_score)


@pytest.mark.parametrize("score1", [None, -100000, -1, 0, 1, 100000])
@pytest.mark.parametrize("score2", [None, -100000, -1, 0, 1, 100000])
def test_format_score_diff(score1: Optional[int], score2: Optional[int]) -> None:

    result = ScoreFormatter.format_score_diff(score1, score2)
    if score1 is not None and score2 is not None:
        assert result == Text(str(abs(score1 - score2)), style=ScoreFormatter.DEFAULT_STYLE)
    else:
        assert result == Text("None", style=ScoreFormatter.ERROR_STYLE)


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
def test_format_test_case_input(input: str) -> None:
    result = ScoreFormatter.format_test_case_input("test_case")
    assert isinstance(result, Text)
    assert result.plain == "test_case"
