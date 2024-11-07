from ahc_local_leaderboard.database.database_manager import (
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.models.summary_score_record import SummaryScoreRecord
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
)


def calculate_total_relative_score_diff(
    relative_score_calculator: RelativeScoreCalculaterInterface,
    non_latest_record: SummaryScoreRecord,
    updated_top_scores: list[tuple[str, int, int]],
) -> int:
    """指定された score_history_id と更新が必要なトップスコアから相対スコアを計算する"""

    total_score_diff = 0
    for test_case_input, top_score, second_top_score in updated_top_scores:
        # 各テストケースのスコア履歴からスコアを取得し、相対スコアを計算
        absolute_score = TestCaseRepository.fetch_absolute_score(test_case_input, non_latest_record.id)
        total_score_diff -= relative_score_calculator(absolute_score, second_top_score)
        total_score_diff += relative_score_calculator(absolute_score, top_score)

    return total_score_diff


def update_score_history_with_relative_diff(non_latest_record: SummaryScoreRecord, relative_score_diff: int) -> None:
    """score_history テーブルの total_relative_score を relative_score_diff に基づき更新する関数"""

    non_latest_record.total_relative_score += relative_score_diff
    ScoreHistoryRepository.update_score_history(non_latest_record)


def update_relative_score(relative_score_calculator: RelativeScoreCalculaterInterface) -> None:
    updated_top_scores = TopScoresRepository.fetch_updated_top_scores()

    # すべての history_id を取得（最新の要素はデータベースに追加時に計算済みなので除外）
    non_latest_records = ScoreHistoryRepository.fetch_non_latest_records()

    for non_latest_record in non_latest_records.records:
        total_relative_score_diff = calculate_total_relative_score_diff(
            relative_score_calculator, non_latest_record, updated_top_scores
        )
        update_score_history_with_relative_diff(non_latest_record, total_relative_score_diff)

    TopScoresRepository.reset_is_updated_flags()


def update_relative_rank(latest_record: SummaryScoreRecord) -> None:
    """指定されたidについてランクを設定する関数"""

    # 最新の提出の relative_score より高いスコアを持つ提出数を数える
    latest_record.relative_rank = ScoreHistoryRepository.count_higher_score_records(latest_record) + 1

    ScoreHistoryRepository.update_score_history(latest_record)


def update_lower_ranks(latest_record: SummaryScoreRecord) -> None:
    """指定されたスコアより低いスコアを持つ提出のランクを +1 する関数"""

    lower_score_records = ScoreHistoryRepository.fetch_lower_score_records(latest_record)

    for lower_score_record in lower_score_records.records:
        assert isinstance(lower_score_record.relative_rank, int)
        lower_score_record.relative_rank += 1
        ScoreHistoryRepository.update_score_history(lower_score_record)


def update_relative_ranks() -> None:
    latest_record = ScoreHistoryRepository.fetch_latest_record()
    if not latest_record:
        return  # データがない場合は処理終了

    update_relative_rank(latest_record)
    update_lower_ranks(latest_record)
