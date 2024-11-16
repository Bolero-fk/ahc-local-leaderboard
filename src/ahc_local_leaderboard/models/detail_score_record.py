from typing import Generic, Optional, TypeVar, Union

from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


class DetailScoreRecord:

    # TODO input_test_case はfile nameに統一する
    def __init__(self, input_test_case: str, absolute_score: Optional[int], top_score: Optional[int]) -> None:
        self.input_test_case = input_test_case
        self.absolute_score = absolute_score
        self.top_score = top_score

    def calculate_relative_score(self, relative_calculator: RelativeScoreCalculaterInterface) -> int:
        return relative_calculator(self.absolute_score, self.top_score)

    def get_absolute_score(self) -> int:
        return self.absolute_score if self.absolute_score is not None else 0

    @classmethod
    def from_row(cls, row: tuple[str, Optional[int], Optional[int]]) -> "DetailScoreRecord":
        return cls(*row)


class TopDetailScoreRecord(DetailScoreRecord):

    def __init__(self, input_test_case: str, top_score: Optional[int], submittion_id: int) -> None:
        assert 0 < submittion_id
        super().__init__(input_test_case, top_score, top_score)
        self.submittion_id = submittion_id


T = TypeVar("T", bound=DetailScoreRecord)


class DetailScoreRecords(Generic[T]):
    def __init__(self, id: Union[int, str], records: list[T]) -> None:
        if isinstance(id, int):
            assert 0 < id
        elif isinstance(id, str):
            assert id == "Top"

        self.id = id
        self.records = records

    def sort_records_by_input_file_name(self) -> None:
        self.records.sort(key=lambda record: record.input_test_case)

    def calculate_total_absolute_score(self) -> int:
        return sum(record.get_absolute_score() for record in self.records)

    def calculate_invalid_score_count(self) -> int:
        return sum(1 for record in self.records if record.absolute_score is None)

    def calculate_total_relative_score(self, relative_calculator: RelativeScoreCalculaterInterface) -> int:
        return sum(record.calculate_relative_score(relative_calculator) for record in self.records)
