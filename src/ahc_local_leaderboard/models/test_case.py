from typing import Optional


class TestCase:

    def __init__(self, file_name: str, score: Optional[int]) -> None:
        self.file_name = file_name
        self.score = score
