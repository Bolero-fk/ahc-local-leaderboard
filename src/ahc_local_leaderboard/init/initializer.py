import yaml

from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.utils.file_utility import FileUtility


class Initializer:

    LEADERBOARD_DIRECTORIES = ["leader_board", "leader_board/top"]
    CONFIG_PATH = "leader_board/config.yaml"

    def __init__(self, record_write_service: RecordWriteService, file_utility: FileUtility, db_path: str):
        self.record_write_service = record_write_service
        self.file_utility = file_utility
        self.db_path = db_path

    def create_directories(self) -> None:
        """順位表用に必要なディレクトリを作成します。"""
        for directory in self.LEADERBOARD_DIRECTORIES:
            self.file_utility.try_create_directory(directory)

    def initialize_database(self) -> None:
        """データベースが存在しない場合、初期化します。"""
        if not self.file_utility.path_exists(self.db_path):
            self.record_write_service.setup_database()

    def prompt_scoring_type(self) -> str:
        """ユーザーにスコアの計算方法を選択させ、その結果を返します。"""
        while True:
            print("スコアの計算方法を選択してください:")
            print("1: Maximization（スコアが高い方が良い）")
            print("2: Minimization（スコアが低い方が良い）")
            choice = input("選択肢の番号を入力してください（1または2）: ")

            if choice in ["1", "2"]:
                return "Maximization" if choice == "1" else "Minimization"
            print("無効な入力です。1または2を入力してください。")

    def write_config_file(self, config_data: dict[str, str]) -> None:
        """指定された設定データをconfig.yamlファイルに書き込みます。"""
        with open(self.CONFIG_PATH, "w") as file:
            yaml.dump(config_data, file)

    def create_config_file(self) -> None:
        """設定ファイルが存在しない場合、ユーザーに設定を尋ねて作成します。"""
        if not self.file_utility.path_exists(self.CONFIG_PATH):
            scoring_type = self.prompt_scoring_type()
            config_data = {"scoring_type": scoring_type}
            self.write_config_file(config_data)

    def execute(self) -> None:
        """全ての初期化処理（ディレクトリ、データベース、設定ファイル）を実行します。"""
        self.create_directories()
        self.initialize_database()
        self.create_config_file()
