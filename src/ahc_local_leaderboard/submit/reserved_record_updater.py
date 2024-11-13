from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class ReservedRecordUpdater:
    def __init__(
        self,
        record_read_service: RecordReadService,
        record_write_service: RecordWriteService,
        relative_score_calculator: RelativeScoreCalculaterInterface,
    ) -> None:
        self.record_read_service = record_read_service
        self.record_write_service = record_write_service
        self.relative_score_calculator = relative_score_calculator

    def update_reserved_record(self, reserved_record: SummaryScoreRecord) -> None:
        """TestCasesテーブルの内容でScoreHistoryテーブルに一時的に挿入されている'reserved_record'を更新する"""
        detail_records = self.record_read_service.fetch_detail_records_by_submission_id(reserved_record.id)
        reserved_record.update(detail_records, self.relative_score_calculator)
        self.record_write_service.update_score_history(reserved_record)
