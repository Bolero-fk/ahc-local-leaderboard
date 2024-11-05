import os

from ahc_local_leaderboard.database.database_manager import ScoreHistoryRepository

class Validator:
    REQUIRED_DIRECTORIES = ['leader_board', 'leader_board/top']
    REQUIRED_FILES = ['leader_board/leader_board.db', 'leader_board/config.yaml']

    @staticmethod
    def validate_file_structure():
        """ディレクトリとファイルの構造を検証し、問題があれば False を返す"""
        dirs_ok = Validator._check_directories()
        files_ok = Validator._check_files()
        
        return dirs_ok and files_ok
    
    @staticmethod
    def _check_directories():
        missing_dirs = [d for d in Validator.REQUIRED_DIRECTORIES if not os.path.isdir(d)]
        if missing_dirs:
            print(f"Missing directories: {', '.join(missing_dirs)}")
            return False
        return True

    @staticmethod
    def _check_files():
        missing_files = [f for f in Validator.REQUIRED_FILES if not os.path.isfile(f)]
        if missing_files:
            print(f"Missing files: {', '.join(missing_files)}")
            return False
        return True

    @staticmethod
    def validate_id_exists(id):
        """指定されたscore_history_idがscore_historyテーブルに存在するか確認"""
        return ScoreHistoryRepository.exists_id(id)
