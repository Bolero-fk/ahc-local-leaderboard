from database_manager import DatabaseManager 

class DetailScoreRecord:
    def __init__(self, id, input_test_cases, absolute_scores, top_scores):
        self.id = id
        self.input_test_cases = input_test_cases
        self.absolute_scores = absolute_scores
        self.top_scores = top_scores

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
            input_test_cases = [row[0] for row in rows]
            absolute_scores = [row[1] for row in rows]
            top_scores = [row[2] for row in rows]

            return cls(submission_id, input_test_cases, absolute_scores, top_scores)