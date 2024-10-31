import argparse
import yaml
import init.initializer as initializer 

from submit.submitter import Submitter
import view.viewer as viewer
from utils.relative_score_calculater import get_relative_score_calculator
import database.relative_score_updater as relative_score_updater
from utils.validator import Validator

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
        '--detail',
        help='Specify the submission Id to view details (can specify ID, latest, or top)',
        type=str,
        metavar="<id>"
    )

    # コマンドライン引数をパース
    args = parser.parse_args()

    if args.command == 'setup':
        initializer.execute()

    if(not Validator.validate_file_structure()):
        print("Structure validation failed. Please run the setup command.\n")
        return

    if args.command == 'submit':
        scoring_type = load_scoring_type()
        submitter = Submitter(get_relative_score_calculator(scoring_type))
        if args.submit_file:
            submitter.execute(submit_file_path=args.submit_file)
        else:
            submitter.execute()

        relative_score_updater.update_relative_score(get_relative_score_calculator(scoring_type))
        relative_score_updater.update_relative_ranks()

    elif args.command == 'view':
        if args.detail:
            scoring_type = load_scoring_type()
            if args.detail.isdigit() and Validator.validate_id_exists(int(args.detail)):
                viewer.show_detail(int(args.detail), get_relative_score_calculator(scoring_type))
            elif args.detail == "latest":
                viewer.show_latest_detail(get_relative_score_calculator(scoring_type))
            elif args.detail == "top":
                viewer.show_top_detail()
            else:
                print("Error: Please specify a valid ID, 'latest', or 'top'")
        else:
            viewer.show_summary_list()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
