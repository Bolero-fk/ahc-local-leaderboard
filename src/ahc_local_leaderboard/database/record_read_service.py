from typing import Optional

from ahc_local_leaderboard.database.database_manager import (
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
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


class RecordReadService:

    def __init__(
        self,
        score_history_repo: ScoreHistoryRepository,
        test_case_repo: TestCaseRepository,
        top_score_repo: TopScoresRepository,
    ):
        self.score_history_repo = score_history_repo
        self.test_case_repo = test_case_repo
        self.top_score_repo = top_score_repo

    def fetch_all_summary_records(self) -> SummaryScoreRecords:
        """データベース内の全サマリーレコードを取得します。"""
        return self.score_history_repo.fetch_all_records()

    def fetch_latest_submission_id(self) -> int:
        """データベース内の最新のレコードIDを取得します。"""
        return self.score_history_repo.fetch_latest_id()

    def fetch_recent_summary_records(self, limit: int) -> SummaryScoreRecords:
        """データベースから最新順に 'limit' 件のレコードを取得します。"""
        assert 0 < limit
        return self.score_history_repo.fetch_recent_summary_records(limit)

    def fetch_summary_record_by_submission_id(self, submission_id: int) -> SummaryScoreRecord:
        """指定IDのレコードを取得します。"""
        assert 0 < submission_id
        return self.score_history_repo.fetch_summary_record_by_submission_id(submission_id)

    def fetch_detail_records_by_submission_id(self, submission_id: int) -> DetailScoreRecords[DetailScoreRecord]:
        """指定した提出IDのテストケースレコードを取得します。"""
        assert 0 < submission_id
        return self.test_case_repo.fetch_records_by_submission_id(submission_id)

    def fetch_absolute_score_for_test_case(self, test_case_name: str, submission_id: int) -> Optional[int]:
        """指定した提出IDの 'test_case_name' のスコアを取得します。"""
        assert 0 < submission_id
        return self.test_case_repo.fetch_absolute_score_for_test_case(test_case_name, submission_id)

    def fetch_top_summary_record(self) -> TopSummaryScoreRecord:
        """トップテストケースのサマリーレコードを取得します。"""
        return self.top_score_repo.fetch_top_summary_record()

    def fetch_test_case_count(self) -> int:
        """テストケースの総数を取得します。"""
        return self.top_score_repo.fetch_test_case_count()

    def fetch_top_detail_records(self) -> DetailScoreRecords[TopDetailScoreRecord]:
        """トップテストケースの詳細レコードを取得します。"""
        return self.top_score_repo.fetch_top_detail_records()

    def fetch_sorted_top_detail_records(self) -> DetailScoreRecords[TopDetailScoreRecord]:
        """ファイル名順にソートしたトップテストケースの詳細レコードを取得します。"""
        detail_records = self.fetch_top_detail_records()
        detail_records.sort_records_by_input_file_name()
        return detail_records

    def fetch_top_score_for_test_case(self, test_case: TestCase) -> Optional[int]:
        """指定したテストケースのトップスコアを取得します。"""
        return self.top_score_repo.fetch_top_score_for_test_case(test_case)

    def fetch_recently_updated_top_scores(self) -> list[UpdatedTopScore]:
        """更新されたトップスコアの情報を取得します。"""
        return self.top_score_repo.fetch_recently_updated_top_scores()
