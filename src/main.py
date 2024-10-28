import argparse
import yaml
import initializer 

from submitter import Submitter
import viewer
from relative_score_calculater import get_relative_score_calculator
import score_history_table_updater

def load_scoring_type():
    """config.yaml を読み込み、scoring_type に基づいた計算クラスを返す"""
    with open("leader_board/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    
    return config.get("scoring_type", "Minimization")

def main():
    # コマンドライン引数のパーサーを作成
    parser = argparse.ArgumentParser(description="AHCスコア履歴管理プログラム")
    
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    subparsers.add_parser('setup', help='ローカル順位表を準備します')

    submit_parser = subparsers.add_parser('submit', help='ローカル順位表に出力を提出します')
    submit_parser.add_argument('--submit-file', type=str, help='提出する output ファイルを指定します')

    # view コマンド
    view_parser = subparsers.add_parser('view', help='スコア履歴やテストケースを表示します')
    view_parser.add_argument(
        '--detail',
        help='詳細表示する提出IDを指定します (ID または latest または top が指定できます)',
        type=str,
        metavar="<id>"
    )

    # コマンドライン引数をパース
    args = parser.parse_args()

    if args.command == 'setup':
        initializer.execute()
    elif args.command == 'submit':
        scoring_type = load_scoring_type()
        submitter = Submitter(get_relative_score_calculator(scoring_type))
        if args.submit_file:
            submitter.execute(submit_file_path=args.submit_file)
        else:
            submitter.execute()

        score_history_table_updater.update_relative_score(get_relative_score_calculator(scoring_type))
        score_history_table_updater.update_relative_ranks()

    elif args.command == 'view':
        if args.detail:
            scoring_type = load_scoring_type()
            if args.detail.isdigit():
                viewer.show_detail(int(args.detail), get_relative_score_calculator(scoring_type))
            elif args.detail == "latest":
                viewer.show_latest_detail()
            elif args.detail == "top":
                viewer.show_top_detail()
            else:
                print("エラー: 有効なID、'latest' または 'top' を指定してください")
        else:
            viewer.show_summary_list()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
