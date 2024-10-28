from database_manager import DatabaseManager 

class ScoreRecord:
    def __init__(self, id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank):
        self.id = id
        self.submission_time = submission_time
        self.total_absolute_score = total_absolute_score
        self.total_relative_score = total_relative_score
        self.invalid_score_count = invalid_score_count
        self.relative_rank = relative_rank
    
    def add_score(self, detail_record, relative_score):
        if (detail_record.absolute_score is not None):
            self.total_absolute_score += detail_record.absolute_score
        else:
            self.invalid_score_count += 1

        self.total_relative_score += relative_score

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
        return cls("Top", "Top Score Summary", total_absolute_score, total_relative_score, invalid_score_count, "Top")

    @classmethod
    def fetch(cls, submission_id):
        """指定された提出IDの詳細を表示する"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
                FROM score_history
                WHERE id = ?     
            ''', (submission_id, ))
            id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank = cursor.fetchone()
        
            return cls(id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank)

class ScoreRecords:
    def __init__(self, records):
        self.records = records

    @classmethod
    def fetch_latest(cls, limit=10):
        """データベースから最新のスコア履歴を取得し、ScoreRecords インスタンスを返す"""
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, submission_time, total_absolute_score, total_relative_score, invalid_score_count, relative_rank
                FROM score_history
                ORDER BY submission_time DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
        
        records = [ScoreRecord(*row) for row in rows]
        return cls(records)
