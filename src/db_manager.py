import sqlite3

def add_score(score, input_file, output_file, top_score, submission_time):
    conn = sqlite3.connect('score_history.db')
    cursor = conn.cursor()

    # スコアデータを挿入
    cursor.execute('''
        INSERT INTO score_history (score, test_case_input, test_case_output, top_score, submission_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (score, input_file, output_file, top_score, submission_time))

    conn.commit()
    conn.close()

def get_scores():
    conn = sqlite3.connect('score_history.db')
    cursor = conn.cursor()

    # すべてのスコア履歴を取得
    cursor.execute('SELECT * FROM score_history')
    rows = cursor.fetchall()

    conn.close()
    return rows
