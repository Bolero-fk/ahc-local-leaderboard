import sqlite3

class DatabaseManager:
    """データベース接続を管理するクラス"""

    _DB_PATH = 'leader_board/leader_board.db'

    def __init__(self):
        self.connection = False

    def __enter__(self):
        """with 文の開始時にデータベースに接続"""
        self.connection = sqlite3.connect(self._DB_PATH)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """with 文の終了時にデータベース接続を閉じる"""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = True
