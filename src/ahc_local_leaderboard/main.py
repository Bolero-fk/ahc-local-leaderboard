import argparse
import yaml

from ahc_local_leaderboard.init import initializer as initializer
from ahc_local_leaderboard.submit.submitter import Submitter
import ahc_local_leaderboard.view.viewer as viewer
from ahc_local_leaderboard.utils.relative_score_calculater import get_relative_score_calculator
import ahc_local_leaderboard.database.relative_score_updater as relative_score_updater
from ahc_local_leaderboard.utils.validator import Validator

def load_scoring_type():
    """config.yaml を読み込み、scoring_type に基づいた計算クラスを返す"""
    with open("leader_board/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    
    return config.get("scoring_type", "Minimization")

def main():
    parser = argparse.ArgumentParser(description="Local Lederboard")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    subparsers.add_parser('setup', help='Setup the local leaderboard')

    submit_parser = subparsers.add_parser('submit', help='Submit output to the local leaderboard')
    submit_parser.add_argument('--submit-file', type=str, help='Specify the submit file to submit')

    view_parser = subparsers.add_parser('view', help='View score history and test case details')

    view_parser.add_argument(
        'limit',
        help='Specify the number of score history entries to display',
        type=int,
        nargs='?',
        default=10
    )

    view_parser.add_argument(
        '--detail',
        help='Specify the submission Id to view details (can specify ID, latest, or top)',
        type=str,
        metavar="<id>"
    )

    args = parser.parse_args()

    if args.command == 'setup':
        initializer.execute()

    if(not Validator.validate_file_structure()):
        print("Structure validation failed. Please run the setup command.\n")
        return

    scoring_type = load_scoring_type()
    relative_score_calculator = get_relative_score_calculator(scoring_type)

    if args.command == 'submit':
        submitter = Submitter(relative_score_calculator)
        if args.submit_file:
            submitter.execute(submit_file_path=args.submit_file)
        else:
            submitter.execute()

        relative_score_updater.update_relative_score(relative_score_calculator)
        relative_score_updater.update_relative_ranks()

    elif args.command == 'view':
        if args.detail:
            if args.detail.isdigit() and Validator.validate_id_exists(int(args.detail)):
                viewer.show_detail(int(args.detail), relative_score_calculator)
            elif args.detail == "latest":
                viewer.show_latest_detail(relative_score_calculator)
            elif args.detail == "top":
                viewer.show_top_detail()
            else:
                print("Error: Please specify a valid ID, 'latest', or 'top'")
        else:
            viewer.show_summary_list(args.limit)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
