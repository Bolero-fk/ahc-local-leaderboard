from rich.console import Console
from rich.table import Table

from score_formatter import ScoreFormatter
from score_record import ScoreRecords, ScoreRecord

def create_score_table(title):
    """スコアテーブルを作成し、列を追加する"""
    table = Table(title=title)
    table.add_column("ID", justify="right")
    table.add_column("Rank", justify="right")
    table.add_column("Submission Time", justify="left")
    table.add_column("Total Absolute Score", justify="right")
    table.add_column("Total Relative Score", justify="right")
    return table

def add_separator_row(table):
    """区切り線をテーブルに追加する"""
    table.add_row("─" * 8, "─" * 8, "─" * 20, "─" * 20, "─" * 20)

def view_latest_10_scores():
    """データベースから最新の10件のスコア履歴を取得し、トップスコアの合計を加えて表示する"""
    
    # 最新10件のスコア履歴を取得
    score_records = ScoreRecords.fetch_latest()

    # 表を作成
    table = create_score_table("Latest 10 Scores (Including Top Score)")

    # 最初の行 (Top Score Summary) の追加
    top_record = ScoreRecord.fetch_top()
    table.add_row(
        "Top",
        "Top",
        top_record.submission_time,
        ScoreFormatter.format_total_absolute_score(top_record.total_absolute_score, top_record.invalid_score_count),
        ScoreFormatter.format_relative_score(top_record.total_relative_score, 100000000000)
    )

    # 区切り線を追加
    add_separator_row(table)

    # 最新10件のスコア履歴をテーブルに追加
    for record in score_records.records:
        table.add_row(
            str(record.id),
            str(record.relative_rank),
            record.submission_time,
            ScoreFormatter.format_total_absolute_score(record.total_absolute_score, record.invalid_score_count),
            ScoreFormatter.format_relative_score(record.total_relative_score, 100000000000)
        )
  
    Console().print(table)

def show_summary_list():
    """最新10件とトップスコアのサマリーをまとめて表示する"""
    view_latest_10_scores()
