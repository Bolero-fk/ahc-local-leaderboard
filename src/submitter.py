import shutil
from datetime import datetime

import score_calculater
from database_manager import DatabaseManager
from score_record import ScoreRecord
from detail_score_record import DetailScoreRecords, DetailScoreRecord
import viewer

def copy_output_file(submit_file, test_case):
    output_file = f'{submit_file}/{test_case.file_name}'
    dest_file = f'leader_board/top/{test_case.file_name}'

    try:
        shutil.copy(output_file, dest_file)
    except Exception as e:
        print(f"Failed to copy file {output_file}: {e}")

class Submitter:
    def __init__(self, relative_score_calculator):
        self.relative_score_calculator = relative_score_calculator

    def _process_test_cases(self, test_cases, score_history_id):
        """各テストケースのスコアと記録を処理する"""
        detail_records = DetailScoreRecords(score_history_id, [])
        score_record = ScoreRecord(score_history_id, self.submission_time, 0, 0, 0, None)

        for test_case in test_cases:
            new_top_score = self._try_update_top_score(test_case, score_history_id)
            relative_score = self.relative_score_calculator.calculate_relative_score(test_case.score, new_top_score)

            DatabaseManager.insert_test_case(test_case, score_history_id)

            detail_record = DetailScoreRecord(test_case.file_name, test_case.score, new_top_score)
            detail_records.records.append(detail_record)
            score_record.add_score(detail_record, relative_score)

        return detail_records, score_record

    def _try_update_top_score(self, test_case, score_history_id):
        """テストケースのスコアを評価し、必要に応じてトップスコアを更新する"""
        top_score = DatabaseManager.fetch_top_score(test_case)
        is_topscore_case = self.relative_score_calculator.is_better_score(test_case.score, top_score)

        if is_topscore_case:
            DatabaseManager.update_top_score(test_case, score_history_id)
            copy_output_file(self.submit_file_path, test_case)

        new_top_score = test_case.score if is_topscore_case else top_score
        return new_top_score

    def execute(self, submit_file_path='out'):
        self.submit_file_path = submit_file_path
        self.submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        test_cases = score_calculater.execute(submit_file_path)
        score_history_id = DatabaseManager.reserve_score_history_table(self.submission_time)

        detail_records, score_record = self._process_test_cases(test_cases, score_history_id)
            
        viewer.show_test_case_table(detail_records, self.relative_score_calculator)
        DatabaseManager.update_score_history_table(score_record)
