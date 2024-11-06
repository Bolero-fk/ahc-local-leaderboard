from unittest.mock import Mock, patch

import pytest

from ahc_local_leaderboard.utils.relative_score_calculater import (
    MaximizationScoring,
    MinimizationScoring,
    RelativeScoreCalculaterInterface,
    get_relative_score_calculator,
)


def test_maximization_calculate_relative_score() -> None:
    maximization = MaximizationScoring()

    # 正常な計算
    assert maximization.calculate_relative_score(500, 1000) == 500_000_000
    assert maximization.calculate_relative_score(500, 500) == RelativeScoreCalculaterInterface.MAX_SCORE
    assert maximization.calculate_relative_score(None, 1000) == RelativeScoreCalculaterInterface.MIN_SCORE
    assert maximization.calculate_relative_score(500, None) == RelativeScoreCalculaterInterface.MAX_SCORE

    # 無効な比較の場合
    with pytest.raises(ValueError, match="Invalid top score"):
        maximization.calculate_relative_score(500, 400)


def test_minimization_calculate_relative_score() -> None:
    minimization = MinimizationScoring()

    # 正常な計算
    assert minimization.calculate_relative_score(1000, 500) == 500_000_000
    assert minimization.calculate_relative_score(500, 500) == RelativeScoreCalculaterInterface.MAX_SCORE
    assert minimization.calculate_relative_score(None, 1000) == RelativeScoreCalculaterInterface.MIN_SCORE
    assert minimization.calculate_relative_score(500, None) == RelativeScoreCalculaterInterface.MAX_SCORE

    # 無効な比較の場合
    with pytest.raises(ValueError, match="Invalid top score"):
        minimization.calculate_relative_score(500, 600)


def test_maximization_is_better_score() -> None:
    maximization = MaximizationScoring()

    # 比較が正しく行われるかの確認
    assert maximization.is_better_score(600, 500) is True
    assert maximization.is_better_score(400, 500) is False
    assert maximization.is_better_score(500, 500) is False
    assert maximization.is_better_score(500, None) is True
    assert maximization.is_better_score(None, 500) is False
    assert maximization.is_better_score(None, None) is True


def test_minimization_is_better_score() -> None:
    minimization = MinimizationScoring()

    # 比較が正しく行われるかの確認
    assert minimization.is_better_score(600, 500) is False
    assert minimization.is_better_score(400, 500) is True
    assert minimization.is_better_score(500, 500) is False
    assert minimization.is_better_score(500, None) is True
    assert minimization.is_better_score(None, 500) is False
    assert minimization.is_better_score(None, None) is True


@patch("ahc_local_leaderboard.utils.validator.Validator.validate_scoring_type", return_value=True)
def test_get_relative_score(mock_validator: Mock) -> None:
    max_calculator = get_relative_score_calculator("Maximization")
    assert isinstance(max_calculator, MaximizationScoring)

    min_calculator = get_relative_score_calculator("Minimization")
    assert isinstance(min_calculator, MinimizationScoring)

    mock_validator.return_value = False
    with pytest.raises(ValueError, match="Not Found Scoring Type"):
        get_relative_score_calculator("InvalidType")
