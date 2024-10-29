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

    @staticmethod
    def reserve_score_history_table(submission_time):
        """スコア履歴テーブルに空の行を挿入し、そのIDを取得する"""

        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO score_history (submission_time)
                VALUES (?)
            ''', (submission_time,))

        return cursor.lastrowid 

    @staticmethod
    def update_score_history_table(record):
        """スコア履歴テーブルを更新する"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()

            # スコア履歴テーブルに絶対スコアと相対スコアを更新
            cursor.execute('''
                UPDATE score_history
                SET total_absolute_score = ?, total_relative_score = ?, invalid_score_count = ?, relative_rank = ?
                WHERE id = ?
            ''', (record.total_absolute_score, record.total_relative_score, record.invalid_score_count, record.relative_rank, record.id))

    @staticmethod
    def insert_test_case(test_case, score_history_id):
        """テストケーステーブルにテストケースを挿入する"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO test_cases (test_case_input, absolute_score, score_history_id)
                VALUES (?, ?, ?)
            ''', (test_case.file_name, test_case.score, score_history_id))

    @staticmethod
    def update_top_score(test_case, score_history_id):
        """トップスコアテーブルを更新する"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (test_case.file_name,))
            result = cursor.fetchone()

            if result is not None:
                second_top_score = result[0]
            else:
                second_top_score = None

            cursor.execute('''
                INSERT OR REPLACE INTO top_scores (test_case_input, top_absolute_score, second_top_score, is_updated, score_history_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (test_case.file_name, test_case.score, second_top_score, True, score_history_id))

    @staticmethod
    def fetch_top_score(test_case):
        """トップスコアを取得する"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (test_case.file_name,))
            result = cursor.fetchone()
            return result[0] if result is not None else None

    @staticmethod
    def fetch_latest_id():
        """最新の提出のidを取得する"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM score_history ORDER BY submission_time DESC LIMIT 1')
            result = cursor.fetchone()
            return result[0] if result is not None else None
