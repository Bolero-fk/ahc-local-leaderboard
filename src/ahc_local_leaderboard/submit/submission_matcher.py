from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
)
from ahc_local_leaderboard.models.test_case import TestCases


class SubmissionMatcher:
    """同様の提出が既にデータベースに記録されているかをチェックするクラス"""

    def __init__(self, record_read_service: RecordReadService) -> None:
        self.record_read_service = record_read_service

    def fetch_same_score_records(self, sum_score: int) -> list[DetailScoreRecords[DetailScoreRecord]]:
        """指定されたスコアと一致する記録を取得します。"""
        same_score_records = self.record_read_service.fetch_records_by_absolute_score(sum_score)
        return [self.record_read_service.fetch_detail_records_by_id(record.id) for record in same_score_records]

    def is_submission_in_records(
        self, detail_records: list[DetailScoreRecords[DetailScoreRecord]], test_cases: TestCases
    ) -> bool:
        """特定のテストケースが既存の記録に含まれるか確認します。"""
        for detail_record in detail_records:
            if any(
                test_cases.contains_test_case(record.file_name, record.absolute_score)
                for record in detail_record.records
            ):
                return True
        return False

    def is_submission_already_recorded(self, test_cases: TestCases) -> bool:
        """同様の提出が既に記録されているかを確認します。"""
        sum_score = test_cases.calculate_sum_score()
        same_score_records = self.fetch_same_score_records(sum_score)
        return self.is_submission_in_records(same_score_records, test_cases)
