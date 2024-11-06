import os
import shutil

from ahc_local_leaderboard.models.test_case import TestCase
from ahc_local_leaderboard.utils.validator import Validator


class FiliUtility:

    @staticmethod
    def path_exists(path: str) -> bool:
        """指定されたパスが存在するかを確認します"""
        return os.path.exists(path)

    @staticmethod
    def try_create_directory(directory_path: str) -> None:
        """指定されたディレクトリが存在しない場合のみディレクトリを作成します"""
        os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    def copy_submit_file_to_leaderboard(submit_path: str, test_case: TestCase) -> None:
        """入力された提出ファイルを順位表ディレクトリにコピーします"""

        submit_file = f"{submit_path}/{test_case.file_name}"
        if not Validator.check_file(submit_file):
            raise FileNotFoundError(f"Submit file '{submit_file}' does not exist and could not be validated.")

        dest_dir = "leader_board/top"
        if not Validator.check_directory(dest_dir):
            raise FileNotFoundError(f"Destination directory '{dest_dir}' does not exist and could not be validated.")

        dest_file = f"{dest_dir}/{test_case.file_name}"
        try:
            shutil.copy(submit_file, dest_file)
        except Exception as e:
            raise IOError(f"Failed to copy file from '{submit_file}' to '{dest_file}': {e}")
