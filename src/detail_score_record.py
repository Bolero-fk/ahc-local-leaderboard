from database_manager import DatabaseManager 

class DetailScoreRecord:
    def __init__(self, input_test_case, absolute_score, top_score):
        self.input_test_case = input_test_case
        self.absolute_score = absolute_score
        self.top_score = top_score

class DetailScoreRecords:
    def __init__(self, id, records):
        self.id = id
        self.records = records

    @classmethod
    def fetch(cls, submission_id):
        """指定された提出のテストケース情報を取得"""

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

            return cls(submission_id, records)