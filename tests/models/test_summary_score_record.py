from ahc_local_leaderboard.models.detail_score_record import DetailScoreRecord
from ahc_local_leaderboard.models.summary_score_record import (  # 実際のモジュール名に変更
    SummaryScoreRecord,
    SummaryScoreRecords,
    TopSummaryScoreRecord,
)


def check_summary_score_record_attributes(
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


def test_summary_score_record_initialization() -> None:
    # SummaryScoreRecord の初期化と属性確認
    check_summary_score_record_attributes(1, "2023-01-01 10:00:00", 500, 800, 2, 5)


def check_top_summary_score_record_attributes(
    total_absolute_score: int,
    total_relative_score: int,
    invalid_score_count: int,
) -> None:
    record = TopSummaryScoreRecord(total_absolute_score, total_relative_score, invalid_score_count)
    assert record.total_absolute_score == total_absolute_score
    assert record.total_relative_score == total_relative_score
    assert record.invalid_score_count == invalid_score_count


def test_top_summary_score_record_initialization() -> None:
    # TopSummaryScoreRecord の初期化と属性確認
    check_top_summary_score_record_attributes(1000, 1500, 3)


def test_summary_score_record_add_score() -> None:
    # add_score メソッドのテスト
    record = SummaryScoreRecord(
        id=1,
        submission_time="2023-01-01 10:00:00",
        total_absolute_score=500,
        total_relative_score=800,
        invalid_score_count=0,
        relative_rank=5,
    )

    # absolute_score が存在する DetailScoreRecord の追加
    detail_record = DetailScoreRecord("test_case_1", 100, 200)
    record.add_score(detail_record, relative_score=150)
    assert record.total_absolute_score == 600
    assert record.total_relative_score == 950
    assert record.invalid_score_count == 0

    # absolute_score が None の DetailScoreRecord の追加
    detail_record_with_none = DetailScoreRecord("test_case_2", None, 200)
    record.add_score(detail_record_with_none, relative_score=100)
    assert record.total_absolute_score == 600
    assert record.total_relative_score == 1050
    assert record.invalid_score_count == 1


def test_summary_score_records_initialization() -> None:
    # SummaryScoreRecords の初期化と属性確認
    record1 = SummaryScoreRecord(
        id=1,
        submission_time="2023-01-01 10:00:00",
        total_absolute_score=500,
        total_relative_score=800,
        invalid_score_count=2,
        relative_rank=5,
    )
    record2 = SummaryScoreRecord(
        id=2,
        submission_time="2023-01-01 11:00:00",
        total_absolute_score=700,
        total_relative_score=900,
        invalid_score_count=1,
        relative_rank=3,
    )
    summary_records = SummaryScoreRecords(records=[record1, record2])
    assert len(summary_records.records) == 2
    assert summary_records.records[0].id == 1
    assert summary_records.records[1].id == 2
