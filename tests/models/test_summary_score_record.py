from typing import Optional
from unittest.mock import Mock

import pytest

from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
)
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    SummaryScoreRecords,
    TopSummaryScoreRecord,
)
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


@pytest.fixture
def mock_detail_score_records() -> Mock:
    return Mock(spec=DetailScoreRecords)


@pytest.fixture
def mock_relative_score_calculator() -> Mock:
    return Mock(spec=RelativeScoreCalculaterInterface)


@pytest.mark.parametrize("id", [1, 1000])
@pytest.mark.parametrize("submission_time", ["2023-01-01 10:00:00", "today"])
@pytest.mark.parametrize("total_absolute_score", [-100000, 0, 100000])
@pytest.mark.parametrize("total_relative_score", [0, 100000])
@pytest.mark.parametrize("invalid_score_count", [0, 100000])
@pytest.mark.parametrize("relative_rank", [None, 1, 100000])
def test_summary_score_record_initialization(
    id: int,
    submission_time: str,
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
    relative_rank: int,
) -> None:
    record = SummaryScoreRecord(
        id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
    )
    assert record.id == id
    assert record.submission_time == submission_time
    assert record.total_absolute_score == total_absolute_score
    assert record.total_relative_score == total_relative_score
    assert record.invalid_score_count == invalid_score_count
    assert record.relative_rank == relative_rank


@pytest.fixture
def sample_summary_record() -> SummaryScoreRecord:
    return SummaryScoreRecord(1, "2023-01-01 10:00:00", 100, 0, 0, 1)


@pytest.mark.parametrize("total_absolute_score ", [1, 100000])
@pytest.mark.parametrize("total_relative_score ", [1, 100000])
@pytest.mark.parametrize("invalid_score_count ", [1, 100000])
def test_update(
    mock_detail_score_records: Mock,
    mock_relative_score_calculator: Mock,
    sample_summary_record: SummaryScoreRecord,
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
) -> None:

    mock_detail_score_records.calculate_total_absolute_score.return_value = total_absolute_score
    mock_detail_score_records.calculate_total_relative_score.return_value = total_relative_score
    mock_detail_score_records.calculate_invalid_score_count.return_value = invalid_score_count

    sample_summary_record.update(mock_detail_score_records, mock_relative_score_calculator)

    assert sample_summary_record.total_absolute_score == total_absolute_score
    assert sample_summary_record.total_relative_score == total_relative_score
    assert sample_summary_record.invalid_score_count == invalid_score_count


@pytest.mark.parametrize("id", [-1000, -1])
@pytest.mark.parametrize("submission_time", ["2023-01-01 10:00:00", "today"])
@pytest.mark.parametrize("total_absolute_score", [-100000, 0, 100000])
@pytest.mark.parametrize("total_relative_score", [-100000, -1])
@pytest.mark.parametrize("invalid_score_count", [-100000, -1])
@pytest.mark.parametrize("relative_rank", [-100000, 0])
def test_summary_score_record_initialization_assertions(
    id: int,
    submission_time: str,
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
    relative_rank: int,
) -> None:
    with pytest.raises(AssertionError):
        SummaryScoreRecord(
            id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
        )


@pytest.mark.parametrize("total_absolute_score", [-100000, 0, 100000])
@pytest.mark.parametrize("total_relative_score", [0, 100000])
@pytest.mark.parametrize("invalid_score_count", [0, 100000])
def test_top_summary_score_record_initialization(
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
) -> None:
    record = TopSummaryScoreRecord(total_absolute_score, total_relative_score, invalid_score_count)
    assert record.total_absolute_score == total_absolute_score
    assert record.total_relative_score == total_relative_score
    assert record.invalid_score_count == invalid_score_count


@pytest.mark.parametrize("total_absolute_score", [-100000, 0, 100000])
@pytest.mark.parametrize("total_relative_score", [-100000, -1])
@pytest.mark.parametrize("invalid_score_count", [-100000, -1])
def test_top_summary_score_record_initialization_assertions(
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
) -> None:
    with pytest.raises(AssertionError):
        TopSummaryScoreRecord(total_absolute_score, total_relative_score, invalid_score_count)


