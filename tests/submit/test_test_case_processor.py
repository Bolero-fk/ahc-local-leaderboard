from unittest.mock import Mock, patch

import pytest

from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.test_case import TestCase, TestCases
from ahc_local_leaderboard.submit.test_case_processor import (
    TestCaseProcessor,
    TestCasesProcessor,
)
from ahc_local_leaderboard.utils.file_utility import FileUtility
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


@pytest.fixture
def mock_file_utility() -> Mock:
    return Mock(spec=FileUtility)


@pytest.fixture
def mock_test_case_processor() -> Mock:
    return Mock(spec=TestCaseProcessor)


@pytest.fixture
def mock_test_cases() -> Mock:
    return Mock(spec=TestCases)


def test_update_top_score(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    mock_file_utility: Mock,
) -> None:

    test_case_processor = TestCaseProcessor(
        mock_record_read_service, mock_record_write_service, mock_relative_score_calculator, mock_file_utility
    )

    score_history_id = 1

    test_case = Mock(spec=TestCase)
    test_case_processor.update_top_score(test_case, score_history_id)

    mock_record_write_service.update_top_score.assert_called_once_with(test_case, score_history_id)
    mock_file_utility.copy_submit_file_to_leaderboard.assert_called_once_with(test_case)


@pytest.mark.parametrize("is_better", [True, False])
def test_try_update_top_score(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    mock_file_utility: Mock,
    is_better: bool,
) -> None:

    test_case_processor = TestCaseProcessor(
        mock_record_read_service, mock_record_write_service, mock_relative_score_calculator, mock_file_utility
    )

    test_case = Mock(spec=TestCase)
    test_case.score = 100
    top_score = 90
    score_history_id = 1

    mock_record_read_service.fetch_top_score.return_value = top_score
    mock_relative_score_calculator.is_better_score.return_value = is_better

    with patch.object(TestCaseProcessor, "update_top_score") as mock_update_top_score:
        test_case_processor.try_update_top_score(test_case, score_history_id)

        mock_record_read_service.fetch_top_score.assert_called_once_with(test_case)
        mock_relative_score_calculator.is_better_score.assert_called_once_with(test_case.score, top_score)

        if is_better:
            mock_update_top_score.assert_called_once_with(test_case, score_history_id)
        else:
            mock_update_top_score.assert_not_called()


def test_process_test_case(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    mock_file_utility: Mock,
) -> None:

    test_case_processor = TestCaseProcessor(
        mock_record_read_service, mock_record_write_service, mock_relative_score_calculator, mock_file_utility
    )

    test_case = Mock(spec=TestCase)
    score_history_id = 1

    with patch.object(TestCaseProcessor, "try_update_top_score") as mock_try_update_top_score:

        test_case_processor.process_test_case(test_case, score_history_id)

        mock_try_update_top_score.assert_called_once()
        mock_record_write_service.insert_test_case.assert_called_once_with(test_case, score_history_id)


@pytest.mark.parametrize("test_case_count", [0, 1, 100])
def test_process_test_cases(mock_test_case_processor: Mock, mock_test_cases: Mock, test_case_count: int) -> None:
    test_cases_processor = TestCasesProcessor(mock_test_case_processor)

    mock_test_cases.__iter__ = Mock(return_value=iter([Mock(spec=TestCase) for _ in range(test_case_count)]))
    score_history_id = 1

    test_cases_processor.process_test_cases(mock_test_cases, score_history_id)

    assert mock_test_case_processor.process_test_case.call_count == test_case_count
