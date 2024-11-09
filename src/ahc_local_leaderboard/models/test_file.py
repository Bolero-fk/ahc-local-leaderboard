import os
from typing import Iterator


class TestFile:
    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(self, file_name: str, input_file_path: str, submit_file_path: str) -> None:
        self.file_name = file_name
        self.input_file_path = input_file_path
        self.submit_file_path = submit_file_path


class TestFiles:
    __test__ = False  # pytest によるテスト収集を無効化

    test_files: list[TestFile] = []

    def __init__(self, input_dir_path: str, submit_dir_path: str) -> None:
        self.input_dir_path = input_dir_path
        self.submit_dir_path = submit_dir_path
        self.file_count = 0

    def add_all_files(self) -> None:
        assert self.file_count == 0  # 呼び出すのは一回だけ
        input_file_names = os.listdir(self.input_dir_path)
        input_file_names.sort()
        for input_file_name in input_file_names:
            self.add_file(input_file_name)

    def add_file(self, file_name: str) -> None:
        input_file_path = f"{self.input_dir_path}/{file_name}"
        submit_file_path = f"{self.submit_dir_path}/{file_name}"
        self.test_files.append(TestFile(file_name, input_file_path, submit_file_path))
        self.file_count += 1

    def __iter__(self) -> Iterator[TestFile]:
        return iter(self.test_files)