@pytest.mark.parametrize("absolute_score1", [None, 0, 100])
@pytest.mark.parametrize("absolute_score2", [None, 0, 100])
@pytest.mark.parametrize("relative_score1", [-100, 0, 100])
@pytest.mark.parametrize("relative_score2", [-100, 0, 100])
def test_summary_score_record_add_score(
    absolute_score1: Optional[int], absolute_score2: Optional[int], relative_score1: int, relative_score2: int
) -> None:
    total_absolute_score = 100
    total_relative_score = 100
    invalid_score_count = 0
    record = SummaryScoreRecord(
        id=1,
        submission_time="2023-01-01 10:00:00",
        total_absolute_score=total_absolute_score,
        total_relative_score=total_relative_score,
        invalid_score_count=invalid_score_count,
        relative_rank=5,
    )

    detail_record1 = DetailScoreRecord("test_case_1", absolute_score1, 200)
    record.add_score(detail_record1, relative_score=relative_score1)
    if isinstance(absolute_score1, int):
        total_absolute_score += absolute_score1
    else:
        invalid_score_count += 1
    total_relative_score += relative_score1

    assert record.total_absolute_score == total_absolute_score
    assert record.total_relative_score == total_relative_score
    assert record.invalid_score_count == invalid_score_count

    detail_record2 = DetailScoreRecord("test_case_2", absolute_score2, 200)
    record.add_score(detail_record2, relative_score=relative_score2)
    if isinstance(absolute_score2, int):
        total_absolute_score += absolute_score2
    else:
        invalid_score_count += 1
    total_relative_score += relative_score2

    assert record.total_absolute_score == total_absolute_score
    assert record.total_relative_score == total_relative_score
    assert record.invalid_score_count == invalid_score_count


@pytest.mark.parametrize("record_count", [0, 1, 10])
def test_summary_score_records_initialization(record_count: int) -> None:

    records = [SummaryScoreRecord(i + 1, f"test_case_{i}", i * 100, i * 200, 0, i + 1) for i in range(record_count)]
    summary_records = SummaryScoreRecords(records=records)
    assert len(summary_records.records) == record_count


def test_add_record() -> None:
    record1 = Mock(spec=SummaryScoreRecord)
    record2 = Mock(spec=SummaryScoreRecord)
    records = SummaryScoreRecords([record1])

    records.add_record(record2)

    assert len(records.records) == 2
    assert records.records[-1] == record2


def test_update_relative_ranks() -> None:
    record1 = Mock(spec=SummaryScoreRecord, total_relative_score=300)
    record2 = Mock(spec=SummaryScoreRecord, total_relative_score=200)
    record3 = Mock(spec=SummaryScoreRecord, total_relative_score=400)
    records = SummaryScoreRecords([record1, record2, record3])

    records.update_relative_ranks()

    assert record3.relative_rank == 1
    assert record1.relative_rank == 2
    assert record2.relative_rank == 3


def test_get_latest_record() -> None:
    record1 = Mock(spec=SummaryScoreRecord, submission_time="2023-01-01 10:00:00")
    record2 = Mock(spec=SummaryScoreRecord, submission_time="2023-01-02 10:00:00")
    record3 = Mock(spec=SummaryScoreRecord, submission_time="2023-01-01 12:00:00")
    records = SummaryScoreRecords([record1, record2, record3])

    latest_record = records.get_latest_record()

    assert latest_record == record2


def test_get_records_except_latest() -> None:
    record1 = Mock(spec=SummaryScoreRecord, submission_time="2023-01-01 10:00:00")
    record2 = Mock(spec=SummaryScoreRecord, submission_time="2023-01-02 10:00:00")
    record3 = Mock(spec=SummaryScoreRecord, submission_time="2023-01-01 12:00:00")
    records = SummaryScoreRecords([record1, record2, record3])

    remaining_records = records.get_records_except_latest()

    assert record2 not in remaining_records
    assert record1 in remaining_records
    assert record3 in remaining_records
