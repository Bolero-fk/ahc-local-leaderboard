from summary_score_record import SummaryScoreRecords, SummaryScoreRecord
from detail_score_record import DetailScoreRecords
from database_manager import DatabaseManager
from table_builder import SummaryTableBuilder, DetailTableBuilder, TopDetailTableBuilder

MAX_SINGLE_RELATIVE_SCORE = 1000000000

def fetch_sum_max_relative_score():
    test_case_count = DatabaseManager.fetch_test_case_count()
    return test_case_count * MAX_SINGLE_RELATIVE_SCORE

def view_latest_10_scores():
    """データベースから最新の10件のスコア履歴を取得し、トップスコアの合計を加えて表示する"""
    table_builder = SummaryTableBuilder("Latest 10 Scores (Including Top Score)", fetch_sum_max_relative_score())

    top_record = SummaryScoreRecord.fetch_top()
    table_builder.insert_record(top_record)

    table_builder.add_separator_row()

    # 最新10件のスコア履歴を取得
    score_records = SummaryScoreRecords.fetch_latest()
    for record in score_records.records:
        table_builder.insert_record(record)
    
    table_builder.display()

def show_summary_list():
    """最新10件とトップスコアのサマリーをまとめて表示する"""
    view_latest_10_scores()

def show_summary_table(summary_record):
    """提出サマリー情報を表示するテーブルを作成"""
    table_builder = SummaryTableBuilder(f"Submission Summary for ID {summary_record.id}", fetch_sum_max_relative_score())
    table_builder.insert_record(summary_record)
    table_builder.display()

def show_test_case_table(detail_records, relative_score_calculator):
    """テストケースの詳細を表示するテーブルを作成"""
    table_builder =  DetailTableBuilder(f"Submission Details for ID {detail_records.id}", MAX_SINGLE_RELATIVE_SCORE, relative_score_calculator)
    for detail_record in detail_records.records:
        table_builder.insert_record(detail_record)

    table_builder.display()

def show_detail(submission_id, relative_score_calculator):
    """指定された提出IDの詳細を表示する"""
    summary_record = SummaryScoreRecord.fetch(submission_id)
    show_summary_table(summary_record)

    detail_records = DetailScoreRecords.fetch(submission_id)
    show_test_case_table(detail_records, relative_score_calculator)

def show_latest_detail(relative_score_calculator):
    """最新の提出の詳細を表示する"""
    latest_id = DatabaseManager.fetch_latest_id()
    show_detail(latest_id, relative_score_calculator)

def show_top_test_case_table(detail_records):
    """トップテストケースの詳細を表示するテーブルを作成"""
    table_builder = TopDetailTableBuilder(f"Submission Details for Top Case")
    for detail_record in sorted(detail_records.records, key=lambda record: record.input_test_case):
        table_builder.insert_record(detail_record)
    
    table_builder.display()

def show_top_detail():
    """各テストケースにおけるトップケースの詳細を表示する"""
    detail_records = DetailScoreRecords.fetch_top_scores()
    show_top_test_case_table(detail_records)
