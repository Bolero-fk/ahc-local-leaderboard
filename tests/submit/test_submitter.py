from unittest.mock import Mock

import pytest

from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.models.test_case import TestCases
from ahc_local_leaderboard.models.test_file import TestFiles
from ahc_local_leaderboard.submit.relative_score_updater import RelativeScoreUpdater
from ahc_local_leaderboard.submit.reserved_record_updater import ReservedRecordUpdater
from ahc_local_leaderboard.submit.submission_matcher import SubmissionMatcher
from ahc_local_leaderboard.submit.submitter import Submitter
from ahc_local_leaderboard.submit.test_case_processor import TestCasesProcessor
from ahc_local_leaderboard.submit.test_file_processor import TestFilesProcessor


@pytest.fixture
def mock_record_write_service() -> Mock:
    return Mock(spec=RecordWriteService)


@pytest.fixture
def mock_test_files_processor() -> Mock:
    return Mock(spec=TestFilesProcessor)


@pytest.fixture
def mock_test_cases_processor() -> Mock:
    return Mock(spec=TestCasesProcessor)


@pytest.fixture
def mock_reserved_record_updater() -> Mock:
    return Mock(spec=ReservedRecordUpdater)


@pytest.fixture
def mock_relative_score_updater() -> Mock:
    return Mock(spec=RelativeScoreUpdater)


@pytest.fixture
def mock_test_files() -> Mock:
    return Mock(spec=TestFiles)


@pytest.fixture
def mock_test_cases() -> Mock:
    return Mock(spec=TestCases)


@pytest.fixture
def mock_reserved_record() -> Mock:
    return Mock(spec=SummaryScoreRecord)


@pytest.fixture
def mock_submission_matcher() -> Mock:
    return Mock(spec=SubmissionMatcher)


@pytest.mark.parametrize("skip_duplicate", [False, True])
def test_submitter_execute_calls_in_order(
    mock_record_write_service: Mock,
    mock_test_files_processor: Mock,
    mock_test_cases_processor: Mock,
    mock_reserved_record_updater: Mock,
    mock_relative_score_updater: Mock,
    mock_test_files: Mock,
    mock_test_cases: Mock,
    mock_reserved_record: Mock,
    mock_submission_matcher: Mock,
    skip_duplicate: bool,
) -> None:
    submitter = Submitter(
        record_write_service=mock_record_write_service,
        test_files_processor=mock_test_files_processor,
        test_case_processor=mock_test_cases_processor,
        reserved_record_updater=mock_reserved_record_updater,
        relative_score_updater=mock_relative_score_updater,
        submission_matcher=mock_submission_matcher,
    )

    mock_test_files_processor.process_test_files.return_value = mock_test_cases
    mock_record_write_service.reserve_empty_score_history_record.return_value = mock_reserved_record
    mock_reserved_record.id = 1
    mock_submission_matcher.is_submission_already_recorded.return_value = False

    result = submitter.execute(mock_test_files, skip_duplicate)

    if skip_duplicate:
        mock_submission_matcher.is_submission_already_recorded.assert_called_once()
    else:
        mock_submission_matcher.is_submission_already_recorded.assert_not_called()

    mock_test_files_processor.process_test_files.assert_called_once_with(mock_test_files)
    mock_record_write_service.reserve_empty_score_history_record.assert_called_once()
    mock_test_cases_processor.process_test_cases.assert_called_once_with(mock_test_cases, mock_reserved_record.id)
    mock_reserved_record_updater.update_reserved_record.assert_called_once_with(mock_reserved_record)
    mock_relative_score_updater.apply_relative_score_updates.assert_called_once()
    assert result is True


@pytest.mark.parametrize("skip_duplicate", [False, True])
def test_submitter_execute_already_exists_submission(
    mock_record_write_service: Mock,
    mock_test_files_processor: Mock,
    mock_test_cases_processor: Mock,
    mock_reserved_record_updater: Mock,
    mock_relative_score_updater: Mock,
    mock_test_files: Mock,
    mock_test_cases: Mock,
    mock_reserved_record: Mock,
    mock_submission_matcher: Mock,
    skip_duplicate: bool,
) -> None:
    submitter = Submitter(
        record_write_service=mock_record_write_service,
        test_files_processor=mock_test_files_processor,
        test_case_processor=mock_test_cases_processor,
        reserved_record_updater=mock_reserved_record_updater,
        relative_score_updater=mock_relative_score_updater,
        submission_matcher=mock_submission_matcher,
    )

    mock_test_files_processor.process_test_files.return_value = mock_test_cases
    mock_record_write_service.reserve_empty_score_history_record.return_value = mock_reserved_record
    mock_reserved_record.id = 1
    mock_submission_matcher.is_submission_already_recorded.return_value = True

    result = submitter.execute(mock_test_files, skip_duplicate)

    if skip_duplicate:
        mock_test_files_processor.process_test_files.assert_called_once_with(mock_test_files)
        mock_submission_matcher.is_submission_already_recorded.assert_called_once()
        mock_record_write_service.reserve_empty_score_history_record.assert_not_called()
        mock_test_cases_processor.process_test_cases.assert_not_called()
        mock_reserved_record_updater.update_reserved_record.assert_not_called()
        mock_relative_score_updater.apply_relative_score_updates.assert_not_called()
        assert result is False
    else:
        mock_test_files_processor.process_test_files.assert_called_once_with(mock_test_files)
        mock_submission_matcher.is_submission_already_recorded.assert_not_called()
        mock_record_write_service.reserve_empty_score_history_record.assert_called_once()
        mock_test_cases_processor.process_test_cases.assert_called_once_with(mock_test_cases, mock_reserved_record.id)
        mock_reserved_record_updater.update_reserved_record.assert_called_once_with(mock_reserved_record)
        mock_relative_score_updater.apply_relative_score_updates.assert_called_once()
        assert result is True
