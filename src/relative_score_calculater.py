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

class MaximizationScoring(RelativeScoreCalculaterInterface):
    def calculate_relative_score(self, testcase_score, top_score):
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

class MinimizationScoring(RelativeScoreCalculaterInterface):
    def calculate_relative_score(self, testcase_score, top_score):
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

def get_relative_score_calculator(scoring_type):
    if scoring_type == "Maximization":
        return MaximizationScoring()
    elif scoring_type == "Minimization":
        return MinimizationScoring()
    
    raise Exception("Not Found Scoring Type")
