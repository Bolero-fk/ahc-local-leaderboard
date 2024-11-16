from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from rich.table import Table

from ahc_local_leaderboard.models.detail_score_record import (
    DetailScoreRecord,
    TopDetailScoreRecord,
)
from ahc_local_leaderboard.models.summary_score_record import (
    SummaryScoreRecord,
    TopSummaryScoreRecord,
)
from ahc_local_leaderboard.utils.console_handler import ConsoleHandler
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)
from ahc_local_leaderboard.view.score_formatter import ScoreFormatter

T = TypeVar("T")


class TableBuilder(ABC, Generic[T]):
    """テーブル構築のための基底クラス。"""

    def __init__(self, title: str) -> None:
        self.table = Table(title=title)
        self.define_header()

    @abstractmethod
    def define_header(self) -> None:
        """テーブルのヘッダーを設定する抽象メソッド。"""
        pass

    @abstractmethod
    def insert_record(self, record: T) -> None:
        """各行を挿入するための抽象メソッド。"""
        pass

    def insert_records(self, records: list[T]) -> None:
        for record in records:
            self.insert_record(record)

    def display(self) -> None:
        """テーブルを表示するメソッド。"""
        ConsoleHandler.console.print(self.table)


class SummaryTableBuilder(TableBuilder[SummaryScoreRecord]):
    """スコア概要を表示するテーブルを構築するクラス。"""

    def __init__(self, title: str, max_relative_score: int):
        self.max_relative_score = max_relative_score

        super().__init__(title)

    def define_header(self) -> None:
        """スコア概要テーブルのヘッダーを定義します。"""
        self.table.add_column("Id", justify="right")
        self.table.add_column("Rank", justify="right")
        self.table.add_column("Submission Time", justify="left")
        self.table.add_column("Total Absolute Score", justify="right")
        self.table.add_column("Total Relative Score", justify="right")

    def insert_record(self, record: SummaryScoreRecord) -> None:
        """スコア概要の各レコードを挿入します。"""
        self.table.add_row(
            str(record.id),
            str(record.relative_rank),
            record.submission_time,
            ScoreFormatter.format_total_absolute_score(record.total_absolute_score, record.invalid_score_count),
            ScoreFormatter.format_relative_score(record.total_relative_score, self.max_relative_score),
        )

    def insert_top_record(self, record: TopSummaryScoreRecord) -> None:
        """トップスコアのレコードを挿入します。"""
        self.table.add_row(
            "Top",
            "Top",
            "Top Score Summary",
            ScoreFormatter.format_total_absolute_score(record.total_absolute_score, record.invalid_score_count),
            ScoreFormatter.format_relative_score(record.total_relative_score, self.max_relative_score),
        )

    def add_separator_row(self) -> None:
        """区切り線をテーブルに追加します。"""
        self.table.add_row("─" * 8, "─" * 8, "─" * 20, "─" * 20, "─" * 20)


class DetailTableBuilder(TableBuilder[DetailScoreRecord]):
    """スコア詳細を表示するテーブルを構築するクラス。"""

    def __init__(
        self, title: str, max_relative_score: int, relative_score_calculator: RelativeScoreCalculaterInterface
    ) -> None:
        self.max_relative_score = max_relative_score
        self.relative_score_calculator = relative_score_calculator

        super().__init__(title)

    def define_header(self) -> None:
        """スコア詳細テーブルのヘッダーを定義します。"""
        self.table.add_column("Test Case", justify="left")
        self.table.add_column("Absolute Score", justify="right")
        self.table.add_column("Score Diff", justify="right")
        self.table.add_column("Relative Score", justify="right")

    def insert_record(self, record: DetailScoreRecord) -> None:
        """スコア詳細の各レコードを挿入します。"""
        relative_score = self.relative_score_calculator(record.absolute_score, record.top_score)

        self.table.add_row(
            ScoreFormatter.format_test_case_input(record.input_test_case),
            ScoreFormatter.format_absolute_score(record.absolute_score),
            ScoreFormatter.format_score_diff(record.absolute_score, record.top_score),
            ScoreFormatter.format_relative_score(relative_score, self.max_relative_score),
        )


class TopDetailTableBuilder(TableBuilder[TopDetailScoreRecord]):
    """トップスコア詳細を表示するテーブルを構築するクラス。"""

    def __init__(self, title: str):
        super().__init__(title)

    def define_header(self) -> None:
        """トップスコア詳細テーブルのヘッダーを定義します。"""
        self.table.add_column("Test Case", justify="left")
        self.table.add_column("Absolute Score", justify="right")
        self.table.add_column("Id", justify="right")

    def insert_record(self, record: TopDetailScoreRecord) -> None:
        """トップスコア詳細の各レコードを挿入します。"""
        self.table.add_row(
            ScoreFormatter.format_test_case_input(record.input_test_case),
            ScoreFormatter.format_absolute_score(record.absolute_score),
            str(record.submittion_id),
        )
