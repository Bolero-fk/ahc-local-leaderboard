import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

from ahc_local_leaderboard.database.database_manager import (
    DatabaseManager,
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.models.detail_score_record import DetailScoreRecords
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    TopSummaryScoreRecord,
)
from ahc_local_leaderboard.models.test_case import TestCase


@pytest.fixture
def temp_database() -> Generator[None, None, None]:

    with tempfile.TemporaryDirectory() as temp_dir, patch("ahc_local_leaderboard.consts.ROOT_DIR", Path(temp_dir)):
        (Path(temp_dir) / "leader_board").mkdir(parents=True, exist_ok=True)
        DatabaseManager.setup()
        yield


def get_temp_summary_record() -> SummaryScoreRecord:
    return SummaryScoreRecord(1, "test", 1, 10, 1, 1)


def get_now_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def test_database_connection(temp_database: Generator[None, None, None]) -> None:
    with DatabaseManager() as conn:
        assert isinstance(conn, sqlite3.Connection)


def test_score_history_table_exists(temp_database: Generator[None, None, None]) -> None:

    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='score_history'")
        result = cursor.fetchone()
        assert result is not None


def test_test_cases_table_exists(temp_database: Generator[None, None, None]) -> None:

    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_cases'")
        result = cursor.fetchone()
        assert result is not None


def test_top_scores_table_exists(temp_database: Generator[None, None, None]) -> None:
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='top_scores'")
        result = cursor.fetchone()
        assert result is not None


@pytest.fixture
def score_history_repository(temp_database: Generator[None, None, None]) -> ScoreHistoryRepository:
    return ScoreHistoryRepository()


def test_reserve_empty_score_history_record(score_history_repository: ScoreHistoryRepository) -> None:

    submission_time = get_now_time()
    record = score_history_repository.reserve_empty_score_history_record(submission_time)

    assert isinstance(record, SummaryScoreRecord)
    assert record.submission_time == submission_time
    assert record.total_absolute_score == 0
    assert record.total_relative_score == 0
    assert record.invalid_score_count == 0
    assert record.relative_rank is None


def test_update_score_history(score_history_repository: ScoreHistoryRepository) -> None:

    submission_time = get_now_time()
    record = score_history_repository.reserve_empty_score_history_record(submission_time)

    record.total_absolute_score = 100
    record.total_relative_score = 200
    record.invalid_score_count = 1
    record.relative_rank = 10
    score_history_repository.update_score_history(record)

    updated_record = score_history_repository.fetch_summary_record_by_submission_id(record.id)
    assert updated_record.total_absolute_score == 100
    assert updated_record.total_relative_score == 200
    assert updated_record.invalid_score_count == 1
    assert updated_record.relative_rank == 10


def test_fetch_summary_record_by_submission_id(score_history_repository: ScoreHistoryRepository) -> None:

    submission_time = get_now_time()

    reserved_record = score_history_repository.reserve_empty_score_history_record(submission_time)
    record = get_temp_summary_record()
    record.id = reserved_record.id
    record.submission_time = submission_time

    score_history_repository.update_score_history(record)

    fetched_record = score_history_repository.fetch_summary_record_by_submission_id(record.id)

    assert fetched_record.id == record.id
    assert fetched_record.submission_time == record.submission_time
    assert fetched_record.total_absolute_score == record.total_absolute_score
    assert fetched_record.total_relative_score == record.total_relative_score
    assert fetched_record.invalid_score_count == record.invalid_score_count
    assert fetched_record.relative_rank == record.relative_rank


def test_fetch_all_record(score_history_repository: ScoreHistoryRepository) -> None:

    submission_time1 = "test_time1"
    record1 = score_history_repository.reserve_empty_score_history_record(submission_time1)
    record1.total_absolute_score = 1
    record1.total_relative_score = 2
    record1.invalid_score_count = 3
    record1.relative_rank = 4
    score_history_repository.update_score_history(record1)

    submission_time2 = "test_time2"
    record2 = score_history_repository.reserve_empty_score_history_record(submission_time2)
    record2.total_absolute_score = 10
    record2.total_relative_score = 20
    record2.invalid_score_count = 30
    record2.relative_rank = 40
    score_history_repository.update_score_history(record2)

    all_records = score_history_repository.fetch_all_records()

    assert len(all_records.records) == 2

    records = [record1, record2]

    for i in range(len(all_records.records)):
        assert all_records.records[i].id == records[i].id
        assert all_records.records[i].submission_time == records[i].submission_time
        assert all_records.records[i].total_absolute_score == records[i].total_absolute_score
        assert all_records.records[i].total_relative_score == records[i].total_relative_score
        assert all_records.records[i].invalid_score_count == records[i].invalid_score_count
        assert all_records.records[i].relative_rank == records[i].relative_rank


