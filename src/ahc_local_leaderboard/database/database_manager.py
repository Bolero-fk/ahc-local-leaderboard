import sqlite3
import traceback
from typing import Optional, Type

from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
    TopDetailScoreRecord,
)
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    SummaryScoreRecords,
    TopSummaryScoreRecord,
)
from ahc_local_leaderboard.models.test_case import TestCase


class DatabaseManager:
    """データベース接続を管理するクラス"""

    _DB_PATH = "leader_board/leader_board.db"

    def __init__(self) -> None:
        self.connection: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        """with 文の開始時にデータベースに接続"""
        self.connection = sqlite3.connect(self._DB_PATH)
        return self.connection

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[traceback.TracebackException],
    ) -> None:
        """with 文の終了時にデータベース接続を閉じる"""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None

    SCORE_HISTORY_TABLE = """
    CREATE TABLE IF NOT EXISTS score_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total_absolute_score INTEGER,
        total_relative_score INTEGER,
        invalid_score_count INTEGER DEFAULT 0,
        relative_rank INTEGER DEFAULT NULL,
        submission_time DATETIME NOT NULL UNIQUE
    )
    """

    TEST_CASES_TABLE = """
    CREATE TABLE IF NOT EXISTS test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_case_input TEXT NOT NULL,
        absolute_score INTEGER,
        score_history_id INTEGER NOT NULL,
        FOREIGN KEY (score_history_id) REFERENCES score_history(id) ON DELETE CASCADE,
        UNIQUE(test_case_input, score_history_id)
    )
    """

    TOP_SCORES_TABLE = """
    CREATE TABLE IF NOT EXISTS top_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_case_input TEXT NOT NULL UNIQUE,
        top_absolute_score INTEGER DEFAULT NULL,
        second_top_score INTEGER DEFAULT NULL,
        is_updated BOOLEAN NOT NULL DEFAULT FALSE,
        score_history_id INTEGER NOT NULL,
        FOREIGN KEY (score_history_id) REFERENCES score_history(id) ON DELETE SET NULL
    )
    """

    @staticmethod
    def setup() -> None:
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(DatabaseManager.SCORE_HISTORY_TABLE)
            cursor.execute(DatabaseManager.TEST_CASES_TABLE)
            cursor.execute(DatabaseManager.TOP_SCORES_TABLE)


class ScoreHistoryRepository:
    @staticmethod
    def reserve_score_history(submission_time: str) -> SummaryScoreRecord:
        """スコア履歴テーブルに空行を挿入し、そのIDを返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO score_history (submission_time)
                VALUES (?)
            """,
                (submission_time,),
            )

        lastrowid: Optional[int] = cursor.lastrowid
        if lastrowid is None:
            raise ValueError("Failed to insert a new row into the score_history table.")

        return SummaryScoreRecord(lastrowid, submission_time, 0, 0, 0, None)

    @staticmethod
    def update_score_history(record: SummaryScoreRecord) -> None:
        """指定されたスコアレコードの情報でスコア履歴テーブルを更新します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE score_history
                SET total_absolute_score = ?, total_relative_score = ?, invalid_score_count = ?, relative_rank = ?
                WHERE id = ?
            """,
                (
                    record.total_absolute_score,
                    record.total_relative_score,
                    record.invalid_score_count,
                    record.relative_rank,
                    record.id,
                ),
            )

    @staticmethod
    def fetch_record(id: int) -> SummaryScoreRecord:
        """指定されたIDのスコアレコードを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, submission_time, total_absolute_score, total_relative_score,
                            invalid_score_count, relative_rank
                FROM score_history
                WHERE id = ?
            """,
                (id,),
            )
            row = cursor.fetchone()

        if row is None:
            raise ValueError(f"No record found for id: {id}")

        return SummaryScoreRecord(*row)

    @staticmethod
    def fetch_all_record() -> SummaryScoreRecords:
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, submission_time, total_absolute_score, total_relative_score,
                            invalid_score_count, relative_rank
                FROM score_history
            """
            )

            rows = cursor.fetchall()

        records = [SummaryScoreRecord(*row) for row in rows]
        return SummaryScoreRecords(records)

    @staticmethod
    def fetch_non_latest_records() -> SummaryScoreRecords:
        """最新エントリ以外のスコア履歴レコードを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, submission_time, total_absolute_score, total_relative_score,
                            invalid_score_count, relative_rank
                FROM score_history
                WHERE submission_time < (SELECT MAX(submission_time) FROM score_history)
                ORDER BY submission_time
            """
            )
            rows = cursor.fetchall()

        records = [SummaryScoreRecord(*row) for row in rows]
        return SummaryScoreRecords(records)

    @staticmethod
    def fetch_latest_id() -> int:
        """最新のスコア履歴IDを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM score_history ORDER BY submission_time DESC LIMIT 1")
            result: Optional[tuple[int]] = cursor.fetchone()

        if result is None:
            raise ValueError("No entries found in the score_history table.")

        return result[0]

    @staticmethod
    def fetch_latest_record() -> SummaryScoreRecord:
        """最新のスコア履歴レコードを取得します"""
        latest_id = ScoreHistoryRepository.fetch_latest_id()
        return ScoreHistoryRepository.fetch_record(latest_id)

    @staticmethod
    def fetch_latest_records(limit: int) -> SummaryScoreRecords:
        """最新のスコア履歴レコードを指定数分取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, submission_time, total_absolute_score, total_relative_score,
                            invalid_score_count, relative_rank
                FROM score_history
                ORDER BY submission_time DESC
                LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()

        records = [SummaryScoreRecord(*row) for row in rows]
        return SummaryScoreRecords(records)

    @staticmethod
    def count_higher_score_records(record: SummaryScoreRecord) -> int:
        """指定レコードより高いスコアのレコード数を返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM score_history
                WHERE total_relative_score >= ? and id != ?
            """,
                (record.total_relative_score, record.id),
            )
            result: tuple[int] = cursor.fetchone()

            return result[0]

    @staticmethod
    def fetch_lower_score_records(record: SummaryScoreRecord) -> SummaryScoreRecords:
        """指定レコードより低いスコアのレコードを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, submission_time, total_absolute_score, total_relative_score,
                           invalid_score_count, relative_rank
                FROM score_history
                WHERE total_relative_score < ? and id != ?
            """,
                (record.total_relative_score, record.id),
            )
            rows = cursor.fetchall()

        records = [SummaryScoreRecord(*row) for row in rows]
        return SummaryScoreRecords(records)

    @staticmethod
    def exists_id(id: int) -> bool:
        """指定されたidがscore_historyテーブルに存在するか確認"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM score_history
                WHERE id = ?
            """,
                (id,),
            )
            result: int = cursor.fetchone()[0]

            return result > 0


class TestCaseRepository:
    @staticmethod
    def insert_test_case(test_case: TestCase, score_history_id: int) -> None:
        """テストケース情報をテストケーステーブルに挿入します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO test_cases (test_case_input, absolute_score, score_history_id)
                VALUES (?, ?, ?)
            """,
                (test_case.file_name, test_case.score, score_history_id),
            )

    @staticmethod
    def fetch_absolute_score(test_case_input: str, score_history_id: int) -> Optional[int]:
        """指定されたtest_case_inputとscore_history_idに対応するabsolute_scoreを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT absolute_score
                FROM test_cases
                WHERE test_case_input = ? AND score_history_id = ?
            """,
                (test_case_input, score_history_id),
            )
            result: Optional[tuple[Optional[int]]] = cursor.fetchone()

        if result is None:
            raise ValueError(f"No absolute score found for {test_case_input} and score_history_id={score_history_id}")

        return result[0]

    @staticmethod
    def fetch_records(submission_id: int) -> DetailScoreRecords[DetailScoreRecord]:
        """指定された提出IDに関連するレコードを取得します"""

        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT tc.test_case_input, tc.absolute_score, ts.top_absolute_score
                FROM test_cases AS tc
                LEFT JOIN top_scores AS ts ON tc.test_case_input = ts.test_case_input
                WHERE tc.score_history_id = ?
            """,
                (submission_id,),
            )

            rows = cursor.fetchall()
        records = [DetailScoreRecord(*row) for row in rows]
        return DetailScoreRecords[DetailScoreRecord](submission_id, records)


