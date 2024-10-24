import argparse
import db_manager
import initializer 
from datetime import datetime

def main():
    # コマンドライン引数のパーサーを作成
    parser = argparse.ArgumentParser(description="AHCスコア履歴管理プログラム")
    
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')

    # スコア追加のサブコマンド
    add_parser = subparsers.add_parser('add', help='スコアを追加します')


    add_parser.add_argument('--score', type=int, required=True, help='コンテストのスコア')
    add_parser.add_argument('--input_file', type=str, required=True, help='テストケースの入力ファイル')
    add_parser.add_argument('--output_file', type=str, required=True, help='テストケースの出力ファイル')
    add_parser.add_argument('--top_score', type=int, required=True, help='テストケースのトップスコア')

    # 履歴表示のサブコマンド
    view_parser = subparsers.add_parser('view', help='スコア履歴を表示します')

    setup_parser = subparsers.add_parser('setup', help='ローカル順位表を準備します')

    # コマンドライン引数をパース
    args = parser.parse_args()

    if args.command == 'add':
        # スコアをデータベースに追加
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db_manager.add_score(args.score, args.input_file, args.output_file, args.top_score, submission_time)
        print("スコアを追加しました。")

    elif args.command == 'setup':
        initializer.setup_leaderboard_system()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
