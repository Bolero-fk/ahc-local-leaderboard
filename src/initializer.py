import os
import sqlite3
import json

def create_directories():
    """必要なディレクトリを作成する関数"""
    directories = ["leader_board", "leader_board/top"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"ディレクトリ {directory} を作成しました。")
        else:
            print(f"ディレクトリ {directory} は既に存在します。")

def initialize_database():
    """SQLiteデータベースを初期化する関数"""
    db_path = 'leader_board/leader_board.db'
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leader_board (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER,
                test_case_input TEXT,
                test_case_output TEXT,
                top_score INTEGER,
                submission_time TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print(f"データベース {db_path} を初期化しました。")
    else:
        print(f"データベース {db_path} は既に存在します。")

def setup_leaderboard_system():
    """3つの初期化処理をまとめて実行する関数"""
    create_directories()       # ディレクトリ作成
    initialize_database()      # データベース初期化
