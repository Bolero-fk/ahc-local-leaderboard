class TestCase:
    """テストケースを管理するクラス"""
    def __init__(self, file_name, score):
        self.file_name = file_name
        self.score = score

    def __repr__(self):
        return f"TestCaseScore(file_name='{self.file_name}', score={self.score})"