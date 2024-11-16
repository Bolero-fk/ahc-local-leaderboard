import os
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest

from ahc_local_leaderboard.models.test_case import TestCase
from ahc_local_leaderboard.utils.file_utility import FileUtility


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """一時ディレクトリを作成して提供し、テスト後に削除する"""
    with tempfile.TemporaryDirectory() as temp_dir_path:
        yield Path(temp_dir_path)


@pytest.fixture
def test_case() -> TestCase:
    """テストケース用のモックオブジェクトを作成"""
    case = Mock(spec=TestCase)
    case.file_name = "test_submit.txt"
    case.submit_file_path = "out/test_submit.txt"
    return case


def test_path_exists(temp_dir: Path) -> None:
    # 存在するパスのテスト
    assert FileUtility.path_exists(temp_dir) is True
    # 存在しないパスのテスト
    non_existing_path = temp_dir / "nonexistent"
    assert FileUtility.path_exists(non_existing_path) is False


def test_try_create_directory(temp_dir: Path) -> None:
    # ディレクトリが存在しない場合の作成テスト
    new_dir = temp_dir / "new_directory"
    assert not os.path.exists(new_dir)
    FileUtility.try_create_directory(new_dir)
    assert os.path.exists(new_dir)

    # 既に存在するディレクトリを再作成（エラーにならないことを確認）
    FileUtility.try_create_directory(new_dir)
    assert os.path.exists(new_dir)


@patch("shutil.copy")
def test_copy_file(mock_copy: Mock, temp_dir: Path) -> None:
    src = temp_dir / "source.txt"
    dest = temp_dir / "destination.txt"

    # 正常にコピーされることをテスト
    FileUtility.copy_file(src, dest)
    mock_copy.assert_called_once_with(src, dest)

    # コピーが失敗した場合のエラーハンドリング
    mock_copy.side_effect = Exception("Copy error")
    with pytest.raises(IOError):
        FileUtility.copy_file(src, dest)


@patch("ahc_local_leaderboard.utils.validator.Validator.check_directory", return_value=True)
def test_get_top_file_path(
    mock_check_directory: Mock,
    test_case: TestCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # 順位表ディレクトリのパス取得

    test_dir = Path("test")
    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", test_dir)

    expected_path = test_dir / "leader_board/top" / test_case.file_name
    result = FileUtility.get_top_file_path(test_case)
    assert result == expected_path
    mock_check_directory.assert_called_once_with(test_dir / "leader_board/top")

    # バリデーションが失敗した場合のエラーハンドリング
    mock_check_directory.return_value = False
    with pytest.raises(FileNotFoundError):
        FileUtility.get_top_file_path(test_case)


@patch("ahc_local_leaderboard.utils.validator.Validator.check_directory", return_value=True)
@patch("shutil.copy")
def test_copy_submit_file_to_leaderboard(
    mock_copy: Mock,
    mock_check_directory: Mock,
    test_case: TestCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    test_dir = Path("test")
    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", test_dir)

    FileUtility.copy_submit_file_to_leaderboard(test_case)

    # 各バリデーションメソッドが正しく呼ばれたか確認
    mock_check_directory.assert_called_once_with(Path("test/leader_board/top"))

    # コピーが行われたか確認
    expected_dest = test_dir / "leader_board/top" / test_case.file_name
    mock_copy.assert_called_once_with(test_case.submit_file_path, expected_dest)
