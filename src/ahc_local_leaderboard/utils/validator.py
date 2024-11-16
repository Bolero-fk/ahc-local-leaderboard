import os
from pathlib import Path

from ahc_local_leaderboard.consts import (
    get_config_path,
    get_database_path,
    get_leader_board_path,
    get_top_dir,
)
from ahc_local_leaderboard.database.database_manager import ScoreHistoryRepository
from ahc_local_leaderboard.utils.console_handler import ConsoleHandler


class Validator:

    @staticmethod
    def validate_file_structure() -> bool:
        """ディレクトリとファイルの構造を検証し、問題があれば False を返す"""

        required_derectories = [get_leader_board_path(), get_top_dir()]
        required_files = [get_database_path(), get_config_path()]

        dirs_ok = Validator.check_directories(required_derectories)
        files_ok = Validator.check_files(required_files)

        return dirs_ok and files_ok

    @staticmethod
    def check_directory(dirctory_path: Path) -> bool:
        if not os.path.isdir(dirctory_path):
            ConsoleHandler.print_error(f"Missing directory: {dirctory_path}")
            return False
        return True

    @staticmethod
    def check_directories(dirctory_paths: list[Path]) -> bool:
        missing_dirs = [d for d in dirctory_paths if not os.path.isdir(d)]
        if missing_dirs:
            ConsoleHandler.print_error(f"Missing directories: {', '.join(str( missing_dirs))}")
            return False
        return True

    @staticmethod
    def check_file(file_path: Path) -> bool:
        if not os.path.isfile(file_path):
            ConsoleHandler.print_error(f"Missing file: {file_path}")
            return False
        return True

    @staticmethod
    def check_files(file_paths: list[Path]) -> bool:
        missing_files = [f for f in file_paths if not os.path.isfile(f)]
        if missing_files:
            ConsoleHandler.print_error(f"Missing files: {', '.join(str(missing_files))}")
            return False
        return True

    @staticmethod
    def validate_id_exists(id: int) -> bool:
        """指定されたscore_history_idがscore_historyテーブルに存在するか確認"""
        return ScoreHistoryRepository().exists_id(id)
