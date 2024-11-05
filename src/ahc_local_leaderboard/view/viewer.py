from ahc_local_leaderboard.database.database_manager import (
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.view.table_builder import (
    DetailTableBuilder,
    SummaryTableBuilder,
    TopDetailTableBuilder,
)

MAX_SINGLE_RELATIVE_SCORE = 1000000000

def fetch_sum_max_relative_score():
    test_case_count = TopScoresRepository.fetch_test_case_count()
    return test_case_count * MAX_SINGLE_RELATIVE_SCORE

def view_latest_scores(list_length):
    """データベースから最新の{list_length}件のスコア履歴を取得し、トップスコアの合計を加えて表示する"""

    top_record = TopScoresRepository.fetch_top_summary_record()
    score_records = ScoreHistoryRepository.fetch_latest_records(list_length)

    table_builder = SummaryTableBuilder(f"Latest {len(score_records.records)} Scores (Including Top Score)", fetch_sum_max_relative_score())
    table_builder.insert_record(top_record)
    table_builder.add_separator_row()

    for record in score_records.records:
        table_builder.insert_record(record)
    
    table_builder.display()

def show_summary_list(list_length):
    """最新{list_length}件とトップスコアのサマリーをまとめて表示する"""
    view_latest_scores(list_length)

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
    summary_record = ScoreHistoryRepository.fetch_record(submission_id)
    show_summary_table(summary_record)

    detail_records = TestCaseRepository.fetch_records(submission_id)
    show_test_case_table(detail_records, relative_score_calculator)

def show_latest_detail(relative_score_calculator):
    """最新の提出の詳細を表示する"""
    latest_id = ScoreHistoryRepository.fetch_latest_id()
    show_detail(latest_id, relative_score_calculator)

def show_top_test_case_table(detail_records):
    """トップテストケースの詳細を表示するテーブルを作成"""
    table_builder = TopDetailTableBuilder(f"Submission Details for Top Case")
    for detail_record in sorted(detail_records.records, key=lambda record: record.input_test_case):
        table_builder.insert_record(detail_record)
    
    table_builder.display()

def show_top_detail():
    """各テストケースにおけるトップケースの詳細を表示する"""
    detail_records = TopScoresRepository.fetch_top_detail_records()
    show_top_test_case_table(detail_records)
