import sqlite3
from rich.console import Console
from rich.table import Table

console = Console()

def get_top_score_summary():
    """top_scores テーブルから合計 Absolute Score とトップスコアの情報を取得"""
    db_path = 'leader_board/leader_board.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # 全テストケースのトップスコアの合計を取得
        cursor.execute('SELECT SUM(top_absolute_score), COUNT(*) FROM top_scores')
        total_absolute_score, test_case_count = cursor.fetchone()

    # Total Relative Score を 10^9 * テストケース数 で計算
    total_relative_score = 10**9 * test_case_count

    # トップスコアの情報を仮定した形式で返す
    return ("Top Score Summary", total_absolute_score, total_relative_score)

def view_latest_10_scores():
    """データベースから最新の10件のスコア履歴を取得し、トップスコアの合計を加えて表示する"""
    db_path = 'leader_board/leader_board.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 最新10件のスコア履歴を取得
        cursor.execute('''
            SELECT submission_time, total_absolute_score, total_relative_score
            FROM score_history
            ORDER BY submission_time DESC
            LIMIT 10
        ''')
        rows = cursor.fetchall()

    # トップスコアの合計情報を取得
    top_score_summary = get_top_score_summary()

    # 表を作成
    table = Table(title="Latest 10 Scores (Including Top Score)")
    table.add_column("Submission Time", justify="left")
    table.add_column("Total Absolute Score", justify="right")
    table.add_column("Total Relative Score", justify="right")

    # トップスコアを先頭に追加
    table.add_row(*map(str, top_score_summary))

    # 最新10件のスコア履歴をテーブルに追加
    for row in rows:
        table.add_row(row[0], str(row[1]), str(row[2]))

    console.print(table)

def execute():
    """最新10件とトップスコアのサマリーをまとめて表示する"""
    view_latest_10_scores()