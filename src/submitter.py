import sqlite3
from datetime import datetime
import score_calculater
import shutil

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

def fetch_top_score(testcase):
    """トップスコアを取得する関数"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (testcase.file_name,))
        result = cursor.fetchone()

        if not result:
            return testcase.score, True

        top_score = result[0]
        if testcase.score is not None and testcase.score < top_score:
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

def execute():
    submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    score_history_id = reserve_score_history_table(submission_time)
    testcases = score_calculater.execute()

    sum_absolute_score = 0
    sum_relative_score = 0

    for testcase in testcases:
        top_score, is_topscore_case = fetch_top_score(testcase)

        if (is_topscore_case):
            update_top_score_table(testcase, score_history_id)
            copy_output_file(testcase)

        update_test_case_table(testcase, score_history_id)

        absolute_score = 0
        relative_score = 0
        
        if (testcase.score is not None):
            absolute_score = testcase.score
            relative_score = round(pow(10, 9) * (top_score/testcase.score))
        else: 
            absolute_score = round(pow(10, 9))
            relative_score = 0

        sum_absolute_score += absolute_score
        sum_relative_score += relative_score

        print(testcase.file_name, ":", absolute_score, relative_score)
    
    update_score_history_table(score_history_id, sum_absolute_score, sum_relative_score)

    # delete_reserved_score_history(score_history_id)