from unittest.mock import Mock

import pytest

from ahc_local_leaderboard.models.sort_config import (
    DetailScoreRecordsSortConfig,
    SummaryScoreRecordsSortConfig,
)
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


@pytest.fixture
def mock_relative_score_calculator() -> Mock:
    return Mock(spec=RelativeScoreCalculaterInterface)


@pytest.mark.parametrize("column", ["id", "rank", "time", "abs", "rel"])
@pytest.mark.parametrize("order", ["asc", "desc"])
def test_summary_records_sort_config_initialization(column: str, order: str) -> None:
    sort_config = SummaryScoreRecordsSortConfig(column, order)
    assert sort_config.column == column
    assert sort_config.order == order


@pytest.mark.parametrize("column", ["name", ""])
@pytest.mark.parametrize("order", ["", "dsc"])
def test_summary_records_sort_config_initialization_assertions(column: str, order: str) -> None:
    with pytest.raises(AssertionError):
        SummaryScoreRecordsSortConfig(column, order)


@pytest.mark.parametrize("column", ["id", "abs", "rel"])
@pytest.mark.parametrize("order", ["asc", "desc"])
def test_detail_records_sort_config_initialization(
    column: str, order: str, mock_relative_score_calculator: Mock
) -> None:
    sort_config = DetailScoreRecordsSortConfig(column, order, mock_relative_score_calculator)
    assert sort_config.column == column
    assert sort_config.order == order


@pytest.mark.parametrize("column", ["name", "", "time", "rel"])
@pytest.mark.parametrize("order", ["", "dsc"])
def test_detail_records_sort_config_initialization_assertions(
    column: str, order: str, mock_relative_score_calculator: Mock
) -> None:
    with pytest.raises(AssertionError):
        DetailScoreRecordsSortConfig(column, order, mock_relative_score_calculator)
