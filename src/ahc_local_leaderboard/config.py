from pathlib import Path
from typing import Any, Dict

import yaml


class Config:

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config_data = self.load()

    def load(self) -> Dict[str, Any]:
        """設定ファイルを読み込み、辞書形式で返します。"""
        try:
            with open(self.config_path, "r") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{self.config_path}' not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading configuration file: {e}")

    def get_scoring_type(self) -> str:
        """scoring_type のデフォルト値を返します。"""
        return str(self.config_data.get("scoring_type", "Minimization"))
