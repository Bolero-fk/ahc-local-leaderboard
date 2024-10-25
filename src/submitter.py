import sqlite3
from datetime import datetime
import score_calculater
import shutil
from colorama import Fore, Style
import math
from rich.console import Console
from rich.text import Text

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

def copy_output_file(submit_file, testcase):
    output_file = f'{submit_file}/{testcase.file_name}'
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

def exponential_interpolation(start, end, t, factor=5):
    """指数関数的な補完を行う関数（expを使用）"""
    exp_t = math.exp(t * factor) - 1  # exp に基づく変換（factor で急激さを調整）
    exp_max = math.exp(factor) - 1    # 正規化のための最大値
    normalized_t = exp_t / exp_max    # 0〜1 に正規化
    return start + (end - start) * normalized_t

def get_gradient_color(relative_score):
    """relative_score の値に応じて赤→黄色→緑のグラデーションを生成する関数"""
    max_score = 1000000000

    color_thr = max_score * 0.9
    if relative_score <= color_thr:
        # 0 ~ color_thr は赤→黄色
        t = relative_score / color_thr
        red = 255
        green = exponential_interpolation(0, 255, t)
        blue = 0
    else:
        # color_thr ~ max_score は黄色→緑
        t = (relative_score - color_thr) / (max_score - color_thr)
        red = exponential_interpolation(255, 0, t)
        green = 255
        blue = 0

    return f"rgb({int(red)},{int(green)},{int(blue)})"

def print_colored_output(file_name, absolute_score, relative_score):

    absolute_score_text = Text(str(absolute_score), style="white")
    
    # relative_score のグラデーションカラーを取得
    relative_score_color = get_gradient_color(relative_score)
    relative_score_text = Text(str(relative_score), style=relative_score_color)

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
            absolute_score = relative_score_calculator.get_provisional_score()

        sum_absolute_score += absolute_score
        sum_relative_score += relative_score

        print_colored_output(testcase.file_name, testcase.score, relative_score)
    
    update_score_history_table(score_history_id, sum_absolute_score, sum_relative_score)
