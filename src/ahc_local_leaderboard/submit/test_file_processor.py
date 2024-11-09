import subprocess
from abc import ABC, abstractmethod
from typing import Optional

from rich.progress import track

from ahc_local_leaderboard.models.test_case import TestCase, TestCases
from ahc_local_leaderboard.models.test_file import TestFile, TestFiles


class TestFileProcessorInterface(ABC):
    __test__ = False  # pytest によるテスト収集を無効化

    @abstractmethod
    def process_test_file(self, test_file: TestFile) -> Optional[int]:
        """単一のテストファイルのスコアを計算し、成功した場合はスコアを返す"""
        pass


class AtCoderTestFileProcessor(TestFileProcessorInterface):
    def validate_output_format(self, decoded_output: str) -> None:
        """標準出力が期待するフォーマットか検証する"""
        if len(decoded_output.split("\n")) != 2:
            raise ValueError("入力されたテストファイルでAHCツールを実行するとエラーを返しています")

    def parse_stdout(self, decoded_output: str) -> int:
        """標準出力からスコアを取り出す"""
        try:
            score_str = decoded_output.split(" ")[-1].strip()
            return int(score_str)
        except (IndexError, ValueError):
            raise ValueError("スコアを標準出力から抽出できませんでした。")

    def process_test_file(self, test_file: TestFile) -> Optional[int]:
        """AHCで配布されるツールを使ってスコアを計算し、成功した場合はスコアを返す"""
        try:
            with open(test_file.input_file_path) as fin, open(test_file.submit_file_path) as fout:
                score_process = subprocess.run(
                    ["cargo", "run", "-r", "--bin", "vis", fin.name, fout.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )

                decoded_output = score_process.stdout.decode("utf-8")
                self.validate_output_format(decoded_output)
                return self.parse_stdout(decoded_output)
        except Exception:
            return None


class TestFilesProcessor:
    __test__ = False  # pytest によるテスト収集を無効化

    LOADING_TEXT = "Test Case Processing..."

    def __init__(self, test_files: TestFiles, test_file_processor: TestFileProcessorInterface) -> None:
        self.test_files = test_files
        self.test_file_processor = test_file_processor

    def process_test_files(self) -> TestCases:
        """全てのテストファイルのスコアを計算する"""

        test_cases = TestCases()
        self.test_files.add_all_files()

        for test_file in track(self.test_files, description=self.LOADING_TEXT, total=self.test_files.file_count):
            score = self.test_file_processor.process_test_file(test_file)
            test_cases.add_test_case(TestCase(test_file.file_name, score))

        return test_cases
