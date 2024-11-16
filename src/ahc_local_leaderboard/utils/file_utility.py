import os
import shutil
from pathlib import Path

from ahc_local_leaderboard.consts import get_top_dir
from ahc_local_leaderboard.models.test_case import TestCase


class FileUtility:

    @staticmethod
    def path_exists(path: Path) -> bool:
        """指定されたパスが存在するかを確認します"""
        return os.path.exists(path)

    @staticmethod
    def try_create_directory(directory_path: Path) -> None:
        """指定されたディレクトリが存在しない場合のみディレクトリを作成します"""
        os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    def copy_file(src: Path, dest: Path) -> None:
        """指定されたファイルをコピーします"""
        try:
            shutil.copy(src, dest)
        except Exception as e:
            raise IOError(f"Failed to copy file from '{src}' to '{dest}': {e}")

    @staticmethod
    def copy_submit_file_to_leaderboard(test_case: TestCase) -> None:
        """入力された提出ファイルを順位表ディレクトリにコピーします"""
        submit_file_path = test_case.submit_file_path
        top_file_path = get_top_dir() / test_case.file_name
        FileUtility.copy_file(submit_file_path, top_file_path)
