from datetime import datetime

from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.test_file import TestFiles
from ahc_local_leaderboard.submit.relative_score_updater import RelativeScoreUpdater
from ahc_local_leaderboard.submit.reserved_record_updater import ReservedRecordUpdater
from ahc_local_leaderboard.submit.submission_matcher import SubmissionMatcher
from ahc_local_leaderboard.submit.test_case_processor import TestCasesProcessor
from ahc_local_leaderboard.submit.test_file_processor import TestFilesProcessor


class Submitter:
    """入力されたテスト結果をローカル順位表に提出し、データベースを更新するクラス。"""

    def __init__(
        self,
        record_write_service: RecordWriteService,
        test_files_processor: TestFilesProcessor,
        test_case_processor: TestCasesProcessor,
        reserved_record_updater: ReservedRecordUpdater,
        relative_score_updater: RelativeScoreUpdater,
        submission_matcher: SubmissionMatcher,
    ) -> None:
        self.record_write_service = record_write_service
        self.test_files_processor = test_files_processor
        self.test_case_processor = test_case_processor
        self.reserved_record_updater = reserved_record_updater
        self.relative_score_updater = relative_score_updater
        self.submission_matcher = submission_matcher

    def execute(self, test_files: TestFiles, skip_duplicate: bool) -> bool:
        """入力された'test_files'の実行結果をローカル順位表に提出します。"""

        test_cases = self.test_files_processor.process_test_files(test_files)

        if skip_duplicate and self.submission_matcher.is_submission_already_recorded(test_cases):
            return False

        submission_time = datetime.now()
        reserved_record = self.record_write_service.reserve_empty_score_history_record(submission_time)

        self.test_case_processor.process_test_cases(test_cases, reserved_record.id)

        self.reserved_record_updater.update_reserved_record(reserved_record)

        self.relative_score_updater.apply_relative_score_updates()

        return True
