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
    setup_scoring_dependencies,
)
from ahc_local_leaderboard.init.initializer import Initializer
from ahc_local_leaderboard.models.test_file import TestFiles
from ahc_local_leaderboard.submit.submitter import Submitter
from ahc_local_leaderboard.utils.console_handler import ConsoleHandler
from ahc_local_leaderboard.utils.validator import Validator
from ahc_local_leaderboard.view.viewer import Viewer


def handle_setup(initial_dependencies: PrevDependencies) -> None:
    initializer = Initializer(
        initial_dependencies["record_write_service"],
        initial_dependencies["file_utility"],
        get_database_path(),
        [get_leader_board_path(), get_top_dir()],
        get_config_path(),
    )
    initializer.execute()


def handle_submit(dependencies: Dependencies, in_dir_path: Path, submit_dir_path: Path) -> None:
    submitter = Submitter(
        dependencies["record_write_service"],
        dependencies["test_files_processor"],
        dependencies["test_cases_processor"],
        dependencies["reserved_record_updater"],
        dependencies["relative_score_updater"],
    )
    test_files = TestFiles(in_dir_path, submit_dir_path)
    submitter.execute(test_files)

    viewer = Viewer(
        dependencies["record_read_service"],
        dependencies["relative_score_calculator"],
    )
    viewer.show_latest_detail()


def handle_view(dependencies: Dependencies, limit: int, detail: str) -> None:
    viewer = Viewer(
        dependencies["record_read_service"],
        dependencies["relative_score_calculator"],
    )
    if detail:
        if detail.isdigit() and Validator.validate_id_exists(int(detail)):
            viewer.show_detail(int(detail))
        elif detail == "latest":
            viewer.show_latest_detail()
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
        viewer.show_summary_list(limit)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Lederboard")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("setup", help="Setup the local leaderboard")

    submit_parser = subparsers.add_parser("submit", help="Submit output to the local leaderboard")
    submit_parser.add_argument(
        "--submit-file", type=str, help="Specify the submit file to submit. Default is 'out'.", default="out"
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

    args = parser.parse_args()

    initial_dependencies = setup_initial_dependencies()

    if args.command == "setup":
        handle_setup(initial_dependencies)
        return

    if not Validator.validate_file_structure():
        ConsoleHandler.print_error("Structure validation failed.")
        ConsoleHandler.print_directive("local-leaderboard setup")
        return

    config = Config(get_config_path())

    dependencies = setup_scoring_dependencies(config, initial_dependencies)

    if args.command == "submit":
        handle_submit(dependencies, get_root_dir() / "in", get_root_dir() / args.submit_file)

    elif args.command == "view":
        handle_view(dependencies, args.limit, args.detail)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
