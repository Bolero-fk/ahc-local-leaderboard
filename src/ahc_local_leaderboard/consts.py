from pathlib import Path

ROOT_DIR = Path.cwd()


def get_root_dir() -> Path:
    return ROOT_DIR


def get_leader_board_path() -> Path:
    return get_root_dir() / "leader_board"


def get_database_path() -> Path:
    return get_leader_board_path() / "leader_board.db"


def get_config_path() -> Path:
    return get_leader_board_path() / "config.yaml"


def get_top_dir() -> Path:
    return get_leader_board_path() / "top"
