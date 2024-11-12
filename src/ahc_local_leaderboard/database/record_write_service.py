from ahc_local_leaderboard.database.database_manager import (
    DatabaseManager,
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.models.test_case import TestCase


class RecordWriteService:

    def __init__(
        self,
        score_history_repo: ScoreHistoryRepository,
        test_case_repo: TestCaseRepository,
        top_score_repo: TopScoresRepository,
    ):
        self.score_history_repo = score_history_repo
        self.test_case_repo = test_case_repo
        self.top_score_repo = top_score_repo

    def insert_test_case(self, test_case: TestCase, score_history_id: int) -> None:
        TestCaseRepository.insert_test_case(test_case, score_history_id)

    def update_top_score(self, test_case: TestCase, score_history_id: int) -> None:
        TopScoresRepository.update_top_score(test_case, score_history_id)

    def update_score_history(self, score_record: SummaryScoreRecord) -> None:
        ScoreHistoryRepository.update_score_history(score_record)

    def reserve_score_history(self, submission_time: str) -> SummaryScoreRecord:
        return ScoreHistoryRepository.reserve_score_history(submission_time)

    def reset_is_updated_flags(self) -> None:
        TopScoresRepository.reset_is_updated_flags()

    def setup_database(self) -> None:
        DatabaseManager.setup()
