from typing import Optional

import pytest

from ahc_local_leaderboard.models.test_case import TestCase


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("score", [None, -1000, -1, 0, 1, 1000])
def test_testcase_initialization(input: str, score: Optional[int]) -> None:
    test_case = TestCase(input, score)
    assert test_case.file_name == input
    assert test_case.score == score