from pathlib import Path
from typing import Optional
from unittest.mock import Mock, patch

import pytest

from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
)
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    SummaryScoreRecords,
)
from ahc_local_leaderboard.models.test_case import TestCase, TestCases
from ahc_local_leaderboard.submit.submission_matcher import SubmissionMatcher


@pytest.fixture
def mock_record_read_service() -> Mock:
    return Mock(spec=RecordReadService)


@pytest.fixture
def mock_summary_record() -> Mock:
    return Mock(spec=SummaryScoreRecord)


@pytest.fixture
def mock_detail_record() -> Mock:
    return Mock(spec=DetailScoreRecord)


@pytest.fixture
def mock_detail_records() -> Mock:
    return Mock(spec=DetailScoreRecords[DetailScoreRecord])


@pytest.fixture
def mock_test_cases() -> Mock:
    return Mock(spec=TestCases)


@pytest.mark.parametrize("check_score", [0])
@pytest.mark.parametrize("same_score_count", [0, 1, 100])
def test_fetch_same_score_records(
    mock_record_read_service: Mock,
    mock_summary_record: Mock,
    mock_detail_records: Mock,
    same_score_count: int,
    check_score: int,
) -> None:

    mock_summary_record.id = 0
    summary_records = SummaryScoreRecords([mock_summary_record] * same_score_count)
    mock_record_read_service.fetch_records_by_absolute_score.return_value = summary_records

    mock_record_read_service.fetch_detail_records_by_id.return_value = mock_detail_records

    submission_matcher = SubmissionMatcher(record_read_service=mock_record_read_service)
    submission_matcher.fetch_same_score_records(check_score)

    mock_record_read_service.fetch_records_by_absolute_score.assert_called_once_with(check_score)
    if 0 < same_score_count:
        mock_record_read_service.fetch_detail_records_by_id.assert_called()
    else:
        mock_record_read_service.fetch_detail_records_by_id.assert_not_called()


@pytest.mark.parametrize("in_records", [False, True])
def test_is_submission_in_records(
    mock_record_read_service: Mock,
    mock_detail_record: Mock,
    mock_detail_records: Mock,
    mock_test_cases: Mock,
    in_records: bool,
) -> None:

    mock_detail_record.file_name = "test"
    mock_detail_record.absolute_score = 0
    mock_detail_records.records = [mock_detail_record]

    mock_test_cases.contains_test_case.return_value = in_records

    submission_matcher = SubmissionMatcher(record_read_service=mock_record_read_service)
    result = submission_matcher.is_submission_in_records([mock_detail_records], mock_test_cases)

    assert result is in_records
    mock_test_cases.contains_test_case.assert_called_with(
        mock_detail_record.file_name, mock_detail_record.absolute_score
    )


@pytest.mark.parametrize("record_file_name", ["file1", "file2"])
@pytest.mark.parametrize("test_case_file_name", ["file1", "file2"])
@pytest.mark.parametrize("record_score", [1, None])
@pytest.mark.parametrize("test_case_score", [1, None])
def test_is_submission_already_recorded(
    mock_record_read_service: Mock,
    mock_detail_record: Mock,
    mock_detail_records: Mock,
    record_file_name: str,
    test_case_file_name: str,
    record_score: Optional[int],
    test_case_score: Optional[int],
) -> None:

    mock_detail_record.file_name = record_file_name
    mock_detail_record.absolute_score = record_score
    mock_detail_records.records = [mock_detail_record]

    test_cases = TestCases()
    test_cases.add_test_case(TestCase(test_case_file_name, test_case_score, Path("test")))

    submission_matcher = SubmissionMatcher(record_read_service=mock_record_read_service)
    with patch.object(SubmissionMatcher, "fetch_same_score_records") as mock_fetch_same_score_records:

        mock_fetch_same_score_records.return_value = [mock_detail_records]
        result = submission_matcher.is_submission_already_recorded(test_cases)

        assert result is (record_file_name == test_case_file_name and record_score == test_case_score)
