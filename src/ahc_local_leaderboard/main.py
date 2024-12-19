import argparse
from pathlib import Path

from ahc_local_leaderboard.config import Config
from ahc_local_leaderboard.consts import (
    get_config_path,
    get_database_path,
    get_leader_board_path,
    get_root_dir,
    get_top_dir,
)
from ahc_local_leaderboard.dependency_setup import (
    Dependencies,
    PrevDependencies,
    setup_initial_dependencies,
    setup_pahcer_test_file_processor,
    setup_scoring_dependencies,
)
from ahc_local_leaderboard.init.initializer import Initializer
from ahc_local_leaderboard.models.sort_config import (
    DetailScoreRecordsSortConfig,
    SummaryScoreRecordsSortConfig,
)
from ahc_local_leaderboard.models.test_file import TestFiles
from ahc_local_leaderboard.submit.submitter import Submitter
from ahc_local_leaderboard.submit.test_file_processor import TestFilesProcessor
from ahc_local_leaderboard.utils.console_handler import ConsoleHandler
from ahc_local_leaderboard.utils.validator import (
    InitValidator,
    SubmitValidator,
    ViewValidator,
)
from ahc_local_leaderboard.view.viewer import Viewer


def handle_setup(initial_dependencies: PrevDependencies) -> None:
    """ローカル順位表のセットアップを実行します。"""
    initializer = Initializer(
        initial_dependencies["record_write_service"],
        initial_dependencies["file_utility"],
        get_database_path(),
        [get_leader_board_path(), get_top_dir()],
        get_config_path(),
    )
    initializer.execute()


def handle_submit(dependencies: Dependencies, test_files: TestFiles, skip_duplicate: bool) -> None:
    """指定した出力をローカル順位表に送信します。"""
    submitter = Submitter(
        dependencies["record_write_service"],
        dependencies["test_files_processor"],
        dependencies["test_cases_processor"],
        dependencies["reserved_record_updater"],
        dependencies["relative_score_updater"],
        dependencies["submission_matcher"],
    )

    submit_result = submitter.execute(test_files, skip_duplicate)

    if submit_result:
        viewer = Viewer(
            dependencies["record_read_service"],
            dependencies["relative_score_calculator"],
        )

        sort_config = DetailScoreRecordsSortConfig("id", "asc", dependencies["relative_score_calculator"])

        viewer.show_latest_detail(sort_config)
    else:
        ConsoleHandler.print_info("Skipping duplicate submissions")


def handle_view(dependencies: Dependencies, limit: int, detail: str, sort_column: str, sort_order: str) -> None:
    """スコア履歴やテストケースの詳細を表示します。"""
    viewer = Viewer(
        dependencies["record_read_service"],
        dependencies["relative_score_calculator"],
    )
    if detail:
        if detail.isdigit():
            sort_config = DetailScoreRecordsSortConfig(
                sort_column, sort_order, dependencies["relative_score_calculator"]
            )
            viewer.show_detail(int(detail), sort_config)
        elif detail == "latest":
            sort_config = DetailScoreRecordsSortConfig(
                sort_column, sort_order, dependencies["relative_score_calculator"]
            )
            viewer.show_latest_detail(sort_config)
        elif detail == "top":
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
        viewer.show_summary_list(limit, SummaryScoreRecordsSortConfig(sort_column, sort_order))


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Lederboard")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("setup", help="Setup the local leaderboard")

    submit_parser = subparsers.add_parser("submit", help="Submit output to the local leaderboard")
    submit_parser.add_argument(
        "--submit-file", type=str, help="Specify the submit file to submit. Default is 'out'.", default="out"
    )

    submit_parser.add_argument(
        "--pahcer-directory",
        type=str,
        help="Specify the directory containing pahcer files. If specified, scores will be extracted from these files.",
        default=None,
    )

    submit_parser.add_argument(
        "--skip-duplicate",
        action="store_true",
        help="Skip submission if the same submission already exists in the database.",
    )

    view_parser = subparsers.add_parser("view", help="View score history and test case details")

    view_parser.add_argument(
        "limit",
        help="Specify the number of score history entries to display. Default is 10.",
        type=int,
        nargs="?",
        default=10,
    )

    view_parser.add_argument(
        "--detail",
        help="Specify the submission Id to view details (can specify ID, latest, or top)",
        type=str,
        metavar="<id>",
    )

    view_parser.add_argument(
        "--sort-column",
        help="Column to sort by (default: id). Choices: id, rank, time, abs, rel",
        type=str,
        choices=["id", "rank", "time", "abs", "rel"],
        default="id",
    )

    view_parser.add_argument(
        "--sort-order",
        help="Sort order (default: desc).",
        type=str,
        choices=["asc", "desc"],
        default="desc",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    initial_dependencies = setup_initial_dependencies()
    if args.command == "setup":
        handle_setup(initial_dependencies)
        return

    init_validator = InitValidator()

    if not init_validator.validate(args):
        init_validator.print_errors()
        ConsoleHandler.print_directive("local-leaderboard setup")
        return

    config = Config(get_config_path())

    dependencies = setup_scoring_dependencies(config, initial_dependencies)

    if args.command == "submit":

        test_files = TestFiles(get_root_dir() / "in", get_root_dir() / args.submit_file)
        submit_validator = SubmitValidator(test_files)
        if not submit_validator.validate(args):
            submit_validator.print_errors()
            return

        if args.pahcer_directory:
            pahcer_test_file_processor = setup_pahcer_test_file_processor(Path(args.pahcer_directory))
            assert pahcer_test_file_processor
            dependencies["test_files_processor"] = TestFilesProcessor(pahcer_test_file_processor)

        try:
            dependencies["db_manager"].begin_transaction()
            handle_submit(dependencies, test_files, args.skip_duplicate)
            dependencies["db_manager"].commit()
        except Exception as e:
            dependencies["db_manager"].rollback()
            ConsoleHandler.print_error(f"Faild to submit file: {e}")

    elif args.command == "view":
        view_validator = ViewValidator(dependencies["record_read_service"])
        if not view_validator.validate(args):
            view_validator.print_errors()
            return

        handle_view(dependencies, args.limit, args.detail, args.sort_column, args.sort_order)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
