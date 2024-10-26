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
    table.add_column("Ranking", justify="right")
    table.add_column("Submission Time", justify="left")
    table.add_column("Total Absolute Score", justify="right")
    table.add_column("Total Relative Score", justify="right")

    sorted_scores = sorted([row[2] for row in rows[1:]], reverse=True)  # 降順にソート
    score_rankings = {}
    current_rank = 1

    # スコアごとに最も良い順位を割り当てる
    for i, score in enumerate(sorted_scores):
        if score not in score_rankings:
            score_rankings[score] = current_rank  # 新しいスコアが出現したら現在の順位を割り当て
        current_rank += 1

    # 最初の行 (Top Score Summary) の追加
    submission_time, total_absolute_score, total_relative_score, invalid_score_count = rows[0]
    abs_score_text = Text(str(total_absolute_score), style="white")
    if invalid_score_count > 0:
        abs_score_text.append(f" ({invalid_score_count})", style="bold red")

    table.add_row("Top", submission_time, abs_score_text, str(total_relative_score))

    # 区切り線を追加
    table.add_row("─" * 8, "─" * 20, "─" * 20, "─" * 20)

    # 最新10件のスコア履歴をテーブルに追加
    for submission_time, total_absolute_score, total_relative_score, invalid_score_count in rows[1:]:

        # Total Absolute Scoreの表示を調整
        if invalid_score_count > 0:
            abs_score_text = Text(f"{total_absolute_score}", style="white")
            abs_score_text.append(f" ({invalid_score_count})", style="bold red")
        else:
            abs_score_text = Text(str(total_absolute_score), style="white")

        # total_relative_score の順位を取得
        rank = score_rankings[total_relative_score]

        table.add_row(str(rank), submission_time, abs_score_text, str(total_relative_score))

    console.print(table)

def execute():
    """最新10件とトップスコアのサマリーをまとめて表示する"""
    view_latest_10_scores()
