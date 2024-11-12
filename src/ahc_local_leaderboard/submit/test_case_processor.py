from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.test_case import TestCase, TestCases
from ahc_local_leaderboard.utils.file_utility import FileUtility
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class TestCaseProcessor:
    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(
        self,
        record_read_service: RecordReadService,
        record_write_service: RecordWriteService,
        relative_score_calculator: RelativeScoreCalculaterInterface,
        file_utility: FileUtility,
    ) -> None:
        self.record_read_service = record_read_service
        self.record_write_service = record_write_service
        self.relative_score_calculator = relative_score_calculator
        self.file_utility = file_utility

    def update_top_score(self, test_case: TestCase, score_history_id: int) -> None:
        """トップスコアを'test_case'の内容で更新し、提出ファイルをリーダーボードにコピーする"""
        self.record_write_service.update_top_score(test_case, score_history_id)
        self.file_utility.copy_submit_file_to_leaderboard(test_case)

    def try_update_top_score(self, test_case: TestCase, score_history_id: int) -> None:
        """'test_case'のスコアを評価し、トップスコアを超えているならトップスコアを更新する"""
        top_score = self.record_read_service.fetch_top_score(test_case)
        if self.relative_score_calculator.is_better_score(test_case.score, top_score):
            self.update_top_score(test_case, score_history_id)

    def process_test_case(self, test_case: TestCase, score_history_id: int) -> None:
        """'test_case'の内容をTeseCasesテーブルに追加し、トップスコアを超えている場合はTopScoresテーブルを更新する"""
        self.try_update_top_score(test_case, score_history_id)
        self.record_write_service.insert_test_case(test_case, score_history_id)


class TestCasesProcessor:
    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(
        self,
        test_case_processor: TestCaseProcessor,
    ) -> None:
        self.test_case_processor = test_case_processor

    def process_test_cases(self, test_cases: TestCases, score_history_id: int) -> None:
        """全テストケースのスコア評価と記録を処理する"""

        for test_case in test_cases:
            self.test_case_processor.process_test_case(test_case, score_history_id)