from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.models.test_case import TestCase


@pytest.fixture
def mock_repos() -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    database_manager = MagicMock()
    score_history_repo = MagicMock()
    test_case_repo = MagicMock()
    top_score_repo = MagicMock()
    return database_manager, score_history_repo, test_case_repo, top_score_repo


@pytest.fixture
def service(mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock]) -> RecordWriteService:
    database_manager, score_history_repo, test_case_repo, top_score_repo = mock_repos
    return RecordWriteService(database_manager, score_history_repo, test_case_repo, top_score_repo)


def test_setup_database(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock]
) -> None:
    database_manager, _, _, _ = mock_repos
    service.setup_database()
    database_manager.setup.assert_called_once()


def test_reserve_empty_score_history_record(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock]
) -> None:
    _, score_history_repo, _, _ = mock_repos
    submission_time = datetime.now()
    mock_record = Mock(spec=SummaryScoreRecord)
    score_history_repo.reserve_empty_score_history_record.return_value = mock_record

    result = service.reserve_empty_score_history_record(submission_time)
    assert result == mock_record
    score_history_repo.reserve_empty_score_history_record.assert_called_once_with(submission_time)


@pytest.mark.parametrize("submission_id", [1, 10, 100])
def test_update_score_history(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    _, score_history_repo, _, _ = mock_repos
    mock_record = Mock(SummaryScoreRecord)
    mock_record.id = submission_id

    service.update_score_history(mock_record)
    score_history_repo.update_score_history.assert_called_once_with(mock_record)


@pytest.mark.parametrize("submission_id", [-100, -10, 0])
def test_update_score_history_assertions(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    mock_record = Mock(SummaryScoreRecord)
    mock_record.id = submission_id

    with pytest.raises(AssertionError):
        service.update_score_history(mock_record)


@pytest.mark.parametrize("submission_id", [1, 10, 100])
def test_insert_test_case(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    _, _, test_case_repo, _ = mock_repos
    mock_test_case = Mock(spec=TestCase)

    service.insert_test_case(mock_test_case, submission_id)
    test_case_repo.insert_test_case.assert_called_once_with(mock_test_case, submission_id)


@pytest.mark.parametrize("submission_id", [-100, -10, 0])
def test_insert_test_case_assertions(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:

    mock_test_case = Mock(spec=TestCase)
    with pytest.raises(AssertionError):
        service.insert_test_case(mock_test_case, submission_id)


@pytest.mark.parametrize("submission_id", [1, 10, 100])
def test_update_top_score(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:
    _, _, _, top_score_repo = mock_repos
    mock_test_case = Mock(spec=TestCase)

    service.update_top_score(mock_test_case, submission_id)
    top_score_repo.update_top_score.assert_called_once_with(mock_test_case, submission_id)


@pytest.mark.parametrize("submission_id", [-100, -10, 0])
def test_update_top_score_assertions(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock], submission_id: int
) -> None:

    mock_test_case = Mock(spec=TestCase)
    with pytest.raises(AssertionError):
        service.update_top_score(mock_test_case, submission_id)


def test_reset_is_updated_flags(
    service: RecordWriteService, mock_repos: tuple[MagicMock, MagicMock, MagicMock, MagicMock]
) -> None:
    _, _, _, top_score_repo = mock_repos
    service.reset_is_updated_flags()
    top_score_repo.reset_is_updated_flags.assert_called_once()
