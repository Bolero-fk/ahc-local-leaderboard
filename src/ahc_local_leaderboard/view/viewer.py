from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
    TopDetailScoreRecord,
)
from ahc_local_leaderboard.models.sort_config import (
    DetailScoreRecordsSortConfig,
    SummaryScoreRecordsSortConfig,
)
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)
from ahc_local_leaderboard.view.table_builder import (
    DetailTableBuilder,
    SummaryTableBuilder,
    TopDetailTableBuilder,
)


class Viewer:
    """スコア履歴やテストケースの詳細を表示するクラス。"""

    MAX_SINGLE_RELATIVE_SCORE = 1000000000

    def __init__(
        self, record_read_service: RecordReadService, relative_score_calculator: RelativeScoreCalculaterInterface
    ):
        self.record_read_service = record_read_service
        self.relative_score_calculator = relative_score_calculator
        self.MAX_SUM_RELATIVE_SCORE = self.record_read_service.fetch_test_case_count() * self.MAX_SINGLE_RELATIVE_SCORE

    def show_summary_list(self, list_length: int, sort_config: SummaryScoreRecordsSortConfig) -> None:
        """指定された件数（list_length）の最新スコア履歴とトップスコアを取得し、テーブル形式で表示します。"""
        assert 0 <= list_length

        top_record = self.record_read_service.fetch_top_summary_record()
        score_records = self.record_read_service.fetch_recent_summary_records(list_length)
        score_records.sort_records(sort_config)

        table_builder = SummaryTableBuilder(
            f"Latest {len(score_records.records)} Scores (Including Top Score)", self.MAX_SUM_RELATIVE_SCORE
        )

        table_builder.insert_top_record(top_record)
        table_builder.add_separator_row()
        table_builder.insert_records(score_records.records)
        table_builder.display()

    def show_summary_table(self, summary_record: SummaryScoreRecord) -> None:
        """テストケースの概要情報テーブルを表示します。"""

        table_builder = SummaryTableBuilder(
            f"Submission Summary for ID {summary_record.id}", self.MAX_SUM_RELATIVE_SCORE
        )

        table_builder.insert_record(summary_record)
        table_builder.display()

    def show_test_case_table(
        self,
        detail_records: DetailScoreRecords[DetailScoreRecord],
    ) -> None:
        """テストケースの詳細テーブルを表示します。"""

        table_builder = DetailTableBuilder(
            f"Submission Details for ID {detail_records.id}",
            self.MAX_SINGLE_RELATIVE_SCORE,
            self.relative_score_calculator,
        )

        table_builder.insert_records(detail_records.records)
        table_builder.display()

    def show_detail(self, submission_id: int, sort_config: DetailScoreRecordsSortConfig) -> None:
        """指定された提出IDの詳細テーブルを表示します。"""
        assert 0 < submission_id

        detail_records = self.record_read_service.fetch_detail_records_by_id(submission_id)
        detail_records.sort_records(sort_config)

        self.show_test_case_table(detail_records)

        summary_record = self.record_read_service.fetch_summary_record_by_id(submission_id)
        self.show_summary_table(summary_record)

    def show_latest_detail(self, sort_config: DetailScoreRecordsSortConfig) -> None:
        """最新の提出の詳細テーブルを表示します。"""
        latest_id = self.record_read_service.fetch_latest_submission_id()
        self.show_detail(latest_id, sort_config)

    def show_top_test_case_table(self, detail_records: DetailScoreRecords[TopDetailScoreRecord]) -> None:
        """トップテストケースの詳細テーブルを表示します。"""
        table_builder = TopDetailTableBuilder("Submission Details for Top Case")

        table_builder.insert_records(detail_records.records)
        table_builder.display()

    def show_top_detail(self) -> None:
        """トップテストケースの詳細テーブルを表示します。"""
        detail_records = self.record_read_service.fetch_sorted_top_detail_records()
        self.show_top_test_case_table(detail_records)
