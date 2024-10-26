from rich.console import Console
from rich.table import Table
from rich.text import Text
from database_manager import DatabaseManager 

console = Console()

def get_top_score_summary():
    """top_scores テーブルから合計 Absolute Score とトップスコアの情報を取得"""
    with DatabaseManager() as conn:
        cursor = conn.cursor()

        # 全テストケースのトップスコアの合計を取得
        cursor.execute('''
            SELECT COALESCE(SUM(top_absolute_score), 0) AS total_absolute_score,
                   COUNT(*) AS total_cases,
                   COUNT(*) - COUNT(top_absolute_score) AS invalid_score_count
            FROM top_scores        
        ''')
        
        total_absolute_score, test_case_count, invalid_score_count = cursor.fetchone()

    # Total Relative Score を 10^9 * テストケース数 で計算
    total_relative_score = 10**9 * test_case_count

    # トップスコアの情報を仮定した形式で返す
    return ("  Top Score Summary", total_absolute_score, total_relative_score, invalid_score_count)

def view_latest_10_scores():
    """データベースから最新の10件のスコア履歴を取得し、トップスコアの合計を加えて表示する"""
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        
        # 最新10件のスコア履歴を取得
        cursor.execute('''
            SELECT submission_time, total_absolute_score, total_relative_score, invalid_score_count
            FROM score_history
            ORDER BY submission_time DESC
            LIMIT 10
        ''')
        rows = cursor.fetchall()

    # トップスコアの合計情報を rows の先頭に追加
    rows.insert(0, get_top_score_summary())

    # 表を作成
    table = Table(title="Latest 10 Scores (Including Top Score)")
    table.add_column("Submission Time", justify="left")
    table.add_column("Total Absolute Score", justify="right")
    table.add_column("Total Relative Score", justify="right")

    # 最新10件のスコア履歴をテーブルに追加
    for submission_time, total_absolute_score, total_relative_score, invalid_score_count in rows:

        # Total Absolute Scoreの表示を調整
        if invalid_score_count > 0:
            abs_score_text = Text(f"{total_absolute_score}", style="white")
            abs_score_text.append(f" ({invalid_score_count})", style="bold red")
        else:
            abs_score_text = Text(str(total_absolute_score), style="white")

        table.add_row(submission_time, abs_score_text, str(total_relative_score))

    console.print(table)

def execute():
    """最新10件とトップスコアのサマリーをまとめて表示する"""
    view_latest_10_scores()
