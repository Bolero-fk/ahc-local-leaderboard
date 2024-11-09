from datetime import datetime
from typing import Optional

from ahc_local_leaderboard.database.database_manager import (
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
)
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.models.test_case import TestCase, TestCases
from ahc_local_leaderboard.models.test_file import TestFiles
from ahc_local_leaderboard.submit.test_file_processor import (
    AtCoderTestFileProcessor,
    TestFilesProcessor,
)
from ahc_local_leaderboard.utils.file_utility import FileUtility
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class Submitter:

    def __init__(self, relative_score_calculator: RelativeScoreCalculaterInterface) -> None:
        self.relative_score_calculator = relative_score_calculator

    def _process_test_cases(self, test_cases: TestCases, score_history_id: int) -> SummaryScoreRecord:
        """各テストケースのスコアと記録を処理する"""
        detail_records = DetailScoreRecords[DetailScoreRecord](score_history_id, [])
        score_record = SummaryScoreRecord(score_history_id, self.submission_time, 0, 0, 0, None)

        for test_case in test_cases:
            new_top_score = self._try_update_top_score(test_case, score_history_id)
            relative_score = self.relative_score_calculator(test_case.score, new_top_score)

            TestCaseRepository.insert_test_case(test_case, score_history_id)

            detail_record = DetailScoreRecord(test_case.file_name, test_case.score, new_top_score)
            detail_records.records.append(detail_record)
            score_record.add_score(detail_record, relative_score)

        return score_record

    def _try_update_top_score(self, test_case: TestCase, score_history_id: int) -> Optional[int]:
        """テストケースのスコアを評価し、必要に応じてトップスコアを更新する"""
        top_score = TopScoresRepository.fetch_top_score(test_case)
        is_topscore_case = self.relative_score_calculator.is_better_score(test_case.score, top_score)

        if is_topscore_case:
            TopScoresRepository.update_top_score(test_case, score_history_id)
            FileUtility.copy_submit_file_to_leaderboard(self.submit_file_path, test_case)

        new_top_score = test_case.score if is_topscore_case else top_score
        return new_top_score

    def execute(self, test_files: TestFiles, submit_file_path: str = "out") -> None:
        self.submit_file_path = submit_file_path
        self.submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        test_files_processor = TestFilesProcessor(test_files, AtCoderTestFileProcessor())
        test_cases = test_files_processor.process_test_files()

        score_history_id = ScoreHistoryRepository.reserve_score_history(self.submission_time)

        score_record = self._process_test_cases(test_cases, score_history_id)
        ScoreHistoryRepository.update_score_history(score_record)
