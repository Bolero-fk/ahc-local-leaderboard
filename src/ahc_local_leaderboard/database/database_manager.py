import sqlite3
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecords, SummaryScoreRecord
from ahc_local_leaderboard.models.detail_score_record import DetailScoreRecords, DetailScoreRecord, TopDetailScoreRecord

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

class ScoreHistoryRepository:
    
    @staticmethod
    def reserve_score_history(submission_time):
        """スコア履歴テーブルに空行を挿入し、そのIDを返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO score_history (submission_time)
                VALUES (?)
            ''', (submission_time,))
        return cursor.lastrowid    

    @staticmethod
    def update_score_history(record):
        """指定されたスコアレコードの情報でスコア履歴テーブルを更新します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE score_history
                SET total_absolute_score = ?, total_relative_score = ?, invalid_score_count = ?, relative_rank = ?
                WHERE id = ?
            ''', (record.total_absolute_score, record.total_relative_score, record.invalid_score_count, record.relative_rank, record.id))

    @staticmethod
    def fetch_record(id):
        """指定されたIDのスコアレコードを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
                FROM score_history
                WHERE id = ?     
            ''', (id, ))
            row = cursor.fetchone()    
                
        return SummaryScoreRecord(*row)
        
    @staticmethod
    def fetch_non_latest_records():
        """最新エントリ以外のスコア履歴レコードを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
                FROM score_history
                WHERE submission_time < (SELECT MAX(submission_time) FROM score_history)
                ORDER BY submission_time
            ''')
            rows = cursor.fetchall()

        records = [SummaryScoreRecord(*row) for row in rows]
        return SummaryScoreRecords(records)

    @staticmethod
    def fetch_latest_id():
        """最新のスコア履歴IDを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM score_history ORDER BY submission_time DESC LIMIT 1')
            result = cursor.fetchone()
        return result[0] if result is not None else None

    @staticmethod
    def fetch_latest_record():
        """最新のスコア履歴レコードを取得します"""
        latest_id = ScoreHistoryRepository.fetch_latest_id()
        return ScoreHistoryRepository.fetch_record(latest_id)

    @staticmethod
    def fetch_latest_records(limit=10):
        """最新のスコア履歴レコードを指定数分取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
                FROM score_history
                ORDER BY submission_time DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
        
        records = [SummaryScoreRecord(*row) for row in rows]
        return SummaryScoreRecords(records)

    @staticmethod
    def count_higher_score_records(record):
        """指定レコードより高いスコアのレコード数を返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM score_history
                WHERE total_relative_score >= ? and id != ?
            ''', (record.total_relative_score, record.id))
            
            return cursor.fetchone()[0]

    @staticmethod
    def fetch_lower_score_records(record):
        """指定レコードより低いスコアのレコードを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
                FROM score_history
                WHERE total_relative_score < ? and id != ?
            ''', (record.total_relative_score, record.id))
            rows = cursor.fetchall()
        
        records = [SummaryScoreRecord(*row) for row in rows]
        return SummaryScoreRecords(records)

    def exists_id(id):
        """指定されたidがscore_historyテーブルに存在するか確認"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM score_history
                WHERE id = ?
            ''', (id,))
            result = cursor.fetchone()[0]
            
            return result > 0

class TestCaseRepository:
    
    @staticmethod
    def insert_test_case(test_case, score_history_id):
        """テストケース情報をテストケーステーブルに挿入します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO test_cases (test_case_input, absolute_score, score_history_id)
                VALUES (?, ?, ?)
            ''', (test_case.file_name, test_case.score, score_history_id))

    @staticmethod
    def fetch_absolute_score(test_case_input, score_history_id):
        """指定されたtest_case_inputとscore_history_idに対応するabsolute_scoreを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT absolute_score
                FROM test_cases
                WHERE test_case_input = ? AND score_history_id = ?
            ''', (test_case_input, score_history_id))
            result = cursor.fetchone()
        return result[0]

    @staticmethod
    def fetch_records(submission_id):
        """ 指定された提出IDに関連するレコードを取得します"""

        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tc.test_case_input, tc.absolute_score, ts.top_absolute_score
                FROM test_cases AS tc
                LEFT JOIN top_scores AS ts ON tc.test_case_input = ts.test_case_input
                WHERE tc.score_history_id = ?
            ''', (submission_id, ))

            rows = cursor.fetchall()            
        records = [DetailScoreRecord(*row) for row in rows]
        return DetailScoreRecords(submission_id, records)

class TopScoresRepository:
    
    @staticmethod
    def update_top_score(test_case, score_history_id):
        """ 指定されたテストケースのスコアでトップスコアテーブルを更新します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (test_case.file_name,))
            result = cursor.fetchone()
            second_top_score = result[0] if result else None
            cursor.execute('''
                INSERT OR REPLACE INTO top_scores (test_case_input, top_absolute_score, second_top_score, is_updated, score_history_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (test_case.file_name, test_case.score, second_top_score, True, score_history_id))

    @staticmethod
    def fetch_top_score(test_case):
        """指定されたテストケースのトップスコアを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (test_case.file_name,))
            result = cursor.fetchone()
        return result[0] if result else None

    @staticmethod
    def reset_is_updated_flags():
        """top_scoresテーブルのis_updatedフラグをすべてFALSEにリセットします"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE top_scores
                SET is_updated = FALSE
                WHERE is_updated = TRUE
            ''')

    @staticmethod
    def fetch_test_case_count():
        """登録されているテストケースの総数を取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM top_scores')
            result = cursor.fetchone()
        return result[0]

    @staticmethod
    def fetch_updated_top_scores():
        """is_updatedがTRUEであるテストケースのトップスコアおよびセミトップスコアを取得します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_case_input, top_absolute_score, second_top_score
                FROM top_scores
                WHERE is_updated = TRUE
            ''')

            return cursor.fetchall()

    @staticmethod
    def fetch_top_summary_record():
        """top_scoresテーブルからトップスコアのサマリー情報を生成し、返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COALESCE(SUM(top_absolute_score), 0) AS total_absolute_score,
                       COUNT(*) AS total_cases,
                       COUNT(*) - COUNT(top_absolute_score) AS invalid_score_count
                FROM top_scores
            ''')
            total_absolute_score, total_cases, invalid_score_count = cursor.fetchone()
        
        # Total Relative Score は全テストケースが最大スコアを取った場合を仮定
        total_relative_score = 10**9 * total_cases
        return SummaryScoreRecord("Top", "Top Score Summary", total_absolute_score, total_relative_score, invalid_score_count, "Top")

    @staticmethod
    def fetch_top_detail_records():
        """top_scoresテーブルからトップスコアの詳細情報を生成し、返します"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_case_input, top_absolute_score, score_history_id
                FROM top_scores
            ''')
            rows = cursor.fetchall()
        records = [TopDetailScoreRecord(*row) for row in rows]
        return DetailScoreRecords("Top", records)