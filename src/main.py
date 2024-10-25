import argparse
import yaml
import initializer 
import submitter
from relative_score_calculater import get_relative_score_calculator

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

    # コマンドライン引数をパース
    args = parser.parse_args()

    if args.command == 'setup':
        initializer.execute()
    elif args.command == 'submit':
        scoring_type = load_scoring_type()
        if args.submit_file:
            submitter.execute(get_relative_score_calculator(scoring_type), submit_file=args.submit_file)
        else:
            submitter.execute(get_relative_score_calculator(scoring_type))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
