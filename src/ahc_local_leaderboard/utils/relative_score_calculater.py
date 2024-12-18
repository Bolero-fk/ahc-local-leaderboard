from abc import ABC, abstractmethod
from typing import Optional


class RelativeScoreCalculaterInterface(ABC):
    """相対スコア計算のためのインターフェースクラス。"""

    MIN_SCORE = 0
    MAX_SCORE = round(pow(10, 9))

    @abstractmethod
    def score_ratio(self, a: int, b: int) -> float:
        """スコアの比率を計算します。"""
        pass

    @abstractmethod
    def compare_scores(self, a: int, b: int) -> bool:
        """スコアの比較を計算します。"""
        pass

    def calculate_relative_score(self, testcase_score: Optional[int], top_score: Optional[int]) -> int:
        """相対スコアを計算します。"""
        if top_score is None:
            return self.MAX_SCORE
        if testcase_score is None:
            return self.MIN_SCORE

        assert 0 < testcase_score and 0 < top_score
        assert testcase_score == top_score or self.is_better_score(top_score, testcase_score)

        return round(self.MAX_SCORE * self.score_ratio(testcase_score, top_score))

    def calculate_diff_relative_score(
        self, testcase_score: Optional[int], top_score: Optional[int], pre_top_score: Optional[int]
    ) -> int:
        """top_score 更新による相対スコアの差分を計算します。"""

        return self.calculate_relative_score(testcase_score, top_score) - self.calculate_relative_score(
            testcase_score, pre_top_score
        )

    def is_better_score(self, a: Optional[int], b: Optional[int]) -> bool:
        """スコアaがスコアbより優れているかを判断します。"""
        if b is None:
            return True

        if a is None:
            return False

        return self.compare_scores(a, b)

    def __call__(self, testcase_score: Optional[int], top_score: Optional[int]) -> int:
        return self.calculate_relative_score(testcase_score, top_score)


class MaximizationScoring(RelativeScoreCalculaterInterface):
    """スコアが大きいほど優れている場合の相対スコア計算クラス。"""

    def score_ratio(self, a: int, b: int) -> float:
        """スコアの比率を計算します（a/b）。"""
        return a / b

    def compare_scores(self, a: int, b: int) -> bool:
        """スコアaがスコアbより大きいかどうかを判定します。"""
        return a > b


class MinimizationScoring(RelativeScoreCalculaterInterface):
    """スコアが小さいほど優れている場合の相対スコア計算クラス。"""

    def score_ratio(self, a: int, b: int) -> float:
        """スコアの比率を計算します（b/a）。"""
        return b / a

    def compare_scores(self, a: int, b: int) -> bool:
        """スコアaがスコアbより小さいかどうかを判定します。"""
        return a < b


def get_relative_score_calculator(scoring_type: str) -> RelativeScoreCalculaterInterface:
    """指定されたスコアリングタイプに対応する計算クラスを返します。"""
    assert scoring_type in ["Maximization", "Minimization"]
    return MaximizationScoring() if scoring_type == "Maximization" else MinimizationScoring()
