import sqlite3
from datetime import datetime
import score_calculater

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

def update_top_score_table(scores, score_history_id):
    """トップスコアテーブルを更新する関数"""
    conn = sqlite3.connect('leader_board/leader_board.db')
    cursor = conn.cursor()

    for score in scores:
        cursor.execute('SELECT top_absolute_score FROM top_scores WHERE test_case_input = ?', (score.file_name,))
        result = cursor.fetchone()

        if result:
            top_score = result[0]
            if score < top_score:
                cursor.execute('''
                    UPDATE top_scores
                    SET top_absolute_score = ?, score_history_id = ?
                    WHERE test_case_input = ?
                ''', (score.score, score_history_id, score.file_name))
        else:
            cursor.execute('''
                INSERT INTO top_scores (test_case_input, top_absolute_score, score_history_id)
                VALUES (?, ?, ?)
            ''', (score.file_name, score.score, score_history_id))

    conn.commit()
    conn.close()

def execute():
    submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    score_history_id = reserve_score_history_table(submission_time)
    scores = score_calculater.execute()
    update_top_score_table(scores, score_history_id)
    # delete_reserved_score_history(score_history_id)