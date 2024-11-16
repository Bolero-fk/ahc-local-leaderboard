from datetime import datetime
from typing import Iterator, Optional

from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    DetailScoreRecords,
)
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class SummaryScoreRecord:

    def __init__(
        self,
        id: int,
        submission_time: str,
        total_absolute_score: int,
        total_relative_score: int,
        invalid_score_count: int,
        relative_rank: Optional[int],
    ) -> None:
        assert 0 < id
        assert 0 <= total_relative_score
        assert 0 <= invalid_score_count
        assert not isinstance(relative_rank, int) or 0 < relative_rank

        self.id = id
        self.submission_time = submission_time
        self.total_absolute_score = total_absolute_score
        self.total_relative_score = total_relative_score
        self.invalid_score_count = invalid_score_count
        self.relative_rank = relative_rank

    def update(
        self,
        detail_records: DetailScoreRecords[DetailScoreRecord],
        relative_score_calculator: RelativeScoreCalculaterInterface,
    ) -> None:

        self.total_absolute_score = detail_records.calculate_total_absolute_score()
        self.total_relative_score = detail_records.calculate_total_relative_score(relative_score_calculator)
        self.invalid_score_count = detail_records.calculate_invalid_score_count()

    @classmethod
    def from_row(cls, row: tuple[int, str, int, int, int, Optional[int]]) -> "SummaryScoreRecord":
        """クエリ結果のタプルからSummaryScoreRecordインスタンスを生成します"""
        return cls(*row)


class TopSummaryScoreRecord:

    def __init__(
        self,
        total_absolute_score: int,
        total_relative_score: int,
        invalid_score_count: int,
    ) -> None:
        assert 0 <= total_relative_score
        assert 0 <= invalid_score_count

        self.total_absolute_score = total_absolute_score
        self.total_relative_score = total_relative_score
        self.invalid_score_count = invalid_score_count


class SummaryScoreRecords:

    def __init__(self, records: list[SummaryScoreRecord]) -> None:
        self.records = records

    def __iter__(self) -> Iterator[SummaryScoreRecord]:
        return iter(self.records)

    def add_record(self, record: SummaryScoreRecord) -> None:
        """指定された record を records に追加する"""
        return self.records.append(record)

    def update_relative_ranks(self) -> None:
        """total_relative_score に基づいて records を降順に並べ、relative_rank を設定する"""
        self.records.sort(key=lambda record: record.total_relative_score, reverse=True)

        relative_rank = 1
        for record in self.records:
            record.relative_rank = relative_rank
            relative_rank += 1

    # TODO: submission_timeの型は datetime にする
    def get_latest_record(self) -> SummaryScoreRecord:
        """submission_time が最も新しい record を返す"""
        assert len(self.records) != 0

        return max(self.records, key=lambda record: datetime.strptime(record.submission_time, "%Y-%m-%d %H:%M:%S"))

    def get_records_except_latest(self) -> list[SummaryScoreRecord]:
        """submission_time が最も新しい record 以外の records を返す"""
        latest_record = self.get_latest_record()
        return [record for record in self.records if record != latest_record]
