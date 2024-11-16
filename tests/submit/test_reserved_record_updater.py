from unittest.mock import Mock

import pytest

from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
)
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.submit.reserved_record_updater import ReservedRecordUpdater
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
def mock_reserved_record() -> Mock:
    reserved_record = Mock(spec=SummaryScoreRecord)
    reserved_record.id = 1
    return reserved_record


@pytest.fixture
def mock_detail_records() -> Mock:
    return Mock(spec=DetailScoreRecords[DetailScoreRecord])


def test_update_reserved_record(
    mock_record_read_service: Mock,
    mock_record_write_service: Mock,
    mock_relative_score_calculator: Mock,
    mock_reserved_record: Mock,
    mock_detail_records: Mock,
) -> None:

    mock_record_read_service.fetch_detail_records_by_id.return_value = mock_detail_records

    updater = ReservedRecordUpdater(
        record_read_service=mock_record_read_service,
        record_write_service=mock_record_write_service,
        relative_score_calculator=mock_relative_score_calculator,
    )

    updater.update_reserved_record(mock_reserved_record)

    mock_record_read_service.fetch_detail_records_by_id.assert_called_once_with(mock_reserved_record.id)
    mock_reserved_record.update.assert_called_once_with(mock_detail_records, mock_relative_score_calculator)
    mock_record_write_service.update_score_history.assert_called_once_with(mock_reserved_record)
