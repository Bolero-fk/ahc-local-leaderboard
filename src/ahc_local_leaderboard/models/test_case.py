from typing import Optional


class TestCase:
    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(self, file_name: str, score: Optional[int]) -> None:
        self.file_name = file_name
        self.score = score
