from typing import Optional, Union
from unittest.mock import Mock

import pytest

from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
    TopDetailScoreRecord,
)
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


@pytest.fixture
def mock_relative_score_calculator() -> Mock:
    return Mock(spec=RelativeScoreCalculaterInterface)


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("score1", [None, -100000, -1, 0, 1, 100000])
@pytest.mark.parametrize("score2", [None, -100000, -1, 0, 1, 100000])
def test_detail_score_record_initialization(input: str, score1: Optional[int], score2: Optional[int]) -> None:
    record = DetailScoreRecord(input, score1, score2)
    assert record.file_name == input
    assert record.absolute_score == score1
    assert record.top_score == score2


@pytest.mark.parametrize(
    "score, top_score, expected_relative_score",
    [
        (100, 200, 2),
        (1, 100, 10),
    ],
)
def test_calculate_relative_score(
    mock_relative_score_calculator: Mock, score: int, top_score: int, expected_relative_score: int
) -> None:
    record = DetailScoreRecord(file_name="test_case_1", absolute_score=score, top_score=top_score)

    mock_relative_score_calculator.return_value = expected_relative_score
    relative_score = record.calculate_relative_score(mock_relative_score_calculator)

    mock_relative_score_calculator.assert_called_once_with(score, top_score)
    assert relative_score == expected_relative_score


@pytest.mark.parametrize(
    "score, expected_absolute_score",
    [
        (100, 100),
        (1, 1),
        (None, 0),
    ],
)
def test_get_absolute_score_with_value(score: Optional[int], expected_absolute_score: int) -> None:
    record = DetailScoreRecord(file_name="test_case_1", absolute_score=score, top_score=1000)
    assert record.get_absolute_score() == expected_absolute_score


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("top_score", [None, -100000, -1, 0, 1, 100000])
@pytest.mark.parametrize("id", [1, 100000])
def test_top_detail_score_record_initialization(input: str, top_score: Optional[int], id: int) -> None:
    top_record = TopDetailScoreRecord(input, top_score, id)
    assert top_record.file_name == input
    assert top_record.absolute_score == top_score
    assert top_record.top_score == top_score
    assert top_record.submittion_id == id


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("top_score", [None, -100000, -1, 0, 1, 100000])
@pytest.mark.parametrize("id", [-100000, -1])
def test_top_detail_score_record_initialization_assertions(input: str, top_score: Optional[int], id: int) -> None:
    with pytest.raises(AssertionError):
        TopDetailScoreRecord(input, top_score, id)


@pytest.mark.parametrize("id", [1, 100000, "Top"])
@pytest.mark.parametrize("record_count", [0, 1, 10])
def test_detail_score_records_initialization(id: Union[int, str], record_count: int) -> None:
    records = [DetailScoreRecord(f"test_case_{i}", i * 100, i * 200) for i in range(record_count)]
    detail_records = DetailScoreRecords[DetailScoreRecord](id=id, records=records)
    assert detail_records.id == id
    assert len(detail_records.records) == record_count


@pytest.mark.parametrize("id", [-100000, -1, "aaa", ""])
@pytest.mark.parametrize("record_count", [1])
def test_detail_score_records_initialization_assertions(id: Union[int, str], record_count: int) -> None:
    records = [DetailScoreRecord(f"test_case_{i}", i * 100, i * 200) for i in range(record_count)]
    with pytest.raises(AssertionError):
        DetailScoreRecords(id=id, records=records)


@pytest.fixture
def sample_records() -> list[DetailScoreRecord]:
    record1 = DetailScoreRecord(file_name="test1.txt", absolute_score=100, top_score=200)
    record2 = DetailScoreRecord(file_name="test2.txt", absolute_score=None, top_score=200)
    record3 = DetailScoreRecord(file_name="test3.txt", absolute_score=300, top_score=400)
    return [record1, record2, record3]


def test_sort_records_by_input_file_name(sample_records: list[DetailScoreRecord]) -> None:
    records = DetailScoreRecords[DetailScoreRecord](id=1, records=sample_records)
    records.sort_records_by_input_file_name()
    assert [record.file_name for record in records.records] == ["test1.txt", "test2.txt", "test3.txt"]


def test_calculate_total_absolute_score(sample_records: list[DetailScoreRecord]) -> None:
    records = DetailScoreRecords[DetailScoreRecord](id=2, records=sample_records)
    total_score = records.calculate_total_absolute_score()
    assert total_score == 400


def test_calculate_invalid_score_count(sample_records: list[DetailScoreRecord]) -> None:
    records = DetailScoreRecords[DetailScoreRecord](id=3, records=sample_records)
    invalid_count = records.calculate_invalid_score_count()
    assert invalid_count == 1


def test_calculate_total_relative_score(
    sample_records: list[DetailScoreRecord], mock_relative_score_calculator: Mock
) -> None:
    records = DetailScoreRecords[DetailScoreRecord](id=4, records=sample_records)
    mock_relative_score_calculator.return_value = 1
    total_relative_score = records.calculate_total_relative_score(mock_relative_score_calculator)

    assert mock_relative_score_calculator.call_count == len(sample_records)
    assert total_relative_score == len(sample_records)
