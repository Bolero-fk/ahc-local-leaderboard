from typing import Optional

import pytest

from ahc_local_leaderboard.utils.relative_score_calculater import (
    MaximizationScoring,
    MinimizationScoring,
    RelativeScoreCalculaterInterface,
    get_relative_score_calculator,
)


@pytest.mark.parametrize("score", [None, -100, 0, 500, 1000])
@pytest.mark.parametrize("top_score", [None, -100, 0, 500, 1000])
def test_maximization_calculate_relative_score(score: Optional[int], top_score: Optional[int]) -> None:
    maximization = MaximizationScoring()

    if not isinstance(top_score, int):
        assert maximization(score, top_score) == RelativeScoreCalculaterInterface.MAX_SCORE
    elif not isinstance(score, int):
        assert maximization(score, top_score) == RelativeScoreCalculaterInterface.MIN_SCORE
    elif score <= 0 or top_score <= 0:
        with pytest.raises(AssertionError):
            maximization(score, top_score)
    elif score > top_score:
        with pytest.raises(AssertionError):
            maximization(score, top_score)
    else:
        assert maximization(score, top_score) == round(RelativeScoreCalculaterInterface.MAX_SCORE * score / top_score)


@pytest.mark.parametrize("score", [None, -100, 0, 500, 1000])
@pytest.mark.parametrize("top_score", [None, -100, 0, 500, 1000])
def test_minimization_calculate_relative_score(score: Optional[int], top_score: Optional[int]) -> None:
    minimization = MinimizationScoring()

    if not isinstance(top_score, int):
        assert minimization(score, top_score) == RelativeScoreCalculaterInterface.MAX_SCORE
    elif not isinstance(score, int):
        assert minimization(score, top_score) == RelativeScoreCalculaterInterface.MIN_SCORE
    elif score <= 0 or top_score <= 0:
        with pytest.raises(AssertionError):
            minimization(score, top_score)
    elif score < top_score:
        with pytest.raises(AssertionError):
            minimization(score, top_score)
    else:
        assert minimization(score, top_score) == round(RelativeScoreCalculaterInterface.MAX_SCORE * top_score / score)


@pytest.mark.parametrize("a", [None, -100, 0, 500, 1000])
@pytest.mark.parametrize("b", [None, -100, 0, 500, 1000])
def test_maximization_is_better_score(a: Optional[int], b: Optional[int]) -> None:
    maximization = MaximizationScoring()

    if not isinstance(b, int):
        assert maximization.is_better_score(a, b)
    elif not isinstance(a, int):
        assert not maximization.is_better_score(a, b)
    else:
        assert maximization.is_better_score(a, b) == (a > b)


@pytest.mark.parametrize("a", [None, -100, 0, 500, 1000])
@pytest.mark.parametrize("b", [None, -100, 0, 500, 1000])
def test_minimization_is_better_score(a: Optional[int], b: Optional[int]) -> None:
    minimization = MinimizationScoring()

    if not isinstance(b, int):
        assert minimization.is_better_score(a, b)
    elif not isinstance(a, int):
        assert not minimization.is_better_score(a, b)
    else:
        assert minimization.is_better_score(a, b) == (a < b)


@pytest.mark.parametrize("scoring_type", ["Maximization", "Minimization", "", "$%'-_@{}~`!#()'."])
def test_get_relative_score(scoring_type: str) -> None:

    if scoring_type == "Maximization":
        assert isinstance(get_relative_score_calculator(scoring_type), MaximizationScoring)
    elif scoring_type == "Minimization":
        assert isinstance(get_relative_score_calculator(scoring_type), MinimizationScoring)
    else:
        with pytest.raises(AssertionError):
            get_relative_score_calculator(scoring_type)
