from typing import Optional

from ahc_local_leaderboard.models.test_case import TestCase


def check_test_case_attributes(expected_file_name: str, expected_score: Optional[int]) -> None:
    """TestCase インスタンスを生成し、属性が期待通りに設定されているかをチェックする関数"""
    test_case = TestCase(expected_file_name, expected_score)
    assert test_case.file_name == expected_file_name
    assert test_case.score == expected_score


def test_testcase_initialization() -> None:
    # スコアが設定された場合のインスタンス生成
    check_test_case_attributes("sample.txt", 100)

    # スコアが None の場合のインスタンス生成と属性確認
    check_test_case_attributes("sample.txt", None)
