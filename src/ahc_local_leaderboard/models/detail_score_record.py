from typing import Generic, Optional, TypeVar, Union

from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class DetailScoreRecord:
    """個々のテストケースのスコア情報を管理するクラス。"""

    def __init__(self, file_name: str, absolute_score: Optional[int], top_score: Optional[int]) -> None:
        self.file_name = file_name
        self.absolute_score = absolute_score
        self.top_score = top_score

    def calculate_relative_score(self, relative_calculator: RelativeScoreCalculaterInterface) -> int:
        """相対スコアを計算して返します。"""
        return relative_calculator(self.absolute_score, self.top_score)

    def get_absolute_score(self) -> int:
        """絶対スコアを取得します（Noneの場合は0を返します）。"""
        return self.absolute_score if self.absolute_score is not None else 0

    @classmethod
    def from_row(cls, row: tuple[str, Optional[int], Optional[int]]) -> "DetailScoreRecord":
        """データベースの行情報からインスタンスを生成します。"""
        return cls(*row)


class TopDetailScoreRecord(DetailScoreRecord):
    """トップスコアの詳細情報を管理するクラス。"""

    def __init__(self, file_name: str, top_score: Optional[int], submittion_id: int) -> None:
        assert 0 < submittion_id
        super().__init__(file_name, top_score, top_score)
        self.submittion_id = submittion_id


T = TypeVar("T", bound=DetailScoreRecord)


class DetailScoreRecords(Generic[T]):
    """複数のスコアレコードを管理し、統計情報を計算するクラス。"""

    def __init__(self, id: Union[int, str], records: list[T]) -> None:
        if isinstance(id, int):
            assert 0 < id
        elif isinstance(id, str):
            assert id == "Top"

        self.id = id
        self.records = records

    def sort_records_by_input_file_name(self) -> None:
        """入力ファイル名でレコードをソートします。"""
        self.records.sort(key=lambda record: record.file_name)

    def calculate_total_absolute_score(self) -> int:
        """絶対スコアの合計を計算して返します。"""
        return sum(record.get_absolute_score() for record in self.records)

    def calculate_invalid_score_count(self) -> int:
        """無効なスコアのレコード数をカウントして返します。"""
        return sum(1 for record in self.records if record.absolute_score is None)

    def calculate_total_relative_score(self, relative_calculator: RelativeScoreCalculaterInterface) -> int:
        """相対スコアの合計を計算して返します。"""
        return sum(record.calculate_relative_score(relative_calculator) for record in self.records)
