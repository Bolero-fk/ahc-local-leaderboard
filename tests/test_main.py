import tempfile
import time
from pathlib import Path
from typing import Generator, Optional, Type

import pytest

from ahc_local_leaderboard.main import main
from ahc_local_leaderboard.models.test_file import TestFile
from ahc_local_leaderboard.submit.test_file_processor import AtCoderTestFileProcessor


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def generate_files(dir_path: Path, dir_name: str, file_names: list[str]) -> None:

    dir_path = dir_path / dir_name

    dir_path.mkdir(parents=True, exist_ok=True)

    for file_name in file_names:
        file_path = dir_path / f"{file_name}.txt"
        with file_path.open("w") as file:
            file.write(f"Content of {file_name}.txt")


def test_main_workflow(
    temp_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:

    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", temp_dir)

    # setup を実行
    monkeypatch.setattr("sys.argv", ["main.py", "setup"])
    monkeypatch.setattr("builtins.input", lambda _: "2")
    main()

    config_file = temp_dir / "leader_board" / "config.yaml"
    db_file = temp_dir / "leader_board" / "leader_board.db"

    captured = capsys.readouterr()

    assert config_file.exists()
    assert db_file.exists()

    # submit を実行
    file_names = ["0000", "0001", "0002"]
    generate_files(temp_dir, "in", file_names)
    generate_files(temp_dir, "out", file_names)

    test_case_scores1 = iter([100, 200, 300])

    def mock_process_testcase1(self: Type["AtCoderTestFileProcessor"], test_file: TestFile) -> Optional[int]:
        return next(test_case_scores1)

    monkeypatch.setattr(AtCoderTestFileProcessor, "process_test_file", mock_process_testcase1)

    monkeypatch.setattr("sys.argv", ["main.py", "submit"])
    main()

    captured = capsys.readouterr()

    # view を実行
    monkeypatch.setattr("sys.argv", ["main.py", "view"])
    main()

    captured = capsys.readouterr()

    assert "600" in captured.out  # 絶対 score の合計
    assert "3000000000" in captured.out  # 相対 score の合計

    # オプション付きで submit を再度実行
    generate_files(temp_dir, "out2", file_names)

    test_case_scores2 = iter([1000, 20, None])

    def mock_process_testcase2(self: Type["AtCoderTestFileProcessor"], test_file: TestFile) -> Optional[int]:
        return next(test_case_scores2)

    monkeypatch.setattr(AtCoderTestFileProcessor, "process_test_file", mock_process_testcase2)

    monkeypatch.setattr("sys.argv", ["main.py", "submit", "--submit-file", "out2"])
    time.sleep(1)  # submission timeが同じ提出はできないので時間をずらす
    main()

    captured = capsys.readouterr()

    assert "(1)" in captured.out  # 絶対 score がNoneのとき
    assert "1100000000" in captured.out  # 相対 scoreの合計
    assert "None" in captured.out  # 相対 scoreの合計

    # view のオプションを変更して実行
    monkeypatch.setattr("sys.argv", ["main.py", "view", "--detail", "top"])
    main()

    captured = capsys.readouterr()
    assert "100" in captured.out
    assert "20" in captured.out
    assert "300" in captured.out


'''

@pytest.fixture(scope="function")
def test_submit_file():
    """テスト用の提出ファイルを準備し、テスト後にクリーンアップ"""
    submit_file_path = "tests/test_out.txt"
    with open(submit_file_path, "w") as file:
        file.write("Sample submission data")
    yield submit_file_path
    if os.path.exists(submit_file_path):
        os.remove(submit_file_path)
'''
