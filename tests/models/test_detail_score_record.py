from typing import Optional

from ahc_local_leaderboard.models.detail_score_record import (  # 実際のモジュール名に変更
    DetailScoreRecord,
    DetailScoreRecords,
    TopDetailScoreRecord,
)


def check_detail_score_record_attributes(
    expected_file_name: str, expected_score: Optional[int], expected_top_score: Optional[int]
) -> None:
    record = DetailScoreRecord(expected_file_name, expected_score, expected_top_score)
    assert record.input_test_case == expected_file_name
    assert record.absolute_score == expected_score
    assert record.top_score == expected_top_score


def check_top_detail_score_record_attributes(
    expected_file_name: str, expected_top_score: Optional[int], expected_id: int
) -> None:
    top_record = TopDetailScoreRecord(expected_file_name, expected_top_score, expected_id)
    assert top_record.input_test_case == expected_file_name
    assert top_record.absolute_score == expected_top_score
    assert top_record.top_score == expected_top_score
    assert top_record.id == expected_id


def test_detail_score_record_initialization() -> None:
    # DetailScoreRecord の初期化と属性確認
    check_detail_score_record_attributes("test_case_1", 100, 200)
    check_detail_score_record_attributes("test_case_2", None, 200)
    check_detail_score_record_attributes("test_case_3", 100, None)
    check_detail_score_record_attributes("test_case_4", None, None)


def test_top_detail_score_record_initialization() -> None:
    # TopDetailScoreRecord の初期化と属性確認
    check_top_detail_score_record_attributes("test_case_1", 300, 1)
    check_top_detail_score_record_attributes("test_case_2", None, 1)


def test_detail_score_records_initialization() -> None:
    # DetailScoreRecords の初期化と属性確認
    records = [DetailScoreRecord("test_case_1", 100, 200), DetailScoreRecord("test_case_2", 150, 250)]
    detail_records = DetailScoreRecords(id=1, records=records)
    assert detail_records.id == 1
    assert len(detail_records.records) == 2
    assert detail_records.records[0].input_test_case == "test_case_1"
    assert detail_records.records[1].input_test_case == "test_case_2"
    assert detail_records.records[0].absolute_score == 100
    assert detail_records.records[1].absolute_score == 150


def test_detail_score_records_with_string_id() -> None:
    # DetailScoreRecords で文字列 ID を使った初期化と属性確認
    records = [TopDetailScoreRecord("test_case_1", 100, 200), TopDetailScoreRecord("test_case_2", 150, 250)]
    detail_records = DetailScoreRecords(id="A1", records=records)
    assert detail_records.id == "A1"
    assert len(detail_records.records) == 2
    assert detail_records.records[0].input_test_case == "test_case_1"
    assert detail_records.records[1].input_test_case == "test_case_2"
