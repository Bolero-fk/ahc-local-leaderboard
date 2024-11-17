from typing import TypedDict

from ahc_local_leaderboard.config import Config
from ahc_local_leaderboard.database.database_manager import (
    DatabaseManager,
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.submit.relative_score_updater import RelativeScoreUpdater
from ahc_local_leaderboard.submit.reserved_record_updater import ReservedRecordUpdater
from ahc_local_leaderboard.submit.test_case_processor import (
    TestCaseProcessor,
    TestCasesProcessor,
)
from ahc_local_leaderboard.submit.test_file_processor import (
    AtCoderTestFileProcessor,
    TestFilesProcessor,
)
from ahc_local_leaderboard.utils.file_utility import FileUtility
from ahc_local_leaderboard.utils.relative_score_calculater import (
    RelativeScoreCalculaterInterface,
    get_relative_score_calculator,
)


class PrevDependencies(TypedDict):
    """scoring_type に依存しない初期依存関係を定義する型。"""

    record_read_service: RecordReadService
    record_write_service: RecordWriteService
    file_utility: FileUtility
    db_manager: DatabaseManager


class Dependencies(TypedDict):
    """scoring_type に依存するすべての依存関係を定義する型。"""

    record_read_service: RecordReadService
    record_write_service: RecordWriteService
    relative_score_calculator: RelativeScoreCalculaterInterface
    file_utility: FileUtility
    test_files_processor: TestFilesProcessor
    test_cases_processor: TestCasesProcessor
    relative_score_updater: RelativeScoreUpdater
    reserved_record_updater: ReservedRecordUpdater
    db_manager: DatabaseManager


def setup_initial_dependencies() -> PrevDependencies:
    """scoring_type に依存しない初期依存関係を生成します。"""
    db_manager = DatabaseManager()
    score_history_repo = ScoreHistoryRepository(db_manager)
    tese_case_repo = TestCaseRepository(db_manager)
    top_scores_repo = TopScoresRepository(db_manager)

    record_read_service = RecordReadService(score_history_repo, tese_case_repo, top_scores_repo)
    record_write_service = RecordWriteService(db_manager, score_history_repo, tese_case_repo, top_scores_repo)
    file_utility = FileUtility()

    return {
        "db_manager": db_manager,
        "record_read_service": record_read_service,
        "record_write_service": record_write_service,
        "file_utility": file_utility,
    }


def setup_scoring_dependencies(config: Config, initial_dependencies: PrevDependencies) -> Dependencies:
    """scoring_type に依存する依存関係を追加します。"""
    relative_score_calculator = get_relative_score_calculator(config.get_scoring_type())
    test_files_processor = TestFilesProcessor(AtCoderTestFileProcessor())
    test_cases_processor = TestCasesProcessor(
        TestCaseProcessor(
            initial_dependencies["record_read_service"],
            initial_dependencies["record_write_service"],
            relative_score_calculator,
            initial_dependencies["file_utility"],
        )
    )
    relative_score_updater = RelativeScoreUpdater(
        initial_dependencies["record_read_service"],
        initial_dependencies["record_write_service"],
        relative_score_calculator,
    )
    reserved_record_updater = ReservedRecordUpdater(
        initial_dependencies["record_read_service"],
        initial_dependencies["record_write_service"],
        relative_score_calculator,
    )

    all_dependencies: Dependencies = {
        **initial_dependencies,
        "relative_score_calculator": relative_score_calculator,
        "test_files_processor": test_files_processor,
        "test_cases_processor": test_cases_processor,
        "relative_score_updater": relative_score_updater,
        "reserved_record_updater": reserved_record_updater,
    }

    return all_dependencies
