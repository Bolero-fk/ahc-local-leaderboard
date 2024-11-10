import argparse
from typing import Any, Dict

import yaml

import ahc_local_leaderboard.database.relative_score_updater as relative_score_updater
from ahc_local_leaderboard.database.database_manager import (
    ScoreHistoryRepository,
    TestCaseRepository,
    TopScoresRepository,
)
from ahc_local_leaderboard.database.record_read_service import RecordReadService
from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.init import initializer as initializer
from ahc_local_leaderboard.models.test_file import TestFiles
from ahc_local_leaderboard.submit.reserved_record_updater import ReservedRecordUpdater
from ahc_local_leaderboard.submit.submitter import Submitter
from ahc_local_leaderboard.submit.test_case_processor import (
    TestCaseProcessor,
    TestCasesProcessor,
)
from ahc_local_leaderboard.submit.test_file_processor import (
    AtCoderTestFileProcessor,
    TestFilesProcessor,
)
from ahc_local_leaderboard.utils.console_handler import ConsoleHandler
from ahc_local_leaderboard.utils.file_utility import FileUtility
from ahc_local_leaderboard.utils.relative_score_calculater import (
    get_relative_score_calculator,
)
from ahc_local_leaderboard.utils.validator import Validator
from ahc_local_leaderboard.view.viewer import Viewer


def load_scoring_type() -> str:
    """config.yaml を読み込み、scoring_type に基づいた計算クラスを返す"""
    with open("leader_board/config.yaml", "r") as file:
        config: Dict[str, Any] = yaml.safe_load(file)

    return str(config.get("scoring_type", "Minimization"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Lederboard")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("setup", help="Setup the local leaderboard")

    submit_parser = subparsers.add_parser("submit", help="Submit output to the local leaderboard")
    submit_parser.add_argument("--submit-file", type=str, help="Specify the submit file to submit")

    view_parser = subparsers.add_parser("view", help="View score history and test case details")

    view_parser.add_argument(
        "limit", help="Specify the number of score history entries to display", type=int, nargs="?", default=10
    )

    view_parser.add_argument(
        "--detail",
        help="Specify the submission Id to view details (can specify ID, latest, or top)",
        type=str,
        metavar="<id>",
    )

    args = parser.parse_args()

    if args.command == "setup":
        initializer.execute()
        return

    if not Validator.validate_file_structure():
        ConsoleHandler.print_error("Structure validation failed.")
        ConsoleHandler.print_directive("local-leaderboard setup")
        return

    scoring_type = load_scoring_type()
    relative_score_calculator = get_relative_score_calculator(scoring_type)

    record_read_service = RecordReadService(ScoreHistoryRepository(), TestCaseRepository(), TopScoresRepository())
    record_write_service = RecordWriteService(ScoreHistoryRepository(), TestCaseRepository(), TopScoresRepository())

    if args.command == "submit":
        test_files = TestFiles("in", args.submit_file)
        testfiles_processor = TestFilesProcessor(AtCoderTestFileProcessor())

        test_cases_processor = TestCasesProcessor(
            TestCaseProcessor(record_read_service, record_write_service, relative_score_calculator, FileUtility())
        )

        reserved_record_updater = ReservedRecordUpdater(
            record_read_service, record_write_service, relative_score_calculator
        )

        submitter = Submitter(
            record_write_service,
            testfiles_processor,
            test_cases_processor,
            reserved_record_updater,
        )
        if args.submit_file:
            submitter.execute(test_files)
        else:
            submitter.execute(test_files)

        relative_score_updater.update_relative_score(relative_score_calculator)
        relative_score_updater.update_relative_ranks()
        viewer = Viewer(record_read_service, relative_score_calculator)
        viewer.show_latest_detail()

    elif args.command == "view":
        viewer = Viewer(record_read_service, relative_score_calculator)
        if args.detail:
            if args.detail.isdigit() and Validator.validate_id_exists(int(args.detail)):
                viewer.show_detail(int(args.detail))
            elif args.detail == "latest":
                viewer.show_latest_detail()
            elif args.detail == "top":
                viewer.show_top_detail()
            else:
                ConsoleHandler.print_error("Invalid argument for 'view --detail' option.")
                ConsoleHandler.print_directives(
                    [
                        "local-leaderboard view --detail <id>",
                        "local-leaderboard view --detail latest",
                        "local-leaderboard view --detail top",
                    ]
                )
        else:
            viewer.show_summary_list(args.limit)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
