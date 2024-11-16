from typing import Dict, Generator, cast
from unittest.mock import MagicMock, Mock, create_autospec, patch

import pytest

from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
    TopDetailScoreRecord,
)
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)
from ahc_local_leaderboard.view.viewer import Viewer


@pytest.fixture
def mock_record_read_service() -> RecordReadService:
    return cast(RecordReadService, create_autospec(RecordReadService))  # mypyのためのcast


@pytest.fixture
def mock_relative_score_calculator() -> RelativeScoreCalculaterInterface:
    return cast(
        RelativeScoreCalculaterInterface, create_autospec(RelativeScoreCalculaterInterface)
    )  # mypyのためのcast


@pytest.fixture
def viewer(mock_record_read_service: Mock, mock_relative_score_calculator: Mock) -> Viewer:
    return Viewer(
        record_read_service=mock_record_read_service, relative_score_calculator=mock_relative_score_calculator
    )


@pytest.fixture
def mock_summary_table_builder_functions() -> Generator[Dict[str, MagicMock], None, None]:
    with patch(
        "ahc_local_leaderboard.view.table_builder.SummaryTableBuilder.insert_top_record"
    ) as mock_function1, patch(
        "ahc_local_leaderboard.view.table_builder.SummaryTableBuilder.insert_record"
    ) as mock_function2, patch(
        "ahc_local_leaderboard.view.table_builder.SummaryTableBuilder.display"
    ) as mock_function3:

        yield {"insert_top_record": mock_function1, "insert_record": mock_function2, "display": mock_function3}


@pytest.fixture
def mock_detail_table_builder_functions() -> Generator[Dict[str, MagicMock], None, None]:
    with patch("ahc_local_leaderboard.view.table_builder.DetailTableBuilder.insert_record") as mock_function1, patch(
        "ahc_local_leaderboard.view.table_builder.DetailTableBuilder.display"
    ) as mock_function2:

        yield {"insert_record": mock_function1, "display": mock_function2}


@pytest.fixture
def mock_top_detail_table_builder_functions() -> Generator[Dict[str, MagicMock], None, None]:
    with patch(
        "ahc_local_leaderboard.view.table_builder.TopDetailTableBuilder.insert_record"
    ) as mock_function1, patch(
        "ahc_local_leaderboard.view.table_builder.TopDetailTableBuilder.display"
    ) as mock_function2:

        yield {"insert_record": mock_function1, "display": mock_function2}


@pytest.mark.parametrize("count", [0, 1, 100])
def test_show_summary_list(
    viewer: Viewer,
    mock_record_read_service: Mock,
    mock_summary_table_builder_functions: Dict[str, MagicMock],
    count: int,
) -> None:

    mock_record_read_service.fetch_top_summary_record.return_value = MagicMock()
    mock_record_read_service.fetch_recent_summary_records.return_value = MagicMock(
        records=[MagicMock() for _ in range(count)]
    )

    viewer.show_summary_list(list_length=count)
    mock_record_read_service.fetch_top_summary_record.assert_called_once()
    mock_record_read_service.fetch_recent_summary_records.assert_called_once_with(count)

    mock_summary_table_builder_functions["insert_top_record"].assert_called_once()
    assert mock_summary_table_builder_functions["insert_record"].call_count == count
    mock_summary_table_builder_functions["display"].assert_called_once()


@pytest.mark.parametrize("count", [-100, -1])
def test_show_summary_list_assertions(viewer: Viewer, count: int) -> None:

    with pytest.raises(AssertionError):
        viewer.show_summary_list(list_length=count)


def test_show_summary_table(viewer: Viewer, mock_summary_table_builder_functions: Dict[str, MagicMock]) -> None:
    summary_record = MagicMock(spec=SummaryScoreRecord)
    summary_record.id = 1

    viewer.show_summary_table(summary_record)
    mock_summary_table_builder_functions["insert_record"].assert_called_once()
    mock_summary_table_builder_functions["display"].assert_called_once()


def test_show_test_case_table(viewer: Viewer, mock_detail_table_builder_functions: Dict[str, MagicMock]) -> None:
    detail_records = MagicMock(spec=DetailScoreRecords)
    detail_records.id = 1
    detail_records.records = [MagicMock(spec=DetailScoreRecord)]

    viewer.show_test_case_table(detail_records)
    mock_detail_table_builder_functions["insert_record"].assert_called_once()
    mock_detail_table_builder_functions["display"].assert_called_once()


@pytest.mark.parametrize("id", [1, 100])
def test_show_detail(id: int, viewer: Viewer, mock_record_read_service: Mock) -> None:
    mock_record_read_service.fetch_summary_record_by_id.return_value = MagicMock(spec=SummaryScoreRecord)
    mock_record_read_service.fetch_detail_records_by_id.return_value = MagicMock(spec=DetailScoreRecords)

    with patch.object(viewer, "show_summary_table") as mock_show_summary_table, patch.object(
        viewer, "show_test_case_table"
    ) as mock_show_test_case_table:

        viewer.show_detail(submission_id=id)
        mock_record_read_service.fetch_summary_record_by_id.assert_called_once_with(id)
        mock_show_summary_table.assert_called_once()
        mock_record_read_service.fetch_detail_records_by_id.assert_called_once_with(id)
        mock_show_test_case_table.assert_called_once()


@pytest.mark.parametrize("id", [-100, -1, 0])
def test_show_detail_assertions(id: int, viewer: Viewer) -> None:
    with pytest.raises(AssertionError):
        viewer.show_detail(submission_id=id)


def test_show_latest_detail(viewer: Viewer, mock_record_read_service: Mock) -> None:
    mock_record_read_service.fetch_latest_submission_id.return_value = 10

    with patch.object(viewer, "show_detail") as mock_show_detail:
        viewer.show_latest_detail()
        mock_show_detail.assert_called_once()


def test_show_top_test_case_table(
    viewer: Viewer, mock_top_detail_table_builder_functions: Dict[str, MagicMock]
) -> None:

    detail_records = MagicMock(spec=DetailScoreRecords)
    detail_records.records = [MagicMock(spec=TopDetailScoreRecord)]

    viewer.show_top_test_case_table(detail_records)
    mock_top_detail_table_builder_functions["insert_record"].assert_called_once()
    mock_top_detail_table_builder_functions["display"].assert_called_once()


def test_show_top_detail(viewer: Viewer, mock_record_read_service: Mock) -> None:
    mock_record_read_service.fetch_sorted_top_detail_records.return_value = MagicMock(spec=DetailScoreRecords)

    with patch.object(viewer, "show_top_test_case_table") as mock_show_top_test_case_table:
        viewer.show_top_detail()
        mock_record_read_service.fetch_sorted_top_detail_records.assert_called_once()
        mock_show_top_test_case_table.assert_called_once()
