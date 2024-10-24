import argparse
import initializer 
import submitter
from datetime import datetime

def main():
    # コマンドライン引数のパーサーを作成
    parser = argparse.ArgumentParser(description="AHCスコア履歴管理プログラム")
    
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    subparsers.add_parser('setup', help='ローカル順位表を準備します')

    subparsers.add_parser('submit', help='ローカル順位表に出力を提出します')

    # コマンドライン引数をパース
    args = parser.parse_args()

    if args.command == 'setup':
        initializer.setup_leaderboard_system()
    elif args.command == 'submit':
        initializer.setup_leaderboard_system()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
