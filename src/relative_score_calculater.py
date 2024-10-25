from abc import ABC, abstractmethod

class RelativeScoreCalculaterInterface(ABC):
    @abstractmethod
    def calculate_relative_score(self, testcase_score, top_score):
        """相対スコアを計算する"""
        pass

    @abstractmethod
    def is_better_score(self, testcase_score, top_score):
        """スコアの優劣を判断する"""
        pass

    @abstractmethod
    def get_provisional_score(self):
        """絶対スコアが None のときの暫定スコアを返す"""
        pass

class MinimizationScoring(RelativeScoreCalculaterInterface):
    def calculate_relative_score(self, top_score, testcase_score):
        if testcase_score is None:
            return 0
        
        return round(pow(10, 9) * (top_score / testcase_score))
    
    def is_better_score(self, testcase_score, top_score):

        if(top_score is None):
            return True

        if(testcase_score is None):
            return False

        return testcase_score < top_score

    def get_provisional_score(self):
        return round(pow(10, 9))

class MaximizationScoring(RelativeScoreCalculaterInterface):
    def calculate_relative_score(self, top_score, testcase_score):
        if testcase_score is None:
            return 0
        
        return round(pow(10, 9) * (testcase_score / top_score))
    
    def is_better_score(self, testcase_score, top_score):

        if(top_score is None):
            return True

        if(testcase_score is None):
            return False

        return testcase_score > top_score

    def get_provisional_score(self):
        return 0