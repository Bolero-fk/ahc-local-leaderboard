from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class SortConfig:
    """Viewer用の表示順序設定クラス"""

    def __init__(self, column: str, order: str):
        assert order in ["asc", "desc"]

        self.column = column
        self.order = order


class SummaryScoreRecordsSortConfig(SortConfig):
    """SummaryScoreRecords用の表示順序設定クラス"""

    def __init__(self, column: str, order: str):
        assert column in ["id", "rank", "time", "abs", "rel"]
        super().__init__(column, order)

        if column == "id":
            self.key = lambda record: record.id
        elif column == "rank":
            self.key = lambda record: record.relative_rank if record.relative_rank is not None else int("inf")
        elif column == "time":
            self.key = lambda record: record.submission_time
        elif column == "abs":
            self.key = lambda record: record.total_absolute_score
        elif column == "rel":
            self.key = lambda record: record.total_relative_score


class DetailScoreRecordsSortConfig(SortConfig):
    """DetailScoreRecords用の表示順序設定クラス"""

    def __init__(self, column: str, order: str, relative_calculator: RelativeScoreCalculaterInterface):
        assert column in ["id", "abs", "rel"]
        super().__init__(column, order)

        if column == "id":
            self.key = lambda record: record.file_name
        elif column == "abs":
            self.key = lambda record: record.absolute_score if record.absolute_score is not None else int("inf")
        elif column == "rel":
            self.key = lambda record: record.calculate_relative_score(relative_calculator)
