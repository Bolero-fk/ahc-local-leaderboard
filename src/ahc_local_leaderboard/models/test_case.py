from typing import Iterator, Optional


class TestCase:
    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(self, file_name: str, score: Optional[int]) -> None:
        self.file_name = file_name
        self.score = score


class TestCases:
    __test__ = False  # pytest によるテスト収集を無効化

    test_cases: list[TestCase] = []

    def __init__(self) -> None:
        self.test_case_count = 0

    def add_test_case(self, test_case: TestCase) -> None:
        self.test_cases.append(test_case)
        self.test_case_count += 1

    def __iter__(self) -> Iterator[TestCase]:
        return iter(self.test_cases)
