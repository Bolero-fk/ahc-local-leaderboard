from typing import Optional

from ahc_local_leaderboard.models.detail_score_record import DetailScoreRecord


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

    def add_score(self, detail_record: DetailScoreRecord, relative_score: int) -> None:
        if detail_record.absolute_score is not None:
            self.total_absolute_score += detail_record.absolute_score
        else:
            self.invalid_score_count += 1

        self.total_relative_score += relative_score


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
