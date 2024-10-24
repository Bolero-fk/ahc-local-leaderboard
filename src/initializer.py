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

        # スコア履歴テーブルの作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS score_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_absolute_score INTEGER NOT NULL,
                total_relative_score INTEGER NOT NULL,
                submission_time DATETIME NOT NULL UNIQUE
            )
        ''')

        # テストケーステーブルの作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_case_input TEXT NOT NULL,
                absolute_score INTEGER,
                score_history_id INTEGER NOT NULL,
                FOREIGN KEY (score_history_id) REFERENCES score_history(id)
            )
        ''')

        # トップスコアテーブルの作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_case_input TEXT NOT NULL UNIQUE,
                top_absolute_score INTEGER,
                score_history_id INTEGER NOT NULL,
                FOREIGN KEY (score_history_id) REFERENCES score_history(id)
            )
        ''')

        conn.commit()
        conn.close()
        print(f"データベース {db_path} を初期化しました。")
    else:
        print(f"データベース {db_path} は既に存在します。")

def execute():
    """3つの初期化処理をまとめて実行する関数"""
    create_directories()       # ディレクトリ作成
    initialize_database()      # データベース初期化
