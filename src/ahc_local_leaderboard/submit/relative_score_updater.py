from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    SummaryScoreRecords,
)
from ahc_local_leaderboard.models.updated_top_score import UpdatedTopScore
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class RelativeScoreUpdater:
    def __init__(
        self,
        record_read_service: RecordReadService,
        record_write_service: RecordWriteService,
        relative_score_calculator: RelativeScoreCalculaterInterface,
    ) -> None:
        self.record_read_service = record_read_service
        self.record_write_service = record_write_service
        self.relative_score_calculator = relative_score_calculator

    def calculate_individual_relative_score_diff(
        self,
        non_latest_record: SummaryScoreRecord,
        updated_top_score: UpdatedTopScore,
    ) -> int:
        """指定されたレコードの相対スコア更新前後の差分を計算する"""

        absolute_score = self.record_read_service.fetch_absolute_score_for_test_case(
            updated_top_score.file_name, non_latest_record.id
        )
        return self.relative_score_calculator.calculate_diff_relative_score(
            absolute_score, updated_top_score.top_score, updated_top_score.second_top_score
        )

    def calculate_total_relative_score_diff(
        self,
        non_latest_record: SummaryScoreRecord,
        updated_top_scores: list[UpdatedTopScore],
    ) -> int:
        """指定されたレコードの相対スコア更新前後の差分の総和を計算する"""

        total_score_diff = 0
        for updated_top_score in updated_top_scores:
            total_score_diff += self.calculate_individual_relative_score_diff(non_latest_record, updated_top_score)

        return total_score_diff

    def update_relative_scores(self, records: list[SummaryScoreRecord]) -> None:
        """入力されたレコードの相対スコアを更新する"""

        updated_top_scores = self.record_read_service.fetch_recently_updated_top_scores()
        for summary_record in records:
            total_relative_score_diff = self.calculate_total_relative_score_diff(summary_record, updated_top_scores)
            summary_record.total_relative_score += total_relative_score_diff

    def fetch_latest_and_remaining_records(self) -> tuple[SummaryScoreRecord, list[SummaryScoreRecord]]:
        """データベースから最新のレコードと、それ以外のレコードを取得する"""

        all_summary_records = self.record_read_service.fetch_all_summary_records()

        latest_record = all_summary_records.get_latest_record()

        remaining_records = all_summary_records.get_records_except_latest()

        return latest_record, remaining_records

    def apply_relative_score_updates(self) -> None:
        """データベース内の相対スコアに関連する内容を更新する"""

        latest_record, remaining_records = self.fetch_latest_and_remaining_records()

        # 最新の要素はデータベースに追加時に計算済みなのでそれ以外を更新する
        self.update_relative_scores(remaining_records)

        updated_records = SummaryScoreRecords(remaining_records)

        updated_records.add_record(latest_record)

        updated_records.update_relative_ranks()

        for summary_record in updated_records:
            self.record_write_service.update_score_history(summary_record)

        self.record_write_service.reset_is_updated_flags()
