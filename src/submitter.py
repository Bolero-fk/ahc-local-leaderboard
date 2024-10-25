import sqlite3
from datetime import datetime
import score_calculater
import shutil
from colorama import Fore, Style

def reserve_score_history_table(submission_time):
    """スコア履歴テーブルに空の行を挿入し、そのIDを予約する"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO score_history (total_absolute_score, total_relative_score, submission_time)
            VALUES (?, ?, ?)
        ''', (None, None, submission_time))

        score_history_id = cursor.lastrowid
        conn.commit()

    return score_history_id

def update_score_history_table(score_history_id, sum_absolute_score, sum_relative_score):
    """スコア履歴テーブルを更新する関数"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()

        # スコア履歴テーブルに絶対スコアと相対スコアを更新
        cursor.execute('''
            UPDATE score_history
            SET total_absolute_score = ?, total_relative_score = ?
            WHERE id = ?
        ''', (sum_absolute_score, sum_relative_score, score_history_id))

        conn.commit()

def fetch_top_score(relative_score_calculator, testcase):
    """トップスコアを取得する関数"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
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

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
                INSERT OR REPLACE INTO top_scores (test_case_input, top_absolute_score, score_history_id)
                VALUES (?, ?, ?)
            ''', (testcase.file_name, testcase.score, score_history_id))
        conn.commit()

def copy_output_file(testcase):
    output_file = f'out/{testcase.file_name}'
    dest_file = f'leader_board/top/{testcase.file_name}'

    try:
        shutil.copy(output_file, dest_file)
    except Exception as e:
        print(f"Failed to copy file {output_file}: {e}")


def update_test_case_table(testcase, score_history_id):
    """テストケーステーブルに1件ずつ行を追加する関数"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()

        # 各テストケースを1件ずつ挿入
        cursor.execute('''
            INSERT INTO test_cases (test_case_input, absolute_score, score_history_id)
            VALUES (?, ?, ?)
        ''', (testcase.file_name, testcase.score, score_history_id))

        conn.commit()

def get_relative_score_color(relative_score):
    """relative_score の値に応じて適切な色を返す関数 (5段階 + 特別な0と1000000000)"""
    if relative_score == 0:
        return Fore.LIGHTRED_EX + Style.BRIGHT
    elif 1 <= relative_score <= 333333333:
        return Fore.RED
    elif 333333334 <= relative_score <= 666666666:
        return Fore.YELLOW
    elif 666666667 <= relative_score < 1000000000:
        return Fore.GREEN
    elif relative_score == 1000000000:
        return Fore.GREEN + Style.BRIGHT

    return Fore.RESET 

def print_colored_output(file_name, absolute_score, relative_score):
    relative_score_color = get_relative_score_color(relative_score)
    print(f"{Fore.WHITE}{file_name}{Style.RESET_ALL}: {Fore.WHITE}{absolute_score}{Style.RESET_ALL}, {relative_score_color}{relative_score}{Style.RESET_ALL}")

def execute(relative_score_calculator):
    submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    score_history_id = reserve_score_history_table(submission_time)
    testcases = score_calculater.execute()

    sum_absolute_score = 0
    sum_relative_score = 0

    for testcase in testcases:
        top_score, is_topscore_case = fetch_top_score(relative_score_calculator, testcase)

        if (is_topscore_case):
            update_top_score_table(testcase, score_history_id)
            copy_output_file(testcase)

        update_test_case_table(testcase, score_history_id)

        absolute_score = 0
        relative_score = relative_score_calculator.calculate_relative_score(testcase.score, top_score)

        if (testcase.score is not None):
            absolute_score = testcase.score
        else: 
            absolute_score = relative_score_calculator.get_provisional_score()

        sum_absolute_score += absolute_score
        sum_relative_score += relative_score

        print_colored_output(testcase.file_name, absolute_score, relative_score)
    
    update_score_history_table(score_history_id, sum_absolute_score, sum_relative_score)
