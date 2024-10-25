import os
import sqlite3
import yaml

def create_directories():
    """必要なディレクトリを作成する関数"""
    directories = ["leader_board", "leader_board/top"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

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
                total_absolute_score INTEGER,
                total_relative_score INTEGER,
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

def create_config_file():
    """スコア設定の選択をユーザーに求め、config.yaml ファイルを作成する関数"""
    config_path = "leader_board/config.yaml"

    if not os.path.exists(config_path):
        # ユーザーにスコア設定の選択を促す
        print("スコアの計算方法を選択してください:")
        print("1: Maximization（スコアが高い方が良い）")
        print("2: Minimization（スコアが低い方が良い）")
        choice = input("選択肢の番号を入力してください（1または2）: ")

        # 入力に基づいて設定を決定
        scoring_type = "Maximization" if choice == "1" else "Minimization"

        # config.yaml に設定を書き込む
        config_data = {"scoring_type": scoring_type}
        with open(config_path, "w") as file:
            yaml.dump(config_data, file)
        
def execute():
    """3つの初期化処理をまとめて実行する関数"""
    create_directories()       # ディレクトリ作成
    initialize_database()      # データベース初期化
    create_config_file()       # 設定ファイル作成
