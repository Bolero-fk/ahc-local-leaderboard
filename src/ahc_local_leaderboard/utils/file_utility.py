import os
import shutil

from ahc_local_leaderboard.consts import get_top_dir
from ahc_local_leaderboard.models.test_case import TestCase
from ahc_local_leaderboard.utils.validator import Validator


class FileUtility:

    @staticmethod
    def path_exists(path: str) -> bool:
        """指定されたパスが存在するかを確認します"""
        return os.path.exists(path)

    @staticmethod
    def try_create_directory(directory_path: str) -> None:
        """指定されたディレクトリが存在しない場合のみディレクトリを作成します"""
        os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    def copy_file(src: str, dest: str) -> None:
        """指定されたファイルをコピーします"""
        try:
            shutil.copy(src, dest)
        except Exception as e:
            raise IOError(f"Failed to copy file from '{src}' to '{dest}': {e}")

    @staticmethod
    def get_top_file_path(test_case: TestCase) -> str:
        """test_caseで指定されている提出ファイルのトップケースのパスを取得します"""
        top_directory_path = str(get_top_dir())
        if not Validator.check_directory(top_directory_path):
            raise FileNotFoundError(
                f"Destination directory '{top_directory_path}' does not exist and could not be validated."
            )

        top_file_path = f"{top_directory_path}/{test_case.file_name}"

        return top_file_path

    @staticmethod
    def copy_submit_file_to_leaderboard(test_case: TestCase) -> None:
        """入力された提出ファイルを順位表ディレクトリにコピーします"""
        submit_file_path = test_case.submit_file_path
        top_file_path = FileUtility.get_top_file_path(test_case)
        FileUtility.copy_file(submit_file_path, top_file_path)
