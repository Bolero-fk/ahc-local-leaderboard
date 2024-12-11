import argparse
from abc import ABC, abstractmethod
from pathlib import Path

from ahc_local_leaderboard.consts import (
    get_config_path,
    get_database_path,
    get_leader_board_path,
    get_root_dir,
    get_top_dir,
)
from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.models.test_file import TestFiles
from ahc_local_leaderboard.utils.console_handler import ConsoleHandler


class CommandValidatorBase(ABC):
    """すべてのコマンドバリデータの基底クラス。共通のバリデーションロジックを提供します。"""

    def __init__(self) -> None:
        self.errors: list[str] = []

    @abstractmethod
    def validate(self, args: argparse.Namespace) -> bool:
        """サブクラスで実装する抽象メソッド。コマンド固有のバリデーション処理を定義します。"""
        pass

    def print_errors(self) -> None:
        """エラーメッセージをコンソールに出力します。"""
        for error in self.errors:
            ConsoleHandler.print_error(error)

    def check_directories(self, dirctory_paths: list[Path]) -> bool:
        """指定されたディレクトリが存在するかを確認します。存在しないディレクトリがあればエラーリストに追加します。"""
        missing_dirs = [str(d.relative_to(get_root_dir())) for d in dirctory_paths if not d.exists()]
        if missing_dirs:
            self.errors.append(f"Missing directories: {', '.join(missing_dirs)}")
            return False
        return True

    def check_files(self, file_paths: list[Path]) -> bool:
        """指定されたファイルが存在するかを確認します。 存在しないファイルがあればエラーリストに追加します。"""
        missing_files = [str(f.relative_to(get_root_dir())) for f in file_paths if not f.exists()]
        if missing_files:
            self.errors.append(f"Missing files: {', '.join(missing_files)}")
            return False
        return True

    def is_valid(self) -> bool:
        """エラーがないかどうかを確認します。エラーがない場合に True を返します。"""
        return len(self.errors) == 0


class InitValidator(CommandValidatorBase):
    """各コマンドの実行前用のバリデータクラス。"""

    def __init__(self) -> None:
        super().__init__()

    def validate(self, args: argparse.Namespace) -> bool:
        """必須のディレクトリとファイルが存在するかを確認します。"""
        required_derectories = [get_leader_board_path(), get_top_dir()]
        self.check_directories(required_derectories)

        required_files = [get_database_path(), get_config_path()]
        self.check_files(required_files)

        return self.is_valid()


class SubmitValidator(CommandValidatorBase):
    """'submit' コマンド用のバリデータクラス。"""

    def __init__(self, test_files: TestFiles) -> None:
        self.test_files = test_files
        super().__init__()

    def validate(self, args: argparse.Namespace) -> bool:
        """'submit' コマンド用のバリデーション処理。入力ディレクトリと提出ディレクトリの存在、および必要なファイルが揃っているかを確認します。"""

        assert args.command == "submit"

        required_derectories = [self.test_files.input_dir_path, self.test_files.submit_dir_path]
        if not self.check_directories(required_derectories):
            return False

        test_file_names = self.test_files.fetch_file_names_from_directory()
        required_files = [self.test_files.submit_dir_path / test_file_name for test_file_name in test_file_names]
        self.check_files(required_files)

        return self.is_valid()


class ViewValidator(CommandValidatorBase):
    """'view' コマンド用のバリデータクラス。"""

    def __init__(self, record_read_service: RecordReadService) -> None:
        self.record_read_service = record_read_service
        super().__init__()

    def validate(self, args: argparse.Namespace) -> bool:
        """'view' コマンド用のバリデーション処理。オプションの詳細設定が正しいか、および ID が存在するかを確認します。"""

        assert args.command == "view"

        if args.detail:
            if not self.check_command_option(args.detail):
                return False

            if args.detail.isdigit():
                self.check_id_exists(int(args.detail))
                self.check_sort_column_option_of_detail_records(args.sort_column)
            elif args.detail == "latest":
                self.check_latest_exists()
                self.check_sort_column_option_of_detail_records(args.sort_column)
        else:
            self.check_sort_column_option_of_summary_records(args.sort_column)

        return self.is_valid()

    def check_latest_exists(self) -> bool:
        """提出記録が一つでも存在するかを確認します。存在しない場合、エラーメッセージを追加します。"""
        if self.record_read_service.fetch_total_record_count() == 0:
            self.errors.append("No records found in the database")
            return False
        return True

    def check_id_exists(self, id: int) -> bool:
        """指定された submission_id がデータベースに存在するかを確認します。存在しない場合、エラーメッセージを追加します。"""
        if not self.record_read_service.exists_id(id):
            self.errors.append(f"Record not found in the database: id = {id}")
            return False
        return True

    def check_command_option(self, option: str) -> bool:
        """'view --detail' オプションの妥当性を確認します。 許可された値（数字、'latest'、'top'）以外の場合にエラーリストに追加します。"""
        if not option.isdigit() and option != "latest" and not option == "top":
            self.errors.append(f"Invalid argument for 'view --detail' option: {option}")
            return False

        return True

    def check_sort_column_option_of_summary_records(self, column: str) -> bool:
        """概略情報を表示する際の'view --sort-column' オプションの妥当性を確認します。"""
        if column not in ["id", "rank", "time", "abs", "rel"]:
            self.errors.append(f"Invalid argument for 'view --sort-column' option: {column}")
            return False

        return True

    def check_sort_column_option_of_detail_records(self, column: str) -> bool:
        """詳細情報を表示する際の'view --sort-column' オプションの妥当性を確認します。"""
        if column not in ["id", "abs", "rel"]:
            self.errors.append(f"Invalid argument for 'view --sort-column' option: {column}")
            return False

        return True
