from typing import Optional

import pytest

from ahc_local_leaderboard.models.test_case import TestCase


@pytest.mark.parametrize("input", ["test1", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("score", [None, -1000, -1, 0, 1, 1000])
@pytest.mark.parametrize("file_path", ["out/0001.txt", "$%'-_@{}~`!#()'."])
def test_testcase_initialization(input: str, score: Optional[int], file_path: str) -> None:
    test_case = TestCase(input, score, file_path)
    assert test_case.file_name == input
    assert test_case.score == score
    assert test_case.submit_file_path == file_path
