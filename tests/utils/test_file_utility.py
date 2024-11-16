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
    with tempfile.TemporaryDirectory() as temp_dir_path:
        yield Path(temp_dir_path)


@pytest.fixture
def test_case() -> TestCase:
    case = Mock(spec=TestCase)
    case.file_name = "test_submit.txt"
    case.submit_file_path = "out/test_submit.txt"
    return case


def test_path_exists(temp_dir: Path) -> None:
    assert FileUtility.path_exists(temp_dir) is True

    non_existing_path = temp_dir / "nonexistent"
    assert FileUtility.path_exists(non_existing_path) is False


def test_try_create_directory(temp_dir: Path) -> None:
    new_dir = temp_dir / "new_directory"
    assert not os.path.exists(new_dir)
    FileUtility.try_create_directory(new_dir)
    assert os.path.exists(new_dir)

    FileUtility.try_create_directory(new_dir)
    assert os.path.exists(new_dir)


@patch("shutil.copy")
def test_copy_file(mock_copy: Mock, temp_dir: Path) -> None:
    src = temp_dir / "source.txt"
    dest = temp_dir / "destination.txt"

    FileUtility.copy_file(src, dest)
    mock_copy.assert_called_once_with(src, dest)

    mock_copy.side_effect = Exception("Copy error")
    with pytest.raises(IOError):
        FileUtility.copy_file(src, dest)


@patch("shutil.copy")
def test_copy_submit_file_to_leaderboard(
    mock_copy: Mock,
    test_case: TestCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    test_dir = Path("test")
    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", test_dir)

    FileUtility.copy_submit_file_to_leaderboard(test_case)

    expected_dest = test_dir / "leader_board/top" / test_case.file_name
    mock_copy.assert_called_once_with(test_case.submit_file_path, expected_dest)
