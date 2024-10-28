import math
import shutil
from datetime import datetime

from colorama import Fore, Style
from rich.console import Console
from rich.text import Text

import score_calculater
from score_formatter import ScoreFormatter
from database_manager import DatabaseManager

def reserve_score_history_table(submission_time):
    """スコア履歴テーブルに空の行を挿入し、そのIDを予約する"""

    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO score_history (submission_time)
            VALUES (?)
        ''', (submission_time,))

    return cursor.lastrowid 

def update_score_history_table(score_history_id, sum_absolute_score, sum_relative_score, invalid_score_count):
    """スコア履歴テーブルを更新する関数"""

    with DatabaseManager() as conn:
        cursor = conn.cursor()

        # スコア履歴テーブルに絶対スコアと相対スコアを更新
        cursor.execute('''
            UPDATE score_history
            SET total_absolute_score = ?, total_relative_score = ?, invalid_score_count = ?
            WHERE id = ?
        ''', (sum_absolute_score, sum_relative_score, invalid_score_count, score_history_id))


def fetch_top_score(relative_score_calculator, testcase):
    """トップスコアを取得する関数"""

    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (testcase.file_name,))
        result = cursor.fetchone()

        if not result:
            return testcase.score, True

        top_score = result[0]
        if testcase.score is not None and relative_score_calculator.is_better_score(testcase.score, top_score):
            return testcase.score, True
        
    return top_score, False

def update_top_score_table(testcase, score_history_id):
    """トップスコアテーブルを更新する関数"""

    with DatabaseManager() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (testcase.file_name,))
        result = cursor.fetchone()

        if result is not None:
            second_top_score = result[0]
        else:
            second_top_score = None

        cursor.execute('''
            INSERT OR REPLACE INTO top_scores (test_case_input, top_absolute_score, second_top_score, is_updated, score_history_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (testcase.file_name, testcase.score, second_top_score, True, score_history_id))


def copy_output_file(submit_file, testcase):
    output_file = f'{submit_file}/{testcase.file_name}'
    dest_file = f'leader_board/top/{testcase.file_name}'

    try:
        shutil.copy(output_file, dest_file)
    except Exception as e:
        print(f"Failed to copy file {output_file}: {e}")


def update_test_case_table(testcase, score_history_id):
    """テストケーステーブルに1件ずつ行を追加する関数"""

    with DatabaseManager() as conn:
        cursor = conn.cursor()

        # 各テストケースを1件ずつ挿入
        cursor.execute('''
            INSERT INTO test_cases (test_case_input, absolute_score, score_history_id)
            VALUES (?, ?, ?)
        ''', (testcase.file_name, testcase.score, score_history_id))

def print_colored_output(file_name, absolute_score, relative_score):

    absolute_score_text = Text(str(absolute_score), style="white")
    
    relative_score_text = ScoreFormatter.format_relative_score(relative_score, 1000000000)

    # 出力
    console = Console()
    console.print(f"{file_name}: ", end="")
    console.print(absolute_score_text, end=", ")
    console.print(relative_score_text)

def execute(relative_score_calculator, submit_file='out'):
    submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    score_history_id = reserve_score_history_table(submission_time)
    testcases = score_calculater.execute(submit_file)

    sum_absolute_score = 0
    sum_relative_score = 0

    for testcase in testcases:
        top_score, is_topscore_case = fetch_top_score(relative_score_calculator, testcase)

        if (is_topscore_case):
            update_top_score_table(testcase, score_history_id)
            copy_output_file(submit_file, testcase)

        update_test_case_table(testcase, score_history_id)

        absolute_score = 0
        relative_score = relative_score_calculator.calculate_relative_score(testcase.score, top_score)

        if (testcase.score is not None):
            absolute_score = testcase.score
        else: 
            absolute_score = 0

        sum_absolute_score += absolute_score
        sum_relative_score += relative_score

        print_colored_output(testcase.file_name, testcase.score, relative_score)
    
    invalid_score_count = sum(1 for testcase in testcases if testcase.score is None)

    update_score_history_table(score_history_id, sum_absolute_score, sum_relative_score, invalid_score_count)