class TopScoresRepository:
    @staticmethod
    def update_top_score(test_case: TestCase, score_history_id: int) -> None:
        """指定されたテストケースのスコアでトップスコアテーブルを更新します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?", (test_case.file_name,)
            )
            result = cursor.fetchone()
            second_top_score = result[0] if result else None
            cursor.execute(
                """
                INSERT OR REPLACE INTO top_scores (test_case_input, top_absolute_score,
                           second_top_score, is_updated, score_history_id)
                VALUES (?, ?, ?, ?, ?)
            """,
                (test_case.file_name, test_case.score, second_top_score, True, score_history_id),
            )

    @staticmethod
    def fetch_top_score(test_case: TestCase) -> Optional[int]:
        """指定されたテストケースのトップスコアを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?", (test_case.file_name,)
            )
            result = cursor.fetchone()
        return result[0] if result else None

    @staticmethod
    def reset_is_updated_flags() -> None:
        """top_scoresテーブルのis_updatedフラグをすべてFALSEにリセットします"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE top_scores
                SET is_updated = FALSE
                WHERE is_updated = TRUE
            """
            )

    @staticmethod
    def fetch_test_case_count() -> int:
        """登録されているテストケースの総数を取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM top_scores")
            result: tuple[int] = cursor.fetchone()
        return result[0]

    @staticmethod
    def fetch_updated_top_scores() -> list[tuple[str, int, int]]:
        """is_updatedがTRUEであるテストケースのトップスコアおよびセミトップスコアを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT test_case_input, top_absolute_score, second_top_score
                FROM top_scores
                WHERE is_updated = TRUE
            """
            )

            return cursor.fetchall()

    @staticmethod
    def fetch_top_summary_record() -> TopSummaryScoreRecord:
        """top_scoresテーブルからトップスコアのサマリー情報を生成し、返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(SUM(top_absolute_score), 0) AS total_absolute_score,
                       COUNT(*) AS total_cases,
                       COUNT(*) - COUNT(top_absolute_score) AS invalid_score_count
                FROM top_scores
            """
            )
            total_absolute_score, total_cases, invalid_score_count = cursor.fetchone()

        # Total Relative Score は全テストケースが最大スコアを取った場合を仮定
        total_relative_score = 10**9 * total_cases
        return TopSummaryScoreRecord(total_absolute_score, total_relative_score, invalid_score_count)

    @staticmethod
    def fetch_top_detail_records() -> DetailScoreRecords[TopDetailScoreRecord]:
        """top_scoresテーブルからトップスコアの詳細情報を生成し、返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT test_case_input, top_absolute_score, score_history_id
                FROM top_scores
            """
            )
            rows = cursor.fetchall()
        records = [TopDetailScoreRecord(*row) for row in rows]
        return DetailScoreRecords[TopDetailScoreRecord]("Top", records)
