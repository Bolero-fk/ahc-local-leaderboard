from pathlib import Path
from typing import Iterator


class TestFile:
    """個々のテストファイルを管理するクラス。"""

    __test__ = False  # pytest によるテスト収集を無効化

    # TODO ファイルの存在チェックのバリデーション
    def __init__(self, file_name: str, input_file_path: Path, submit_file_path: Path) -> None:
        self.file_name = file_name
        self.input_file_path = input_file_path
        self.submit_file_path = submit_file_path


class TestFiles:
    """複数のテストファイルを管理するクラス。"""

    __test__ = False  # pytest によるテスト収集を無効化

    def __init__(self, input_dir_path: Path, submit_dir_path: Path) -> None:
        self.input_dir_path = input_dir_path
        self.submit_dir_path = submit_dir_path
        self.file_count = 0
        self.test_files: list[TestFile] = []

    def fetch_file_names_from_directory(self) -> list[str]:
        """入力ディレクトリ内のすべてのファイル名を取得します。"""
        return [file.name for file in self.input_dir_path.iterdir() if file.is_file()]

    def add_all_files(self) -> None:
        """入力ディレクトリ内のすべてのファイルをTestFileとして追加します。"""
        assert self.file_count == 0  # 呼び出すのは一回だけ

        test_file_names = self.fetch_file_names_from_directory()
        test_file_names.sort()
        for test_file_name in test_file_names:
            self.add_file(test_file_name)

    # TODO ファイル重複チェックのvalidation
    def add_file(self, file_name: str) -> None:
        """指定されたファイルをTestFileオブジェクトとして追加します。"""

        input_file_path = self.input_dir_path / file_name
        submit_file_path = self.submit_dir_path / file_name
        self.test_files.append(TestFile(file_name, input_file_path, submit_file_path))
        self.file_count += 1

    def __iter__(self) -> Iterator[TestFile]:
        return iter(self.test_files)
