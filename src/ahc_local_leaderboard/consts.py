from pathlib import Path

ROOT_DIR = Path.cwd()


def get_root_dir() -> Path:
    """プロジェクトのルートディレクトリを返します。"""
    return ROOT_DIR


def get_leader_board_path() -> Path:
    """順位表ディレクトリのパスを返します。"""
    return get_root_dir() / "leader_board"


def get_database_path() -> Path:
    """データベースファイルのパスを返します。"""
    return get_leader_board_path() / "leader_board.db"


def get_config_path() -> Path:
    """設定ファイル（config.yaml）のパスを返します。"""
    return get_leader_board_path() / "config.yaml"


def get_top_dir() -> Path:
    """トップスコアデータのディレクトリパスを返します。"""
    return get_leader_board_path() / "top"


def get_datetime_format() -> str:
    """日時を文字列に変換するためのフォーマットを取得します。"""
    return "%Y-%m-%d %H:%M:%S"
