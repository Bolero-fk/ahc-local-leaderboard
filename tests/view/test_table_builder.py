from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    TopDetailScoreRecord,
)
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    TopSummaryScoreRecord,
)
from ahc_local_leaderboard.utils.console_handler import ConsoleHandler
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)
from ahc_local_leaderboard.view.table_builder import (
    DetailTableBuilder,
    SummaryTableBuilder,
    TopDetailTableBuilder,
)


@pytest.fixture
def setup_console_handler_mock() -> None:
    ConsoleHandler.console = MagicMock()


@pytest.fixture
def mock_relative_score_calculator() -> RelativeScoreCalculaterInterface:
    return MagicMock(spec=RelativeScoreCalculaterInterface)


@pytest.mark.parametrize(
    "id, total_absolute_score, total_relative_score, invalid_score_count, relative_rank, max_diff",
    [
        (1, 0, 0, 0, None, 0),
        (1000, 100000, 100000, 100000, 1, 1),
    ],
)
def test_summary_table_builder_insert_record(
    id: int,
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
    relative_rank: int,
    max_diff: int,
    setup_console_handler_mock: None,
) -> None:
    record = SummaryScoreRecord(
        id=id,
        submission_time=datetime.now(),
        total_absolute_score=total_absolute_score,
        total_relative_score=total_relative_score,
        invalid_score_count=invalid_score_count,
        relative_rank=relative_rank,
    )

    builder = SummaryTableBuilder("Test Summary Table", max_relative_score=total_relative_score + max_diff)
    builder.insert_record(record)
    builder.display()

    ConsoleHandler.console.print.assert_called_once()


@pytest.mark.parametrize(
    "total_absolute_score, total_relative_score, invalid_score_count, max_diff",
    [
        (0, 0, 0, 0),
        (100000, 100000, 100000, 1),
    ],
)
def test_summary_table_builder_insert_top_record(
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
    max_diff: int,
    setup_console_handler_mock: None,
) -> None:
    record = TopSummaryScoreRecord(
        total_absolute_score=total_absolute_score,
        total_relative_score=total_relative_score,
        invalid_score_count=invalid_score_count,
    )

    builder = SummaryTableBuilder("Test Top Summary Table", max_relative_score=total_relative_score + max_diff)
    builder.insert_top_record(record)
    builder.display()

    ConsoleHandler.console.print.assert_called_once()


@pytest.mark.parametrize(
    "file_name, absolute_score, top_score",
    [
        ("0000.txt", 0, 0),
        ("$%'-_@{}~`!#()'.", 100000, 100000),
    ],
)
def test_detail_table_builder_insert_record(
    file_name: str,
    absolute_score: int,
    top_score: int,
    setup_console_handler_mock: None,
    mock_relative_score_calculator: Mock,
) -> None:
    record = DetailScoreRecord(file_name=file_name, absolute_score=absolute_score, top_score=top_score)

    mock_relative_score_calculator.return_value = 700

    builder = DetailTableBuilder(
        "Test Detail Table", max_relative_score=1000, relative_score_calculator=mock_relative_score_calculator
    )
    builder.insert_record(record)
    builder.display()

    mock_relative_score_calculator.assert_called_once_with(record.absolute_score, record.top_score)
    ConsoleHandler.console.print.assert_called_once()


@pytest.mark.parametrize(
    "file_name, top_score, submittion_id",
    [
        ("0000.txt", 0, 1),
        ("$%'-_@{}~`!#()'.", 100000, 100000),
    ],
)
def test_top_detail_table_builder_insert_record(
    file_name: str, top_score: int, submittion_id: int, setup_console_handler_mock: None
) -> None:
    record = TopDetailScoreRecord(file_name=file_name, top_score=top_score, submittion_id=submittion_id)

    builder = TopDetailTableBuilder("Test Top Detail Table")
    builder.insert_record(record)
    builder.display()

    ConsoleHandler.console.print.assert_called_once()
