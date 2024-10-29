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

    def __call__(self, testcase_score, top_score):
        return self.calculate_relative_score(testcase_score, top_score)

class MaximizationScoring(RelativeScoreCalculaterInterface):
    def calculate_relative_score(self, testcase_score, top_score):
        if top_score is None:
           return round(pow(10, 9))

        if testcase_score is None:
            return 0
        
        return round(pow(10, 9) * (testcase_score / top_score))
    
    def is_better_score(self, testcase_score, top_score):

        if(top_score is None):
            return True

        if(testcase_score is None):
            return False

        return testcase_score > top_score

class MinimizationScoring(RelativeScoreCalculaterInterface):
    def calculate_relative_score(self, testcase_score, top_score):
        if top_score is None:
           return round(pow(10, 9))

        if testcase_score is None:
            return 0
        
        return round(pow(10, 9) * (top_score / testcase_score))
    
    def is_better_score(self, testcase_score, top_score):

        if(top_score is None):
            return True

        if(testcase_score is None):
            return False

        return testcase_score < top_score

def get_relative_score_calculator(scoring_type):
    if scoring_type == "Maximization":
        return MaximizationScoring()
    elif scoring_type == "Minimization":
        return MinimizationScoring()
    
    raise Exception("Not Found Scoring Type")