def test_fetch_latest_id(score_history_repository: ScoreHistoryRepository) -> None:

    submission_time1 = "2024-11-11 11:11:11"

    score_history_repository.reserve_empty_score_history_record(submission_time1)

    submission_time2 = "2024-12-12 12:12:12"
    record2 = score_history_repository.reserve_empty_score_history_record(submission_time2)

    latest_id = score_history_repository.fetch_latest_id()
    assert latest_id == record2.id


def test_fetch_recent_summary_records(score_history_repository: ScoreHistoryRepository) -> None:

    submission_time1 = "2024-11-11 11:11:11"
    record1 = score_history_repository.reserve_empty_score_history_record(submission_time1)
    record1.total_absolute_score = 1
    record1.total_relative_score = 2
    record1.invalid_score_count = 3
    record1.relative_rank = 4
    score_history_repository.update_score_history(record1)

    submission_time2 = "2024-12-12 12:12:12"
    record2 = score_history_repository.reserve_empty_score_history_record(submission_time2)
    record2.total_absolute_score = 10
    record2.total_relative_score = 20
    record2.invalid_score_count = 30
    record2.relative_rank = 40
    score_history_repository.update_score_history(record2)

    recent_records = score_history_repository.fetch_recent_summary_records(1)
    assert len(recent_records.records) == 1

    assert recent_records.records[0].id == record2.id
    assert recent_records.records[0].submission_time == record2.submission_time
    assert recent_records.records[0].total_absolute_score == record2.total_absolute_score
    assert recent_records.records[0].total_relative_score == record2.total_relative_score
    assert recent_records.records[0].invalid_score_count == record2.invalid_score_count
    assert recent_records.records[0].relative_rank == record2.relative_rank


def test_exists_id(score_history_repository: ScoreHistoryRepository) -> None:

    submission_time = get_now_time()
    record = score_history_repository.reserve_empty_score_history_record(submission_time)

    assert score_history_repository.exists_id(record.id) is True
    assert score_history_repository.exists_id(record.id + 1) is False


@pytest.fixture
def test_case_repository(temp_database: Generator[None, None, None]) -> TestCaseRepository:
    return TestCaseRepository()


