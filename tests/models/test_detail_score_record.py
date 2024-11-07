from typing import Optional, Union

import pytest

from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
    TopDetailScoreRecord,
)


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("score1", [None, -100000, -1, 0, 1, 100000])
@pytest.mark.parametrize("score2", [None, -100000, -1, 0, 1, 100000])
def test_detail_score_record_initialization(input: str, score1: Optional[int], score2: Optional[int]) -> None:
    record = DetailScoreRecord(input, score1, score2)
    assert record.input_test_case == input
    assert record.absolute_score == score1
    assert record.top_score == score2


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("top_score", [None, -100000, -1, 0, 1, 100000])
@pytest.mark.parametrize("id", [1, 100000])
def test_top_detail_score_record_initialization(input: str, top_score: Optional[int], id: int) -> None:
    top_record = TopDetailScoreRecord(input, top_score, id)
    assert top_record.input_test_case == input
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
    detail_records = DetailScoreRecords(id=id, records=records)
    assert detail_records.id == id
    assert len(detail_records.records) == record_count


@pytest.mark.parametrize("id", [-100000, -1, "aaa", ""])
@pytest.mark.parametrize("record_count", [1])
def test_detail_score_records_initialization_assertions(id: Union[int, str], record_count: int) -> None:
    records = [DetailScoreRecord(f"test_case_{i}", i * 100, i * 200) for i in range(record_count)]
    with pytest.raises(AssertionError):
        DetailScoreRecords(id=id, records=records)
