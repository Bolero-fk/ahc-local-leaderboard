from unittest.mock import MagicMock, Mock

import pytest

from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.models.detail_score_record import DetailScoreRecords
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    SummaryScoreRecords,
    TopSummaryScoreRecord,
)
from ahc_local_leaderboard.models.test_case import TestCase
from ahc_local_leaderboard.models.updated_top_score import UpdatedTopScore


@pytest.fixture
def mock_repos() -> tuple[MagicMock, MagicMock, MagicMock]:
    score_history_repo = MagicMock()
    test_case_repo = MagicMock()
    top_score_repo = MagicMock()
    return score_history_repo, test_case_repo, top_score_repo


@pytest.fixture
def service(mock_repos: tuple[MagicMock, MagicMock, MagicMock]) -> RecordReadService:
    score_history_repo, test_case_repo, top_score_repo = mock_repos
    return RecordReadService(score_history_repo, test_case_repo, top_score_repo)


def test_fetch_all_summary_records(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]
) -> None:
    score_history_repo, _, _ = mock_repos
    mock_data = Mock(spec=SummaryScoreRecords)
    score_history_repo.fetch_all_records.return_value = mock_data

    result = service.fetch_all_summary_records()
    assert result == mock_data
    score_history_repo.fetch_all_records.assert_called_once()


def test_fetch_latest_submission_id(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]
) -> None:

    score_history_repo, _, _ = mock_repos
    mock_data = 1
    score_history_repo.fetch_latest_id.return_value = mock_data

    result = service.fetch_latest_submission_id()
    assert result == mock_data
    score_history_repo.fetch_latest_id.assert_called_once()


@pytest.mark.parametrize("limit", [1, 10, 100])
def test_fetch_recent_summary_records(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], limit: int
) -> None:
    score_history_repo, _, _ = mock_repos
    mock_data = Mock(spec=SummaryScoreRecords)
    score_history_repo.fetch_recent_summary_records.return_value = mock_data

    result = service.fetch_recent_summary_records(limit)
    assert result == mock_data
    score_history_repo.fetch_recent_summary_records.assert_called_once_with(limit)


@pytest.mark.parametrize("limit", [-100, -10, 0])
def test_fetch_recent_summary_records_assertions(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], limit: int
) -> None:
    score_history_repo, _, _ = mock_repos
    mock_data = Mock(spec=SummaryScoreRecords)
    score_history_repo.fetch_recent_summary_records.return_value = mock_data

    with pytest.raises(AssertionError):
        service.fetch_recent_summary_records(limit)