def test_insert_test_case(test_case_repository: TestCaseRepository) -> None:

    test_case = TestCase(file_name="test1.txt", score=50, submit_file_path="out/test1.txt")
    score_history_id = 1

    test_case_repository.insert_test_case(test_case, score_history_id)

    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT test_case_input, absolute_score, score_history_id
            FROM test_cases
            WHERE test_case_input = ? AND score_history_id = ?
            """,
            (test_case.file_name, score_history_id),
        )
        result = cursor.fetchone()

    assert result is not None
    assert result[0] == test_case.file_name
    assert result[1] == test_case.score
    assert result[2] == score_history_id


def test_fetch_absolute_score_for_test_case(test_case_repository: TestCaseRepository) -> None:

    expected_score = 75
    test_case = TestCase(file_name="test2.txt", score=expected_score, submit_file_path="out/test2.txt")
    score_history_id = 1

    test_case_repository.insert_test_case(test_case, score_history_id)

    score = test_case_repository.fetch_absolute_score_for_test_case("test2.txt", score_history_id)

    assert score == expected_score
    with pytest.raises(ValueError):
        test_case_repository.fetch_absolute_score_for_test_case("non_existent.txt", score_history_id)


def test_fetch_records_by_submission_id(test_case_repository: TestCaseRepository) -> None:

    test_case1 = TestCase(file_name="test3.txt", score=20, submit_file_path="out/test3.txt")
    test_case2 = TestCase(file_name="test4.txt", score=40, submit_file_path="out/test4.txt")
    score_history_id = 1

    test_case_repository.insert_test_case(test_case1, score_history_id)
    test_case_repository.insert_test_case(test_case2, score_history_id)

    records = test_case_repository.fetch_records_by_submission_id(score_history_id)

    assert len(records.records) == 2
    assert records.records[0].input_test_case == "test3.txt"
    assert records.records[0].absolute_score == 20
    assert records.records[1].input_test_case == "test4.txt"
    assert records.records[1].absolute_score == 40


@pytest.fixture
def top_scores_repository(temp_database: Generator[None, None, None]) -> TopScoresRepository:
    return TopScoresRepository()


def test_update_top_score(top_scores_repository: TopScoresRepository) -> None:

    top_score = 100
    test_case = TestCase(file_name="test1.txt", score=top_score, submit_file_path="out/test1.txt")
    score_history_id = 1

    top_scores_repository.update_top_score(test_case, score_history_id)

    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT top_absolute_score, score_history_id FROM top_scores WHERE test_case_input = ?",
            (test_case.file_name,),
        )
        result = cursor.fetchone()

    assert result is not None
    assert result[0] == top_score
    assert result[1] == score_history_id


def test_fetch_top_score_for_test_case(top_scores_repository: TopScoresRepository) -> None:

    expected_top_score = 150
    test_case = TestCase(file_name="test2.txt", score=expected_top_score, submit_file_path="out/test2.txt")
    score_history_id = 2

    top_scores_repository.update_top_score(test_case, score_history_id)

    top_score = top_scores_repository.fetch_top_score_for_test_case(test_case)
    assert top_score == expected_top_score


def test_reset_is_updated_flags(top_scores_repository: TopScoresRepository) -> None:

    test_case1 = TestCase(file_name="test3.txt", score=200, submit_file_path="out/test3.txt")
    test_case2 = TestCase(file_name="test4.txt", score=250, submit_file_path="out/test4.txt")
    score_history_id = 3

    top_scores_repository.update_top_score(test_case1, score_history_id)
    top_scores_repository.update_top_score(test_case2, score_history_id)

    updated_scores = top_scores_repository.fetch_recently_updated_top_scores()
    assert len(updated_scores) == 2

    top_scores_repository.reset_is_updated_flags()

    updated_scores = top_scores_repository.fetch_recently_updated_top_scores()
    assert len(updated_scores) == 0


def test_fetch_test_case_count(top_scores_repository: TopScoresRepository) -> None:

    test_case1 = TestCase(file_name="test5.txt", score=300, submit_file_path="out/test5.txt")
    test_case2 = TestCase(file_name="test6.txt", score=350, submit_file_path="out/test6.txt")
    score_history_id = 4

    top_scores_repository.update_top_score(test_case1, score_history_id)
    top_scores_repository.update_top_score(test_case2, score_history_id)

    count = top_scores_repository.fetch_test_case_count()
    assert count == 2


def test_fetch_recently_updated_top_scores(top_scores_repository: TopScoresRepository) -> None:

    test_case = TestCase(file_name="test7.txt", score=400, submit_file_path="out/test7.txt")
    score_history_id = 5

    top_scores_repository.update_top_score(test_case, score_history_id)

    recently_updated = top_scores_repository.fetch_recently_updated_top_scores()
    assert len(recently_updated) == 1
    assert recently_updated[0].file_name == "test7.txt"
    assert recently_updated[0].top_score == 400


def test_fetch_top_summary_record(top_scores_repository: TopScoresRepository) -> None:

    test_case1 = TestCase(file_name="test8.txt", score=450, submit_file_path="out/test8.txt")
    test_case2 = TestCase(file_name="test9.txt", score=None, submit_file_path="out/test9.txt")
    score_history_id = 6

    top_scores_repository.update_top_score(test_case1, score_history_id)
    top_scores_repository.update_top_score(test_case2, score_history_id)

    summary_record = top_scores_repository.fetch_top_summary_record()
    assert isinstance(summary_record, TopSummaryScoreRecord)
    assert summary_record.total_absolute_score == 450
    assert summary_record.invalid_score_count == 1


def test_fetch_top_detail_records(top_scores_repository: TopScoresRepository) -> None:

    test_case1 = TestCase(file_name="test10.txt", score=500, submit_file_path="out/test10.txt")
    test_case2 = TestCase(file_name="test11.txt", score=550, submit_file_path="out/test11.txt")
    score_history_id = 7

    top_scores_repository.update_top_score(test_case1, score_history_id)
    top_scores_repository.update_top_score(test_case2, score_history_id)

    detail_records = top_scores_repository.fetch_top_detail_records()
    assert isinstance(detail_records, DetailScoreRecords)
    assert len(detail_records.records) == 2
    assert detail_records.records[0].input_test_case == "test10.txt"
    assert detail_records.records[0].top_score == 500
    assert detail_records.records[1].input_test_case == "test11.txt"
    assert detail_records.records[1].top_score == 550
