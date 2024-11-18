import re
import subprocess
from abc import ABC, abstractmethod
from typing import Optional

from rich.progress import track

from ahc_local_leaderboard.models.test_case import TestCase, TestCases
from ahc_local_leaderboard.models.test_file import TestFile, TestFiles


class TestFileProcessorInterface(ABC):
    """テストファイルを処理してスコアを計算するためのインターフェース。"""

    __test__ = False  # pytest によるテスト収集を無効化

    @abstractmethod
    def process_test_file(self, test_file: TestFile) -> Optional[int]:
        """単一のテストファイルのスコアを計算し、成功した場合はスコアを返します。"""
        pass


class AtCoderTestFileProcessor(TestFileProcessorInterface):
    """AtCoderのツールを使用してテストファイルを処理し、スコアを計算するクラス。"""

    def parse_stdout(self, decoded_output: str) -> Optional[int]:
        """標準出力からスコアを取り出します。"""
        match = re.search(r"Score = (\d+)", decoded_output)
        if match:
            score = int(match.group(1))
            if 0 < score:
                return score
            else:
                return None
        else:
            return None

    def process_test_file(self, test_file: TestFile) -> Optional[int]:
        """AHCで配布されるツールを使ってスコアを計算し、成功した場合はスコアを返します。"""
        try:
            with open(test_file.input_file_path) as fin, open(test_file.submit_file_path) as fout:
                score_process = subprocess.run(
                    ["cargo", "run", "-r", "--bin", "vis", fin.name, fout.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )

                decoded_output = score_process.stdout.decode("utf-8")

                return self.parse_stdout(decoded_output)
        except Exception:
            return None


class TestFilesProcessor:
    """複数のテストファイルを処理して、それらに対応するテストケースを生成するクラス。"""

    __test__ = False  # pytest によるテスト収集を無効化

    LOADING_TEXT = "Test Case Processing..."

    def __init__(self, test_file_processor: TestFileProcessorInterface) -> None:
        self.test_file_processor = test_file_processor

    def process_test_files(self, test_files: TestFiles) -> TestCases:
        """全てのテストファイルのスコアを計算します。"""

        self.test_files = test_files

        test_cases = TestCases()
        self.test_files.add_all_files()

        for test_file in track(self.test_files, description=self.LOADING_TEXT, total=self.test_files.file_count):
            score = self.test_file_processor.process_test_file(test_file)
            test_cases.add_test_case(TestCase(test_file.file_name, score, test_file.submit_file_path))

        return test_cases
