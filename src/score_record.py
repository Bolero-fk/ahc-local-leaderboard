from datetime import datetime
from rich.text import Text

from database_manager import DatabaseManager 

class ScoreRecord:
    def __init__(self, id, submission_time, total_absolute_score, total_relative_score, invalid_score_count):
        self.id = id
        self.submission_time = submission_time
        self.total_absolute_score = total_absolute_score
        self.total_relative_score = total_relative_score
        self.invalid_score_count = invalid_score_count

    @classmethod
    def fetch_top(cls):
        """トップスコアの合計情報を取得"""
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
        return cls("Top", "Top Score Summary", total_absolute_score, total_relative_score, invalid_score_count)


class ScoreRecords:
    def __init__(self, records):
        self.records = records

    @classmethod
    def fetch_latest(cls, limit=10):
        """データベースから最新のスコア履歴を取得し、ScoreRecords インスタンスを返す"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, submission_time, total_absolute_score, total_relative_score, invalid_score_count
                FROM score_history
                ORDER BY submission_time DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
        
        records = [ScoreRecord(*row) for row in rows]
        return cls(records)

    def calculate_score_rankings(self):
        """total_relative_score の順位を計算し、各スコアに最も良い順位を割り当てる"""
        sorted_scores = sorted(set(record.total_relative_score for record in self.records), reverse=True)
        score_rankings = {score: rank + 1 for rank, score in enumerate(sorted_scores)}
        return score_rankings
