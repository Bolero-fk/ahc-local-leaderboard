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

    def fetch_top_summary_record(self) -> TopSummaryScoreRecord:
        return TopScoresRepository.fetch_top_summary_record()

    def fetch_test_case_count(self) -> int:
        return TopScoresRepository.fetch_test_case_count()

    def fetch_latest_records(self, limit: int) -> SummaryScoreRecords:
        return ScoreHistoryRepository.fetch_latest_records(limit)

    def fetch_summary_record(self, submission_id: int) -> SummaryScoreRecord:
        return ScoreHistoryRepository.fetch_record(submission_id)

    def fetch_detail_records(self, submission_id: int) -> DetailScoreRecords[DetailScoreRecord]:
        return TestCaseRepository.fetch_records(submission_id)

    def fetch_latest_submission_id(self) -> int:
        return ScoreHistoryRepository.fetch_latest_id()

    def fetch_top_detail_records(self) -> DetailScoreRecords[TopDetailScoreRecord]:
        return TopScoresRepository.fetch_top_detail_records()

    def fetch_sorted_top_detail_records(self) -> DetailScoreRecords[TopDetailScoreRecord]:
        detail_records = self.fetch_top_detail_records()
        detail_records.sort_records_by_input_file_name()
        return detail_records

    def fetch_top_score(self, test_case: TestCase) -> Optional[int]:
        return TopScoresRepository.fetch_top_score(test_case)
