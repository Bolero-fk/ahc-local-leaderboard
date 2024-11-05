from typing import Generic, Optional, TypeVar, Union


class DetailScoreRecord:

    def __init__(self, input_test_case: str, absolute_score: Optional[int], top_score: Optional[int]) -> None:
        self.input_test_case = input_test_case
        self.absolute_score = absolute_score
        self.top_score = top_score


class TopDetailScoreRecord(DetailScoreRecord):

    def __init__(self, input_test_case: str, top_score: Optional[int], id: int) -> None:
        super().__init__(input_test_case, top_score, top_score)
        self.id = id


T = TypeVar("T", bound=DetailScoreRecord)


class DetailScoreRecords(Generic[T]):
    def __init__(self, id: Union[int, str], records: list[T]) -> None:
        self.id = id
        self.records = records
