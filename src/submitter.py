import sqlite3
from datetime import datetime
import score_calculater
import shutil

def reserve_score_history_table(submission_time):
    """スコア履歴テーブルに空の行を挿入し、そのIDを予約する"""
    conn = sqlite3.connect('leader_board/leader_board.db')
    cursor = conn.cursor()

    # 空のスコア履歴を挿入し、score_history_idを取得
    cursor.execute('''
        INSERT INTO score_history (total_absolute_score, total_relative_score, submission_time)
        VALUES (?, ?, ?)
    ''', (-1, -1, submission_time))

    score_history_id = cursor.lastrowid  # 挿入された行のIDを取得

    conn.commit()
    conn.close()

    return score_history_id

def delete_reserved_score_history(score_history_id):
    """指定されたscore_history_idの行を削除する"""
    conn = sqlite3.connect('leader_board/leader_board.db')
    cursor = conn.cursor()

    # 該当する行を削除
    cursor.execute('DELETE FROM score_history WHERE id = ?', (score_history_id,))

    conn.commit()
    conn.close()

def is_top_score(testcase):
    """トップスコアかどうかを判定する関数"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (testcase.file_name,))
        result = cursor.fetchone()

        if not result:
            return True

        top_score = result[0]
        if testcase.score is not None and testcase.score < top_score:
            return True
        
    return False

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

    for testcase in testcases:
        if (is_top_score(testcase)):
            update_top_score_table(testcase, score_history_id)
            copy_output_file(testcase)

        update_test_case_table(testcase, score_history_id)

    # delete_reserved_score_history(score_history_id)