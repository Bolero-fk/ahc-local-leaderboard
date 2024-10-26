import sqlite3

def fetch_updated_top_scores():
    """is_updated が TRUE のトップスコアとセミトップスコアを取得する"""
    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT test_case_input, top_absolute_score, second_top_score
            FROM top_scores
            WHERE is_updated = TRUE
        ''')

        return cursor.fetchall()

def fetch_all_history_ids():
    """score_history テーブルから最新のエントリを除外してすべての score_history_id を取得する関数"""
    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id
            FROM score_history
            WHERE submission_time < (SELECT MAX(submission_time) FROM score_history)
            ORDER BY submission_time
        ''')

        return [row[0] for row in cursor.fetchall()]

def fetch_absolute_score_for_case(test_case_input, score_history_id):
    """指定された test_case_input と score_history_id に対応する absolute_score を取得する関数"""
    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT absolute_score
            FROM test_cases
            WHERE test_case_input = ? AND score_history_id = ?
        ''', (test_case_input, score_history_id))
        
        result = cursor.fetchone()
        
        if result is None:
            raise ValueError(f"No absolute_score found for test_case_input={test_case_input} and score_history_id={score_history_id}")
        
        return result[0]
    
def calculate_total_relative_score_diff (relative_score_calculator, score_history_id, updated_top_scores):
    """指定された score_history_id と更新が必要なトップスコアから相対スコアを計算する"""

    total_score_diff = 0
    for test_case_input, top_score, second_top_score in updated_top_scores:
        # 各テストケースのスコア履歴からスコアを取得し、相対スコアを計算
        absolute_score = fetch_absolute_score_for_case(test_case_input, score_history_id)
        total_score_diff -= relative_score_calculator.calculate_relative_score(absolute_score, second_top_score)
        total_score_diff += relative_score_calculator.calculate_relative_score(absolute_score, top_score)

    return total_score_diff

def update_score_history_with_relative_diff(history_id, relative_score_diff):
    """score_history テーブルの total_relative_score を relative_score_diff に基づき更新する関数"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()

        # 現在の total_relative_score を取得
        cursor.execute('''
            SELECT total_relative_score
            FROM score_history
            WHERE id = ?
        ''', (history_id,))
        current_relative_score = cursor.fetchone()[0]

        # total_relative_score を更新
        new_relative_score = current_relative_score + relative_score_diff
        cursor.execute('''
            UPDATE score_history
            SET total_relative_score = ?
            WHERE id = ?
        ''', (new_relative_score, history_id))

        conn.commit()    

def reset_is_updated_flags():
    """top_scores テーブルの is_updated フラグを FALSE にリセットする関数"""

    with sqlite3.connect('leader_board/leader_board.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE top_scores
            SET is_updated = FALSE
            WHERE is_updated = TRUE
        ''')
        conn.commit()

def execute(relative_score_calculator):
    updated_top_scores  = fetch_updated_top_scores()

    # すべての history_id を取得（最新の要素はデータベースに追加時に計算済みなので除外）
    history_ids = fetch_all_history_ids()

    for history_id in history_ids:
        total_relative_score_diff = calculate_total_relative_score_diff(relative_score_calculator, history_id, updated_top_scores)
        update_score_history_with_relative_diff(history_id, total_relative_score_diff)
    
    reset_is_updated_flags()
