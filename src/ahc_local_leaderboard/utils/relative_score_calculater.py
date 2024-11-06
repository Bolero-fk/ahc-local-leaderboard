from abc import ABC, abstractmethod
from typing import Optional

from ahc_local_leaderboard.utils.validator import Validator


class RelativeScoreCalculaterInterface(ABC):

    @abstractmethod
    def score_ratio(self, testcase_score: int, top_score: int) -> float:
        """スコアの比率を計算します"""
        pass

    @abstractmethod
    def compare_scores(self, testcase_score: int, top_score: int) -> bool:
        """スコアの比較を計算します"""
        pass

    def calculate_relative_score(self, testcase_score: Optional[int], top_score: Optional[int]) -> int:
        """相対スコアを計算します"""
        if top_score is None:
            return round(pow(10, 9))
        if testcase_score is None:
            return 0
        return round(pow(10, 9) * self.score_ratio(testcase_score, top_score))

    def is_better_score(self, testcase_score: Optional[int], top_score: Optional[int]) -> bool:
        """スコアの優劣を判断します"""
        if top_score is None:
            return True

        if testcase_score is None:
            return False

        return self.compare_scores(testcase_score, top_score)

    def __call__(self, testcase_score: Optional[int], top_score: Optional[int]) -> int:
        return self.calculate_relative_score(testcase_score, top_score)


class MaximizationScoring(RelativeScoreCalculaterInterface):

    def score_ratio(self, testcase_score: int, top_score: int) -> float:
        return testcase_score / top_score

    def compare_scores(self, testcase_score: int, top_score: int) -> bool:
        return testcase_score > top_score


class MinimizationScoring(RelativeScoreCalculaterInterface):

    def score_ratio(self, testcase_score: int, top_score: int) -> float:
        return top_score / testcase_score

    def compare_scores(self, testcase_score: int, top_score: int) -> bool:
        return testcase_score < top_score


def get_relative_score_calculator(scoring_type: str) -> RelativeScoreCalculaterInterface:

    if Validator.validate_scoring_type(scoring_type):
        return MaximizationScoring() if scoring_type == "Maximization" else MinimizationScoring()

    raise ValueError(f"Not Found Scoring Type: {scoring_type}")
