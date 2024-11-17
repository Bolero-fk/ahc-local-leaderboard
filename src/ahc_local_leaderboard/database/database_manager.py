import sqlite3
import traceback
from datetime import datetime
from typing import Optional, Type

from ahc_local_leaderboard.consts import get_database_path, get_datetime_format
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
from ahc_local_leaderboard.models.updated_top_score import UpdatedTopScore


class DatabaseManager:
    """データベース接続の管理とテーブルの作成を行うクラス。"""

    def __init__(self) -> None:
        self.connection: Optional[sqlite3.Connection] = None
        self.transaction_mode = False

    def open(self) -> sqlite3.Connection:
        if not self.connection:
            self._db_path = str(get_database_path())
            self.connection = sqlite3.connect(self._db_path)
            self.connection.isolation_level = None

        return self.connection

    def __enter__(self) -> sqlite3.Connection:
        """with 文の開始時にデータベースに接続します。"""

        return self.open()

    def close(self) -> None:
        if self.connection:
            if not self.transaction_mode:
                self.connection.commit()
                self.connection.close()
                self.connection = None

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[traceback.TracebackException],
    ) -> None:
        """with 文の終了時にデータベース接続を閉じます。"""
        self.close()

    def begin_transaction(self) -> None:
        assert not self.transaction_mode

        conn = self.open()
        conn.execute("BEGIN")
        self.transaction_mode = True

    def commit(self) -> None:
        assert self.transaction_mode

        conn = self.open()
        conn.commit()
        self.transaction_mode = False
        self.close()

    def rollback(self) -> None:
        assert self.transaction_mode

        conn = self.open()
        conn.rollback()
        self.transaction_mode = False
        self.close()

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
        """必要なテーブルを作成してデータベースを初期化します。"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute(DatabaseManager.SCORE_HISTORY_TABLE)
            cursor.execute(DatabaseManager.TEST_CASES_TABLE)
            cursor.execute(DatabaseManager.TOP_SCORES_TABLE)


class ScoreHistoryRepository:
    """スコア履歴テーブルへの操作を提供するクラス。"""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def reserve_empty_score_history_record(self, submission_time: datetime) -> SummaryScoreRecord:
        """指定された日時で空のスコア履歴レコードを作成し、そのレコードを返します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO score_history (submission_time)
                VALUES (?)
            """,
                (submission_time.strftime(get_datetime_format()),),
            )

            lastrowid: Optional[int] = cursor.lastrowid
            if lastrowid is None:
                raise ValueError("Failed to insert a new row into the score_history table.")

            return SummaryScoreRecord(lastrowid, submission_time, 0, 0, 0, None)

    def update_score_history(self, record: SummaryScoreRecord) -> None:
        """指定されたスコア履歴レコードの内容でデータベースを更新します。"""
        with self.db_manager as conn:
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

    def fetch_summary_record_by_id(self, id: int) -> SummaryScoreRecord:
        """指定されたIDのスコア履歴レコードを取得し、返します。"""
        with self.db_manager as conn:
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

        return SummaryScoreRecord.from_row(row)

    def fetch_all_records(self) -> SummaryScoreRecords:
        """すべてのスコア履歴レコードを取得し、返します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, submission_time, total_absolute_score, total_relative_score,
                            invalid_score_count, relative_rank
                FROM score_history
            """
            )

            rows = cursor.fetchall()

        records = [SummaryScoreRecord.from_row(row) for row in rows]
        return SummaryScoreRecords(records)

    def fetch_latest_id(self) -> int:
        """最新のスコア履歴レコードのIDを取得して返します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM score_history ORDER BY submission_time DESC LIMIT 1")
            result: Optional[tuple[int]] = cursor.fetchone()

        if result is None:
            raise ValueError("No entries found in the score_history table.")

        return result[0]

    def fetch_recent_summary_records(self, limit: int) -> SummaryScoreRecords:
        """指定した数の最新スコア履歴レコードを取得し、返します。"""
        with self.db_manager as conn:
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

        records = [SummaryScoreRecord.from_row(row) for row in rows]
        return SummaryScoreRecords(records)

    def exists_id(self, id: int) -> bool:
        """指定したIDのスコア履歴レコードが存在するかを確認します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM score_history
                WHERE id = ?
                LIMIT 1
            """,
                (id,),
            )

            result: int = cursor.fetchone()[0]
            return result > 0


class TestCaseRepository:
    """テストケーステーブルへの操作を提供するクラス。"""

    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def insert_test_case(self, test_case: TestCase, score_history_id: int) -> None:
        """指定されたテストケース情報をテストケーステーブルに挿入します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO test_cases (test_case_input, absolute_score, score_history_id)
                VALUES (?, ?, ?)
            """,
                (test_case.file_name, test_case.score, score_history_id),
            )

    def fetch_absolute_score_for_test_case(self, test_case_input: str, score_history_id: int) -> Optional[int]:
        """指定されたテストケースとスコア履歴IDの絶対スコアを取得します。"""
        with self.db_manager as conn:
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

    def fetch_records_by_id(self, submission_id: int) -> DetailScoreRecords[DetailScoreRecord]:
        """指定された提出IDに関連するすべてのテストケースレコードを取得します。"""

        with self.db_manager as conn:
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
        records = [DetailScoreRecord.from_row(row) for row in rows]
        return DetailScoreRecords[DetailScoreRecord](submission_id, records)


class TopScoresRepository:
    """トップスコアテーブルへの操作を提供するクラス。"""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def update_top_score(self, test_case: TestCase, score_history_id: int) -> None:
        """指定テストケースのスコアをもとにトップスコアを更新します。"""
        with self.db_manager as conn:
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

    def fetch_top_score_for_test_case(self, test_case: TestCase) -> Optional[int]:
        """指定テストケースのトップスコアを取得します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?", (test_case.file_name,)
            )
            result = cursor.fetchone()
        return result[0] if result else None

    def reset_is_updated_flags(self) -> None:
        """トップスコアテーブルのすべてのis_updatedフラグをリセットします。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE top_scores
                SET is_updated = FALSE
                WHERE is_updated = TRUE
            """
            )

    def fetch_test_case_count(self) -> int:
        """トップスコアテーブルに登録されたテストケース数を取得します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM top_scores")
            result: tuple[int] = cursor.fetchone()
        return result[0]

    def fetch_recently_updated_top_scores(self) -> list[UpdatedTopScore]:
        """is_updatedがTRUEのテストケースのトップスコアとセカンドトップスコアを取得します。"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT test_case_input, top_absolute_score, second_top_score
                FROM top_scores
                WHERE is_updated = TRUE
            """
            )

            records = cursor.fetchall()

            return [UpdatedTopScore(file_name=row[0], top_score=row[1], second_top_score=row[2]) for row in records]

    def fetch_top_summary_record(self) -> TopSummaryScoreRecord:
        """トップスコアテーブルのトップスコア情報を集計し、概要レコードを返します。"""
        with self.db_manager as conn:
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

    def fetch_top_detail_records(self) -> DetailScoreRecords[TopDetailScoreRecord]:
        """トップスコアテーブルのトップスコア詳細レコードを取得します。"""
        with self.db_manager as conn:
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
