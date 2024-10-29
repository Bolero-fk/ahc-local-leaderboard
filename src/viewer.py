from rich.console import Console
from rich.table import Table
from rich.text import Text

from score_formatter import ScoreFormatter
from score_record import ScoreRecords, ScoreRecord
from detail_score_record import DetailScoreRecords, DetailScoreRecord
from database_manager import DatabaseManager

def create_summary_table_with_header(title):
    """省略テーブルをヘッダー付きで作成します"""
    table = Table(title=title)
    table.add_column("Id", justify="right")
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
    table = create_summary_table_with_header("Latest 10 Scores (Including Top Score)")

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

def show_summary_table(summary_record):
    """提出サマリー情報を表示するテーブルを作成"""
    table = create_summary_table_with_header(f"Submission Summary for ID {summary_record.id}")
    table.add_row(
        str(summary_record.id),
        str(summary_record.relative_rank),
        summary_record.submission_time,
        ScoreFormatter.format_total_absolute_score(
            summary_record.total_absolute_score, 
            summary_record.invalid_score_count
        ),
        ScoreFormatter.format_relative_score(
            summary_record.total_relative_score, 
            100000000000
        )
    )

    Console().print(table)

def create_detail_table_with_header(title):
    """詳細テーブルをヘッダー付きで作成します"""
    table = Table(title=title)
    table.add_column("Test Case", justify="left")
    table.add_column("Absolute Score", justify="right")
    table.add_column("Score Diff", justify="right")
    table.add_column("Relative Score", justify="right")
    return table

def show_test_case_table(detail_records, relative_score_calculator):
    """テストケースの詳細を表示するテーブルを作成"""
    test_case_table = create_detail_table_with_header(f"Submission Details for ID {detail_records.id}")

    for detail_record in detail_records.records:
        input_text = ScoreFormatter.format_test_case_input(detail_record.input_test_case)
        abs_score_text = Text(str(detail_record.absolute_score), style="white" if str(detail_record.absolute_score).isdigit() else "red")

        score_difference = abs(detail_record.absolute_score - detail_record.top_score) if detail_record.absolute_score is not None and detail_record.top_score is not None else "None"
        score_diff_text = Text(str(score_difference), style="white" if str(score_difference).isdigit() else "red")

        relative_score = relative_score_calculator(detail_record.absolute_score, detail_record.top_score)
        relative_score_text = ScoreFormatter.format_relative_score(relative_score, 1000000000)

        test_case_table.add_row(input_text, abs_score_text, score_diff_text, relative_score_text)

    Console().print(test_case_table)

def show_detail(submission_id, relative_score_calculator):
    """指定された提出IDの詳細を表示する"""

    summary_record = ScoreRecord.fetch(submission_id)
    show_summary_table(summary_record)

    detail_records = DetailScoreRecords.fetch(submission_id)
    show_test_case_table(detail_records, relative_score_calculator)

def show_latest_detail(relative_score_calculator):
    """最新の提出の詳細を表示する"""
    latest_id = DatabaseManager.fetch_latest_id()
    show_detail(latest_id, relative_score_calculator)

def create_top_detail_table_with_header(title):
    """詳細テーブルをヘッダー付きで作成します"""
    table = Table(title=title)
    table.add_column("Test Case", justify="left")
    table.add_column("Absolute Score", justify="right")
    table.add_column("Id", justify="right")
    return table

def show_top_test_case_table(detail_records):
    """トップテストケースの詳細を表示するテーブルを作成"""
    test_case_table = create_top_detail_table_with_header(f"Submission Details for Top Case")

    for detail_record in sorted(detail_records.records, key=lambda record: record.input_test_case):
        input_text = ScoreFormatter.format_test_case_input(detail_record.input_test_case)
        abs_score_text = Text(str(detail_record.absolute_score), style="white" if str(detail_record.absolute_score).isdigit() else "red")

        test_case_table.add_row(input_text, abs_score_text, str(detail_record.id))

    Console().print(test_case_table)

def show_top_detail():
    """各テストケースにおけるトップケースの詳細を表示する"""
    detail_records = DetailScoreRecords.fetch_top_scores()
    show_top_test_case_table(detail_records)
