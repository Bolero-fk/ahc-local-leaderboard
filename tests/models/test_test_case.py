from pathlib import Path
from typing import Optional

import pytest

from ahc_local_leaderboard.models.test_case import TestCase, TestCases


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("score", [None, -1000, -1, 0, 1, 1000])
@pytest.mark.parametrize("file_path", ["out/0001.txt", "$%'-_@{}~`!#()'."])
def test_testcase_initialization(input: str, score: Optional[int], file_path: Path) -> None:
    test_case = TestCase(input, score, file_path)
    assert test_case.file_name == input
    assert test_case.score == score
    assert test_case.submit_file_path == file_path


@pytest.mark.parametrize(
    "scores, sum_score",
    [
        ([1, 10, 100], 111),
        ([0], 0),
        ([None, None, 999, 1], 1000),
    ],
)
def test_calculate_sum_score(scores: list[int], sum_score: int) -> None:
    test_cases = TestCases()
    for score in scores:
        test_cases.add_test_case(TestCase("test", score, Path("path")))

    assert test_cases.calculate_sum_score() == sum_score


def test_contains_test_case() -> None:

    test_cases = TestCases()
    test_cases.add_test_case(TestCase("test", 0, Path("path")))
    test_cases.add_test_case(TestCase("test", None, Path("path")))

    assert test_cases.contains_test_case("test", 0)
    assert test_cases.contains_test_case("test", None)
    assert not test_cases.contains_test_case("test1", 0)
    assert not test_cases.contains_test_case("test", 100)
