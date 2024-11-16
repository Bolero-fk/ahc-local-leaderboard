from ahc_local_leaderboard.database.database_manager import (
    DatabaseManager,
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.models.test_case import TestCase


class RecordWriteService:
    """データベースへのスコアやテストケース情報の書き込みを管理するサービスクラス。"""

    def __init__(
        self,
        database_manager: DatabaseManager,
        score_history_repo: ScoreHistoryRepository,
        test_case_repo: TestCaseRepository,
        top_score_repo: TopScoresRepository,
    ):
        self.database_manager = database_manager
        self.score_history_repo = score_history_repo
        self.test_case_repo = test_case_repo
        self.top_score_repo = top_score_repo

    def setup_database(self) -> None:
        """データベースのセットアップを行います。"""
        self.database_manager.setup()

    def reserve_empty_score_history_record(self, submission_time: str) -> SummaryScoreRecord:
        """指定した提出時間で空のスコア履歴レコードを仮登録します。"""
        return self.score_history_repo.reserve_empty_score_history_record(submission_time)

    def update_score_history(self, score_record: SummaryScoreRecord) -> None:
        """スコア履歴レコードを指定の内容で更新します。"""
        assert 0 < score_record.id
        self.score_history_repo.update_score_history(score_record)

    def insert_test_case(self, test_case: TestCase, score_history_id: int) -> None:
        """指定の提出IDに関連するテストケースをデータベースに挿入します。"""
        assert 0 < score_history_id
        self.test_case_repo.insert_test_case(test_case, score_history_id)

    def update_top_score(self, test_case: TestCase, score_history_id: int) -> None:
        """指定のテストケースでトップスコアを更新します。"""
        assert 0 < score_history_id
        self.top_score_repo.update_top_score(test_case, score_history_id)

    def reset_is_updated_flags(self) -> None:
        """トップスコアの更新フラグをリセットします。"""
        self.top_score_repo.reset_is_updated_flags()
