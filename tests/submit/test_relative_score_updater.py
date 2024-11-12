from typing import cast
from unittest.mock import Mock, patch

import pytest

from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    SummaryScoreRecords,
)
from ahc_local_leaderboard.submit.relative_score_updater import RelativeScoreUpdater
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


@pytest.fixture
def mock_record_read_service() -> Mock:
    return Mock(spec=RecordReadService)


@pytest.fixture
def mock_record_write_service() -> Mock:
    return Mock(spec=RecordWriteService)


@pytest.fixture
def mock_relative_score_calculator() -> Mock:
    return Mock(spec=RelativeScoreCalculaterInterface)


@pytest.mark.parametrize("file_name", ["test_case"])
@pytest.mark.parametrize("id", [1])
@pytest.mark.parametrize("abs_score", [10])
@pytest.mark.parametrize("top_score", [100])
@pytest.mark.parametrize("prev_score", [90])
@pytest.mark.parametrize("score_diff", [-10, 0, 10])
def test_calculate_individual_relative_score_diff(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    file_name: str,
    id: int,
    abs_score: int,
    top_score: int,
    prev_score: int,
    score_diff: int,
) -> None:

    updater = RelativeScoreUpdater(mock_record_read_service, mock_record_write_service, mock_relative_score_calculator)

    non_latest_record = Mock(spec=SummaryScoreRecord)
    non_latest_record.id = id
    updated_top_score = (file_name, top_score, prev_score)

    mock_record_read_service.fetch_absolute_score.return_value = abs_score
    mock_relative_score_calculator.calculate_diff_relative_score.return_value = score_diff

    result = updater.calculate_individual_relative_score_diff(non_latest_record, updated_top_score)

    assert result == score_diff
    mock_record_read_service.fetch_absolute_score.assert_called_once_with(file_name, id)
    mock_relative_score_calculator.calculate_diff_relative_score.assert_called_once_with(
        abs_score, top_score, prev_score
    )


@pytest.mark.parametrize("score_diffs", [{}, {10}, {-100, 10, 0}, {1, 10, 100}])
def test_calculate_total_relative_score_diff(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    score_diffs: list[int],
) -> None:

    updater = RelativeScoreUpdater(mock_record_read_service, mock_record_write_service, mock_relative_score_calculator)
    non_latest_record = Mock(spec=SummaryScoreRecord)
    updated_top_scores = [("test_case_1", 100, 90) for _ in score_diffs]

    with patch.object(updater, "calculate_individual_relative_score_diff", side_effect=score_diffs) as mock_cal_diff:

        result = updater.calculate_total_relative_score_diff(non_latest_record, updated_top_scores)

        assert result == sum(score_diffs)
        assert mock_cal_diff.call_count == len(score_diffs)


@pytest.mark.parametrize(
    "initial_scores, diff_scores",
    [
        ([1, 10, 100], [20, 30, -10]),
    ],
)
def test_update_relative_scores(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    initial_scores: list[int],
    diff_scores: list[int],
) -> None:

    updater = RelativeScoreUpdater(mock_record_read_service, mock_record_write_service, mock_relative_score_calculator)

    records = [Mock(spec=SummaryScoreRecord, total_relative_score=score) for score in initial_scores]

    with patch.object(updater, "calculate_total_relative_score_diff", side_effect=diff_scores):

        updater.update_relative_scores(cast(list[SummaryScoreRecord], records))  # mypy用のcast

        expected_scores = [initial + diff for initial, diff in zip(initial_scores, diff_scores)]
        actual_scores = [record.total_relative_score for record in records]

        assert actual_scores == expected_scores


@pytest.mark.parametrize("count_remaining_records", [0, 1, 10])
def test_fetch_latest_and_remaining_records(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    count_remaining_records: int,
) -> None:

    updater = RelativeScoreUpdater(mock_record_read_service, mock_record_write_service, mock_relative_score_calculator)

    latest_record = Mock(spec=SummaryScoreRecord)
    remaining_records = [Mock(spec=SummaryScoreRecord) for _ in range(count_remaining_records)]
    all_records = Mock(spec=SummaryScoreRecords)

    all_records.get_latest_record.return_value = latest_record
    all_records.get_records_except_latest.return_value = remaining_records
    mock_record_read_service.fetch_all_summary_records.return_value = all_records

    result_latest, result_remaining = updater.fetch_latest_and_remaining_records()

    assert result_latest == latest_record
    assert result_remaining == remaining_records


def test_apply_relative_score_updates(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
) -> None:

    updater = RelativeScoreUpdater(mock_record_read_service, mock_record_write_service, mock_relative_score_calculator)
    latest_record = Mock(spec=SummaryScoreRecord, total_relative_score=0)
    remaining_records = [Mock(spec=SummaryScoreRecord)]

    mock_record_write_service.update_score_history = Mock()
    mock_record_write_service.reset_is_updated_flags = Mock()

    with patch(
        "ahc_local_leaderboard.submit.relative_score_updater.SummaryScoreRecords"
    ) as mock_summary_score_records, patch.object(
        updater,
        "fetch_latest_and_remaining_records",
        return_value=(latest_record, remaining_records),
    ) as mock_fetch, patch.object(
        updater, "update_relative_scores", return_value=Mock()
    ) as mock_update:

        mock_updated_records = mock_summary_score_records.return_value
        mock_updated_records.__iter__.return_value = iter([latest_record] + remaining_records)
        mock_updated_records.update_relative_ranks = Mock()
        mock_updated_records.add_record = Mock()

        updater.apply_relative_score_updates()

        mock_fetch.assert_called_once()
        mock_update.assert_called_once_with(remaining_records)
        mock_updated_records.add_record.assert_called_once_with(latest_record)
        mock_updated_records.update_relative_ranks.assert_called_once()
        mock_record_write_service.update_score_history.assert_called()
        mock_record_write_service.reset_is_updated_flags.assert_called_once()
