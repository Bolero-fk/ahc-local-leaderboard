from abc import ABC, abstractmethod
from rich.table import Table
from rich.console import Console

from view.score_formatter import ScoreFormatter

class TableBuilder(ABC):
    def __init__(self, title):
        self.table = Table(title=title)
        self.console = Console()
        self.define_header()

    @abstractmethod
    def define_header(self):
        """テーブルのヘッダーを設定する抽象メソッド"""
        pass

    @abstractmethod
    def insert_record(self, *args):
        """各行を挿入するための抽象メソッド"""
        pass

    def display(self):
        """テーブルを表示するメソッド"""
        self.console.print(self.table)


class SummaryTableBuilder(TableBuilder):
    def __init__(self, title, max_relative_score):
        self.max_relative_score = max_relative_score

        super().__init__(title)

    def define_header(self):
        self.table.add_column("Id", justify="right")
        self.table.add_column("Rank", justify="right")
        self.table.add_column("Submission Time", justify="left")
        self.table.add_column("Total Absolute Score", justify="right")
        self.table.add_column("Total Relative Score", justify="right")

    def insert_record(self, record):
        self.table.add_row(
            str(record.id),
            str(record.relative_rank),
            record.submission_time,
            ScoreFormatter.format_total_absolute_score(record.total_absolute_score, record.invalid_score_count),
            ScoreFormatter.format_relative_score(record.total_relative_score, self.max_relative_score)
        )

    def add_separator_row(self):
        """区切り線をテーブルに追加する"""
        self.table.add_row("─" * 8, "─" * 8, "─" * 20, "─" * 20, "─" * 20)

class DetailTableBuilder(TableBuilder):
    def __init__(self, title, max_relative_score, relative_score_calculator):
        self.max_relative_score = max_relative_score
        self.relative_score_calculator = relative_score_calculator

        super().__init__(title)

    def define_header(self):
        self.table.add_column("Test Case", justify="left")
        self.table.add_column("Absolute Score", justify="right")
        self.table.add_column("Score Diff", justify="right")
        self.table.add_column("Relative Score", justify="right")

    def insert_record(self, record):
        relative_score = self.relative_score_calculator(record.absolute_score, record.top_score)

        self.table.add_row(
            ScoreFormatter.format_test_case_input(record.input_test_case),
            ScoreFormatter.format_absolute_score(record.absolute_score),
            ScoreFormatter.format_score_diff(record.absolute_score, record.top_score) ,
            ScoreFormatter.format_relative_score(relative_score, self.max_relative_score)
        )

class TopDetailTableBuilder(TableBuilder):
    def __init__(self, title):
        super().__init__(title)

    def define_header(self):
        self.table.add_column("Test Case", justify="left")
        self.table.add_column("Absolute Score", justify="right")
        self.table.add_column("Id", justify="right")

    def insert_record(self, record):
        self.table.add_row(
            ScoreFormatter.format_test_case_input(record.input_test_case),
            ScoreFormatter.format_absolute_score(record.absolute_score),
            str(record.id)
        )