@pytest.mark.parametrize("submission_id", [1, 10, 100])
def test_fetch_summary_record_by_id(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    score_history_repo, _, _ = mock_repos
    mock_data = Mock(spec=SummaryScoreRecord)
    score_history_repo.fetch_summary_record_by_id.return_value = mock_data

    result = service.fetch_summary_record_by_id(submission_id)
    assert result == mock_data
    score_history_repo.fetch_summary_record_by_id.assert_called_once_with(submission_id)


@pytest.mark.parametrize("submission_id", [-100, -10, 0])
def test_fetch_summary_record_by_id_assertions(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    score_history_repo, _, _ = mock_repos
    mock_data = Mock(spec=SummaryScoreRecord)
    score_history_repo.fetch_summary_record_by_id.return_value = mock_data

    with pytest.raises(AssertionError):
        service.fetch_summary_record_by_id(submission_id)


@pytest.mark.parametrize("result", [False, True])
def test_exists_id(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], result: bool
) -> None:

    score_history_repo, _, _ = mock_repos
    score_history_repo.exists_id.return_value = result
    temp_id = 1

    assert service.exists_id(temp_id) == result


@pytest.mark.parametrize("submission_id", [1, 10, 100])
def test_fetch_detail_records_by_id(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    _, test_case_repo, _ = mock_repos
    mock_data = Mock(spec=DetailScoreRecords)
    test_case_repo.fetch_records_by_id.return_value = mock_data

    result = service.fetch_detail_records_by_id(submission_id)
    assert result == mock_data
    test_case_repo.fetch_records_by_id.assert_called_once_with(submission_id)


@pytest.mark.parametrize("submission_id", [-100, -10, 0])
def test_fetch_detail_records_by_id_assertions(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    _, test_case_repo, _ = mock_repos
    mock_data = Mock(spec=DetailScoreRecords)
    test_case_repo.fetch_records_by_id.return_value = mock_data

    with pytest.raises(AssertionError):
        service.fetch_detail_records_by_id(submission_id)


@pytest.mark.parametrize("submission_id", [1, 10, 100])
def test_fetch_absolute_score_for_test_case(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    _, test_case_repo, _ = mock_repos
    mock_data = 100
    test_case_repo.fetch_absolute_score_for_test_case.return_value = mock_data

    result = service.fetch_absolute_score_for_test_case("test_case_name", submission_id)
    assert result == mock_data
    test_case_repo.fetch_absolute_score_for_test_case.assert_called_once_with("test_case_name", submission_id)


@pytest.mark.parametrize("submission_id", [-100, -10, 0])
def test_fetch_absolute_score_for_test_case_assertions(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    _, test_case_repo, _ = mock_repos
    mock_data = 100
    test_case_repo.fetch_absolute_score_for_test_case.return_value = mock_data

    with pytest.raises(AssertionError):
        service.fetch_absolute_score_for_test_case("test_case_name", submission_id)


def test_fetch_top_summary_record(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]
) -> None:
    _, _, top_score_repo = mock_repos
    mock_data = Mock(spec=TopSummaryScoreRecord)
    top_score_repo.fetch_top_summary_record.return_value = mock_data

    result = service.fetch_top_summary_record()
    assert result == mock_data
    top_score_repo.fetch_top_summary_record.assert_called_once()


def test_fetch_test_case_count(service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]) -> None:
    _, _, top_score_repo = mock_repos
    mock_data = 10
    top_score_repo.fetch_test_case_count.return_value = mock_data

    result = service.fetch_test_case_count()
    assert result == mock_data
    top_score_repo.fetch_test_case_count.assert_called_once()


def test_fetch_top_detail_records(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]
) -> None:
    _, _, top_score_repo = mock_repos
    mock_data = Mock(spec=DetailScoreRecords)
    top_score_repo.fetch_top_detail_records.return_value = mock_data

    result = service.fetch_top_detail_records()
    assert result == mock_data
    top_score_repo.fetch_top_detail_records.assert_called_once()


def test_fetch_sorted_top_detail_records(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]
) -> None:
    _, _, top_score_repo = mock_repos
    mock_data = Mock(spec=DetailScoreRecords)
    top_score_repo.fetch_top_detail_records.return_value = mock_data

    result = service.fetch_sorted_top_detail_records()
    assert result == mock_data
    top_score_repo.fetch_top_detail_records.assert_called_once()
    mock_data.sort_records_by_input_file_name.assert_called_once()


def test_fetch_top_score_for_test_case(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]
) -> None:
    _, _, top_score_repo = mock_repos
    mock_data = 200
    test_case = Mock(spec=TestCase)
    top_score_repo.fetch_top_score_for_test_case.return_value = mock_data

    result = service.fetch_top_score_for_test_case(test_case)
    assert result == mock_data
    top_score_repo.fetch_top_score_for_test_case.assert_called_once_with(test_case)


def test_fetch_recently_updated_top_scores(
    service: RecordReadService, mock_repos: tuple[MagicMock, MagicMock, MagicMock]
) -> None:
    _, _, top_score_repo = mock_repos
    mock_data = [UpdatedTopScore("file_name", 300, 250)]
    top_score_repo.fetch_recently_updated_top_scores.return_value = mock_data

    result = service.fetch_recently_updated_top_scores()
    assert result == mock_data
    top_score_repo.fetch_recently_updated_top_scores.assert_called_once()
