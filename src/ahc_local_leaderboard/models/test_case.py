from pathlib import Path
from typing import Iterator, Optional


class TestCase:
    """個々のテストケースを管理するクラス。"""

    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(self, file_name: str, score: Optional[int], submit_file_path: Path) -> None:
        self.file_name = file_name
        self.score = score
        self.submit_file_path = submit_file_path


class TestCases:
    """複数のテストケースを管理するクラス。"""

    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(self) -> None:
        self.test_case_count = 0
        self.test_cases: list[TestCase] = []

    def add_test_case(self, test_case: TestCase) -> None:
        """テストケースを追加します。"""
        self.test_cases.append(test_case)
        self.test_case_count += 1

    def calculate_sum_score(self) -> int:
        """テストケースのスコアの総和を返します。スコアがNoneの場合は0として扱います。"""
        return sum(tc.score if tc.score is not None else 0 for tc in self.test_cases)

    def contains_test_case(self, file_name: str, score: Optional[int]) -> bool:
        """指定されたファイル名とスコアを持つテストケースが含まれている場合はTrueを返します。"""
        return any(file_name == tc.file_name and score == tc.score for tc in self.test_cases)

    def __iter__(self) -> Iterator[TestCase]:
        return iter(self.test_cases)
